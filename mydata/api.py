"""FastAPI server for MyData"""

from pathlib import Path
from typing import Optional, List
from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
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


class SourceStats(BaseModel):
    emails: int = 0
    documents: int = 0
    notes: int = 0


class StatsResponse(BaseModel):
    total_documents: int
    total_chunks: int
    total_tags: int
    total_clusters: int
    sources: Optional[SourceStats] = None


# Create FastAPI app
app = FastAPI(title="MyData API", version="0.1.0")

# Add CORS middleware to allow requests from Tauri dev server
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173", "tauri://localhost"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
STATIC_DIR = Path(__file__).parent / "static"
if STATIC_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")


# Global state (initialized on startup or by daemon)
_db: Optional[Database] = None
_crypto: Optional[CryptoManager] = None
_storage: Optional[EncryptedStorage] = None
_embedder: Optional[Embedder] = None
_vectordb: Optional[VectorDB] = None
_pipeline: Optional[IngestionPipeline] = None
_hybrid_searcher = None
_anonymizer = None
_startup_event: Optional[threading.Event] = None


def init_services(crypto, db, storage, embedder, vectordb, pipeline, hybrid_searcher=None, anonymizer=None, startup_event=None):
    """Initialize services from daemon (skip startup event)"""
    global _db, _crypto, _storage, _embedder, _vectordb, _pipeline, _hybrid_searcher, _anonymizer, _startup_event
    _crypto = crypto
    _db = db
    _storage = storage
    _embedder = embedder
    _vectordb = vectordb
    _pipeline = pipeline
    _hybrid_searcher = hybrid_searcher
    _anonymizer = anonymizer
    _startup_event = startup_event


@app.on_event("startup")
async def startup():
    """Initialize services on startup (only if not already initialized by daemon)"""
    global _db, _crypto, _storage, _embedder, _vectordb, _pipeline

    if _pipeline is not None:
        # Already initialized by daemon
        if _startup_event:
            _startup_event.set()  # Signal that API is ready
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

    if _startup_event:
        _startup_event.set()  # Signal that API is ready


@app.get("/")
async def root():
    """Health check"""
    return {
        "service": "MyData",
        "status": "running",
        "crypto_unlocked": _crypto.is_unlocked if _crypto else False,
    }


