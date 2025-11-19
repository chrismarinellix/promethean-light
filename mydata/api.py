"""FastAPI server for MyData"""

from pathlib import Path
from typing import Optional, List
from fastapi import FastAPI, HTTPException, UploadFile, File
from pydantic import BaseModel
from .database import Database
from .crypto import CryptoManager
from .storage import EncryptedStorage
from .embedder import Embedder
from .vectordb import VectorDB
from .ml_organizer import MLOrganizer
from .ingestion import IngestionPipeline
from .cache import get_cache, cached
from sqlmodel import select
from .models import Document, Tag, Cluster
import threading


# Request/Response models
class AddTextRequest(BaseModel):
    text: str
    source: str = "api"


class SearchRequest(BaseModel):
    query: str
    limit: int = 10
    tag: Optional[str] = None


class SearchResult(BaseModel):
    id: str
    score: float
    text: str
    source: str
    created_at: str


class StatsResponse(BaseModel):
    total_documents: int
    total_chunks: int
    total_tags: int
    total_clusters: int


# Create FastAPI app
app = FastAPI(title="MyData API", version="0.1.0")


# Global state (initialized on startup or by daemon)
_db: Optional[Database] = None
_crypto: Optional[CryptoManager] = None
_storage: Optional[EncryptedStorage] = None
_embedder: Optional[Embedder] = None
_vectordb: Optional[VectorDB] = None
_pipeline: Optional[IngestionPipeline] = None


def init_services(crypto, db, storage, embedder, vectordb, pipeline, api_startup_event: threading.Event):
    """Initialize services from daemon (skip startup event)"""
    global _db, _crypto, _storage, _embedder, _vectordb, _pipeline
    _crypto = crypto
    _db = db
    _storage = storage
    _embedder = embedder
    _vectordb = vectordb
    _pipeline = pipeline
    api_startup_event.set() # Signal that API services are initialized and ready


@app.on_event("startup")
async def startup():
    """Initialize services on startup (only if not already initialized by daemon)"""
    global _db, _crypto, _storage, _embedder, _vectordb, _pipeline

    if _pipeline is not None:
        # Already initialized by daemon
        return

    print("🚀 Starting MyData API...")

    # Initialize components
    _crypto = CryptoManager()

    # Try to unlock (will fail if not set up or no env var)
    try:
        _crypto.unlock()
        print("✓ Crypto unlocked")
    except Exception as e:
        print(f"⚠ Crypto not unlocked: {e}")

    _db = Database()
    _storage = EncryptedStorage(_crypto) if _crypto.is_unlocked else None
    _embedder = Embedder()
    _vectordb = VectorDB()
    _vectordb.initialize(dimension=_embedder.dimension)

    if _crypto.is_unlocked and _storage:
        session = _db.session()
        ml_organizer = MLOrganizer(_embedder, session)
        _pipeline = IngestionPipeline(session, _storage, _embedder, _vectordb, ml_organizer)
        print("✓ Ingestion pipeline ready")
    else:
        print("⚠ Ingestion pipeline not available (crypto locked)")

    print("✓ MyData API started")


@app.get("/")
async def root():
    """Health check"""
    return {
        "service": "MyData",
        "status": "running",
        "crypto_unlocked": _crypto.is_unlocked if _crypto else False,
    }


@app.post("/add")
async def add_text(request: AddTextRequest):
    """Add text document"""
    if not _pipeline:
        raise HTTPException(status_code=503, detail="Ingestion pipeline not available")

    doc_id = _pipeline.ingest_text(request.text, source=request.source)

    if doc_id is None:
        raise HTTPException(status_code=500, detail="Failed to ingest text")

    return {"id": str(doc_id), "status": "success"}


@app.post("/add/file")
async def add_file(file: UploadFile = File(...)):
    """Add file document"""
    if not _pipeline:
        raise HTTPException(status_code=503, detail="Ingestion pipeline not available")

    # Save temporarily
    temp_path = Path(f"/tmp/{file.filename}")
    content = await file.read()
    temp_path.write_bytes(content)

    try:
        doc_id = _pipeline.ingest_file(temp_path)
        if doc_id is None:
            raise HTTPException(status_code=500, detail="Failed to ingest file")
        return {"id": str(doc_id), "status": "success"}
    finally:
        temp_path.unlink(missing_ok=True)