@app.get("/status")
async def status_page():
    """Serve the status dashboard"""
    status_html = STATIC_DIR / "status.html"
    if status_html.exists():
        return FileResponse(status_html)
    raise HTTPException(status_code=404, detail="Status page not found")


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

    documents = session.exec(select(Document)).all()
    total_docs = len(documents)
    total_tags = len(session.exec(select(Tag)).all())
    total_clusters = len(session.exec(select(Cluster)).all())
    total_chunks = _vectordb.count() if _vectordb else 0

    # Count by source type
    emails = 0
    docs = 0
    notes = 0
    for doc in documents:
        source = doc.source.lower() if doc.source else ""
        if "email" in source or "@" in source or "outlook" in source or source.startswith("/o="):
            emails += 1
        elif source in ("api", "paste", "note", "text", "saved-chat", "saved-response") or source.startswith("note:"):
            notes += 1
        else:
            docs += 1

    stats = {
        "total_documents": total_docs,
        "total_chunks": total_chunks,
        "total_tags": total_tags,
        "total_clusters": total_clusters,
        "sources": {
            "emails": emails,
            "documents": docs,
            "notes": notes,
        }
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


@app.get("/dashboard/stats")
async def get_dashboard_stats():
    """Get comprehensive dashboard statistics"""
    if not _db:
        raise HTTPException(status_code=503, detail="Database not available")

    from sqlalchemy import func
    from datetime import datetime, timedelta

    session = _db.session()

    # Total documents
    total_docs = len(session.exec(select(Document)).all())

    # Documents by type
    docs_by_type = session.exec(
        select(Document.source_type, func.count(Document.id))
        .group_by(Document.source_type)
    ).all()

    # Recent documents (last 24 hours)
    yesterday = datetime.now() - timedelta(days=1)
    recent_docs = session.exec(
        select(Document)
        .where(Document.updated_at >= yesterday)
        .order_by(Document.updated_at.desc())
    ).all()

    # Latest document timestamp
    latest_doc = session.exec(
        select(Document)
        .order_by(Document.updated_at.desc())
    ).first()

    # Earliest document timestamp
    earliest_doc = session.exec(
        select(Document)
        .order_by(Document.created_at.asc())
    ).first()

    # Total chunks in vector DB
    total_chunks = _vectordb.count() if _vectordb else 0

    # Total tags
    total_tags = len(session.exec(select(Tag)).all())

    # Total clusters
    total_clusters = len(session.exec(select(Cluster)).all())

    # Documents ingested today
    today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    docs_today = len(session.exec(
        select(Document)
        .where(Document.created_at >= today_start)
    ).all())

    return {
        "total_documents": total_docs,
        "total_chunks": total_chunks,
        "total_tags": total_tags,
        "total_clusters": total_clusters,
        "docs_today": docs_today,
        "docs_last_24h": len(recent_docs),
        "latest_ingestion": latest_doc.updated_at.isoformat() if latest_doc else None,
        "earliest_ingestion": earliest_doc.created_at.isoformat() if earliest_doc else None,
        "docs_by_type": [{"type": t, "count": c} for t, c in docs_by_type],
        "recent_documents": [
            {
                "source": doc.source[:100],
                "type": doc.source_type,
                "updated_at": doc.updated_at.isoformat()
            }
            for doc in recent_docs[:10]
        ],
        "daemon_status": "running",
        "crypto_unlocked": _crypto.is_unlocked if _crypto else False,
    }


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


# Chat request/response models
class ChatRequest(BaseModel):
    message: str
    conversation_id: Optional[str] = None


class ChatResponse(BaseModel):
    response: str
    conversation_id: str
    sources: List[dict] = []


@app.post("/chat")
async def chat(request: ChatRequest):
    """Chat with your data using RAG"""
    if not _db or not _crypto or not _embedder or not _vectordb:
        raise HTTPException(status_code=503, detail="Service not available")

    from .chatbot import ChatBot

    session = _db.session()

    try:
        chatbot = ChatBot(
            session=session,
            crypto=_crypto,
            embedder=_embedder,
            vectordb=_vectordb,
            hybrid_searcher=_hybrid_searcher,
            anonymizer=_anonymizer,
        )

        result = chatbot.chat(
            message=request.message,
            conversation_id=request.conversation_id,
        )

        return ChatResponse(
            response=result["response"],
            conversation_id=str(result["conversation_id"]),
            sources=result.get("sources", []),
        )

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chat failed: {str(e)}")


# API Key management
class ApiKeyRequest(BaseModel):
    service: str
    api_key: str


class DatabaseInfoResponse(BaseModel):
    current_database: str
    database_path: str
    qdrant_path: str
    available_databases: List[str]


@app.get("/database/info")
async def get_database_info() -> DatabaseInfoResponse:
    """Get current database information and list available databases"""
    from .config import Config

    # Determine current database name by checking the path
    if _db is not None:
        db_path = str(_db.db_path) if hasattr(_db, 'db_path') else str(Config.DATABASE_PATH)
    else:
        db_path = str(Config.DATABASE_PATH)

    qdrant_path = str(_vectordb.path) if _vectordb and hasattr(_vectordb, 'path') else str(Config.QDRANT_PATH)

    # Determine current database name
    current_db = "default"
    if Config.MYDATA_HOME.name in db_path:
        # Extract the subdirectory name if it's a project-specific db
        db_path_obj = Path(db_path)
        if db_path_obj.parent.name != ".mydata" and db_path_obj.parent.parent.name == ".mydata":
            current_db = db_path_obj.parent.name

    return DatabaseInfoResponse(
        current_database=current_db,
        database_path=db_path,
        qdrant_path=qdrant_path,
        available_databases=Config.list_databases()
    )


class ApiStatusResponse(BaseModel):
    openai: bool = False
    anthropic: bool = False


@app.get("/api-keys/status")
async def get_api_keys_status() -> ApiStatusResponse:
    """Check which API keys are configured"""
    if not _db:
        raise HTTPException(status_code=503, detail="Database not available")

    from .models import ApiKey

    session = _db.session()

    # Check for OpenAI key
    openai_key = session.exec(
        select(ApiKey).where(ApiKey.service == "openai", ApiKey.enabled == True)
    ).first()

    # Check for Anthropic key
    anthropic_key = session.exec(
        select(ApiKey).where(ApiKey.service == "anthropic", ApiKey.enabled == True)
    ).first()

    return ApiStatusResponse(
        openai=openai_key is not None,
        anthropic=anthropic_key is not None
    )


@app.post("/api-key")
async def add_api_key(request: ApiKeyRequest):
    """Add or update an API key"""
    if not _db or not _crypto:
        raise HTTPException(status_code=503, detail="Service not available")

    from .models import ApiKey

    session = _db.session()

    # Check if key already exists
    existing = session.exec(
        select(ApiKey).where(ApiKey.service == request.service)
    ).first()

    encrypted_key = _crypto.encrypt_str(request.api_key)

    if existing:
        existing.encrypted_key = encrypted_key
        existing.enabled = True
        session.add(existing)
    else:
        api_key = ApiKey(
            service=request.service,
            encrypted_key=encrypted_key,
            enabled=True,
        )
        session.add(api_key)

    session.commit()

    return {"success": True, "message": f"API key for {request.service} saved"}


@app.get("/admin/info")
async def get_admin_info():
    """Get comprehensive system information for administrators"""
    import platform
    import sys
    import os
    from datetime import datetime

    from .config import Config

    info = {
        "system": {
            "platform": platform.system(),
            "platform_release": platform.release(),
            "python_version": sys.version,
            "architecture": platform.machine(),
        },
        "paths": {
            "mydata_home": str(Config.MYDATA_HOME),
            "database_path": str(Config.DATABASE_PATH),
            "qdrant_path": str(Config.QDRANT_PATH),
            "models_cache": str(Config.MODELS_CACHE_DIR),
            "log_dir": str(Config.LOG_DIR),
        },
        "config": {
            "api_host": Config.API_HOST,
            "api_port": Config.API_PORT,
            "embedding_model": Config.EMBEDDING_MODEL,
            "chunk_size": Config.CHUNK_SIZE,
            "chunk_overlap": Config.CHUNK_OVERLAP,
            "cache_ttl_seconds": Config.CACHE_TTL_SECONDS,
            "cache_max_size": Config.CACHE_MAX_SIZE,
            "semantic_threshold": Config.SEMANTIC_SIMILARITY_THRESHOLD,
            "hybrid_vector_weight": Config.HYBRID_SEARCH_VECTOR_WEIGHT,
            "hybrid_bm25_weight": Config.HYBRID_SEARCH_BM25_WEIGHT,
        },
        "status": {
            "database_connected": _db is not None,
            "crypto_unlocked": _crypto is not None and _crypto.is_unlocked,
            "embedder_ready": _embedder is not None,
            "vectordb_ready": _vectordb is not None,
            "pipeline_ready": _pipeline is not None,
            "chatbot_ready": _chatbot is not None,
        },
        "database": {},
        "vectordb": {},
        "timestamp": datetime.now().isoformat(),
    }

    # Database info
    if _db:
        try:
            session = _db.session()
            doc_count = len(session.exec(select(Document)).all())
            tag_count = len(session.exec(select(Tag)).all())
            cluster_count = len(session.exec(select(Cluster)).all())

            # Get database file size
            db_path = Config.DATABASE_PATH
            db_size = db_path.stat().st_size if db_path.exists() else 0

            info["database"] = {
                "documents": doc_count,
                "tags": tag_count,
                "clusters": cluster_count,
                "file_size_mb": round(db_size / (1024 * 1024), 2),
            }
        except Exception as e:
            info["database"]["error"] = str(e)

    # Vector DB info
    if _vectordb:
        try:
            vector_count = _vectordb.count()

            # Get qdrant folder size
            qdrant_path = Config.QDRANT_PATH
            qdrant_size = 0
            if qdrant_path.exists():
                for f in qdrant_path.rglob("*"):
                    if f.is_file():
                        qdrant_size += f.stat().st_size

            info["vectordb"] = {
                "vectors": vector_count,
                "dimension": _embedder.dimension if _embedder else 0,
                "folder_size_mb": round(qdrant_size / (1024 * 1024), 2),
            }
        except Exception as e:
            info["vectordb"]["error"] = str(e)

    # Embedder info
    if _embedder:
        info["embedder"] = {
            "model": Config.EMBEDDING_MODEL,
            "dimension": _embedder.dimension,
        }

    # Available databases
    info["available_databases"] = Config.list_databases()

    return info