@app.post("/search")
async def search(request: SearchRequest) -> List[SearchResult]:
    """Semantic search with caching"""
    if not _embedder or not _vectordb:
        raise HTTPException(status_code=503, detail="Search not available")

    # Check cache first
    cache = get_cache()
    cache_key = f"search:{request.query}:{request.limit}:{request.tag}"
    cached_result = cache.get(cache_key)

    if cached_result is not None:
        return cached_result

    # Embed query
    query_vector = _embedder.embed(request.query)

    # Search
    filter_dict = {"tag": request.tag} if request.tag else None
    results = _vectordb.search(
        query_vector=query_vector,
        limit=request.limit,
        filter_dict=filter_dict,
    )

    # Format results
    search_results = []
    for hit in results:
        search_results.append(
            SearchResult(
                id=hit["id"],
                score=hit["score"],
                text=hit["payload"].get("text", ""),
                source=hit["payload"].get("source", ""),
                created_at="",  # TODO: add from payload
            )
        )

    # Cache for 5 minutes
    cache.set(cache_key, search_results)

    return search_results


@app.get("/documents/{doc_id}")
async def get_document(doc_id: str):
    """Get document by ID"""
    if not _db:
        raise HTTPException(status_code=503, detail="Database not available")

    session = _db.session()
    doc = session.get(Document, doc_id)

    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    return {
        "id": str(doc.id),
        "source": doc.source,
        "text": doc.raw_text[:500] + "..." if len(doc.raw_text) > 500 else doc.raw_text,
        "created_at": doc.created_at.isoformat(),
    }


@app.get("/stats")
async def get_stats() -> StatsResponse:
    """Get database statistics (cached)"""
    if not _db:
        raise HTTPException(status_code=503, detail="Database not available")

    # Check cache
    cache = get_cache()
    cached_stats = cache.get("stats")
    if cached_stats:
        return StatsResponse(**cached_stats)

    session = _db.session()

    total_docs = len(session.exec(select(Document)).all())
    total_tags = len(session.exec(select(Tag)).all())
    total_clusters = len(session.exec(select(Cluster)).all())
    total_chunks = _vectordb.count() if _vectordb else 0

    stats = {
        "total_documents": total_docs,
        "total_chunks": total_chunks,
        "total_tags": total_tags,
        "total_clusters": total_clusters,
    }

    # Cache for 5 minutes
    cache.set("stats", stats)

    return StatsResponse(**stats)


@app.get("/summary/{summary_name}")
async def get_summary_endpoint(summary_name: str):
    """Get pre-computed summary (instant, 0 token cost)"""
    from .summaries import get_summary

    summary = get_summary(summary_name)
    if summary is None:
        raise HTTPException(status_code=404, detail=f"Summary '{summary_name}' not found")

    return summary


@app.get("/tags")
async def get_tags() -> List[dict]:
    """Get all tags"""
    if not _db:
        raise HTTPException(status_code=503, detail="Database not available")

    session = _db.session()
    tags = session.exec(select(Tag)).all()

    # Count by tag
    from collections import Counter

    tag_counts = Counter([t.tag for t in tags])

    return [{"tag": tag, "count": count} for tag, count in tag_counts.most_common()]


class AddEmailRequest(BaseModel):
    email_address: str
    password: str
    imap_server: str = "imap.gmail.com"
    imap_port: int = 993


@app.post("/email/add")
async def add_email(request: AddEmailRequest):
    """Add email account for watching"""
    if not _db or not _crypto:
        raise HTTPException(status_code=503, detail="Service not available")

    from .models import EmailCredential

    session = _db.session()

    # Encrypt password
    encrypted_password = _crypto.encrypt_str(request.password)

    # Save credential
    cred = EmailCredential(
        email_address=request.email_address,
        encrypted_password=encrypted_password,
        imap_server=request.imap_server,
        imap_port=request.imap_port,
    )

    session.add(cred)
    session.commit()

    return {
        "success": True,
        "message": f"Email account added: {request.email_address}. Restart daemon to activate."
    }
