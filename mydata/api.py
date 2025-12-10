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


class CheckDuplicateRequest(BaseModel):
    content: str
    threshold: float = 0.92


class CheckDuplicateResponse(BaseModel):
    is_duplicate: bool
    confidence: float
    matches: List[dict] = []


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
    last_email_at: Optional[str] = None  # ISO timestamp of most recent email


# Create FastAPI app
app = FastAPI(title="MyData API", version="0.1.0")

# Add CORS middleware to allow requests from Tauri dev server
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for local development
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
_chatbot = None
_startup_event: Optional[threading.Event] = None

# Rebuild state for background task tracking
_rebuild_state = {
    "status": "idle",  # idle, running, complete, error
    "progress": 0,
    "total_chunks": 0,
    "indexed": 0,
    "skipped": 0,
    "errors": 0,
    "error_messages": [],
    "start_time": None,
    "elapsed_seconds": 0,
    "rate_per_second": 0,
    "message": ""
}


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

    print("Starting MyData API...")

    # Initialize components
    _crypto = CryptoManager()

    # Try to unlock (will fail if not set up or no env var)
    try:
        _crypto.unlock()
        print("[OK] Crypto unlocked")
    except Exception as e:
        print(f"[WARN] Crypto not unlocked: {e}")

    _db = Database()
    _storage = EncryptedStorage(_crypto) if _crypto.is_unlocked else None
    _embedder = Embedder()
    _vectordb = VectorDB()
    _vectordb.initialize(dimension=_embedder.dimension)

    if _crypto.is_unlocked and _storage:
        session = _db.session()
        ml_organizer = MLOrganizer(_embedder, session)
        _pipeline = IngestionPipeline(session, _storage, _embedder, _vectordb, ml_organizer)
        print("[OK] Ingestion pipeline ready")
    else:
        print("[WARN] Ingestion pipeline not available (crypto locked)")

    print("[OK] MyData API started")

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
async def add_file(file: UploadFile = File(...), force: bool = False):
    """Add file document with optional duplicate override"""
    if not _pipeline:
        raise HTTPException(status_code=503, detail="Ingestion pipeline not available")

    # Use temp directory that works on Windows
    import tempfile
    temp_dir = Path(tempfile.gettempdir())
    temp_path = temp_dir / file.filename
    content = await file.read()
    temp_path.write_bytes(content)

    try:
        doc_id = _pipeline.ingest_file(temp_path)
        if doc_id is None:
            raise HTTPException(status_code=500, detail="Failed to ingest file (may be duplicate)")

        # Get chunk count for the response
        from .models import Chunk
        session = _db.session()
        chunks = session.exec(select(Chunk).where(Chunk.doc_id == doc_id)).all()

        return {
            "id": str(doc_id),
            "status": "success",
            "filename": file.filename,
            "chunks_created": len(chunks),
            "size_bytes": len(content)
        }
    finally:
        temp_path.unlink(missing_ok=True)


@app.post("/check-duplicate")
async def check_duplicate(request: CheckDuplicateRequest) -> CheckDuplicateResponse:
    """Check if content already exists in the database before ingesting"""
    if not _embedder or not _vectordb:
        raise HTTPException(status_code=503, detail="Search not available")

    # Take sample of content (first 500 chars for speed)
    sample = request.content[:500] if len(request.content) > 500 else request.content

    if len(sample.strip()) < 20:
        return CheckDuplicateResponse(is_duplicate=False, confidence=0, matches=[])

    try:
        # Embed the sample
        query_vector = _embedder.embed(sample)

        # Search for similar content
        results = _vectordb.search(
            query_vector=query_vector,
            limit=3,
        )

        # Check for high-similarity matches
        matches = []
        max_score = 0

        for hit in results:
            score = hit.get("score", 0)
            if score >= request.threshold:
                matches.append({
                    "id": hit.get("id", ""),
                    "score": round(score, 4),
                    "text": hit.get("payload", {}).get("text", "")[:200] + "...",
                    "source": hit.get("payload", {}).get("source", "unknown"),
                })
            if score > max_score:
                max_score = score

        is_duplicate = len(matches) > 0

        return CheckDuplicateResponse(
            is_duplicate=is_duplicate,
            confidence=round(max_score, 4),
            matches=matches
        )

    except Exception as e:
        # If check fails, return not duplicate (fail open)
        return CheckDuplicateResponse(is_duplicate=False, confidence=0, matches=[])


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

    # Count by source type and track most recent email
    emails = 0
    docs = 0
    notes = 0
    last_email_at = None

    for doc in documents:
        source = doc.source.lower() if doc.source else ""
        if "email" in source or "@" in source or "outlook" in source or source.startswith("/o="):
            emails += 1
            # Track most recent email
            if doc.created_at:
                if last_email_at is None or doc.created_at > last_email_at:
                    last_email_at = doc.created_at
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
        },
        "last_email_at": last_email_at.isoformat() if last_email_at else None,
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


@app.get("/clusters")
async def get_clusters() -> List[dict]:
    """Get all clusters with their labels and document counts"""
    if not _db:
        raise HTTPException(status_code=503, detail="Database not available")

    session = _db.session()
    clusters = session.exec(select(Cluster).order_by(Cluster.document_count.desc())).all()

    return [
        {
            "id": c.id,
            "label": c.label,
            "description": c.description,
            "document_count": c.document_count,
            "created_at": c.created_at.isoformat() if c.created_at else None
        }
        for c in clusters
    ]


@app.get("/clusters/{cluster_id}/documents")
async def get_cluster_documents(cluster_id: int, limit: int = 20) -> List[dict]:
    """Get documents in a specific cluster"""
    if not _db:
        raise HTTPException(status_code=503, detail="Database not available")

    session = _db.session()
    docs = session.exec(
        select(Document)
        .where(Document.cluster_id == cluster_id)
        .order_by(Document.updated_at.desc())
        .limit(limit)
    ).all()

    return [
        {
            "id": str(d.id),
            "source": d.source,
            "source_type": d.source_type,
            "preview": d.raw_text[:200] if d.raw_text else "",
            "created_at": d.created_at.isoformat() if d.created_at else None
        }
        for d in docs
    ]


@app.post("/clusters/rebuild")
async def rebuild_clusters(min_cluster_size: int = 10, min_samples: int = 5):
    """Manually trigger cluster rebuild"""
    if not _db or not _embedder:
        raise HTTPException(status_code=503, detail="Database or embedder not available")

    from .ml_organizer import MLOrganizer
    import traceback

    try:
        session = _db.session()
        organizer = MLOrganizer(_embedder, session)

        # Force has_changes to trigger clustering
        organizer._last_doc_count = -1

        result = organizer.run_clustering(min_cluster_size=min_cluster_size, min_samples=min_samples)

        return {
            "status": result.get("status", "unknown"),
            "clusters": result.get("clusters", 0),
            "message": f"Created {result.get('clusters', 0)} clusters from {result.get('doc_count', 0)} documents"
        }
    except Exception as e:
        print(f"[API] Cluster rebuild failed: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Clustering failed: {str(e)}")


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


# War Room intelligence view
class WarRoomRequest(BaseModel):
    query: str
    context: Optional[str] = None


class WarRoomResponse(BaseModel):
    status: str = "Active"
    lastUpdate: str
    timeline: List[dict] = []
    people: List[dict] = []
    topics: dict = {}
    actions: List[dict] = []
    issues: List[dict] = []
    documents: List[dict] = []
    stats: dict = {}


@app.post("/warroom")
async def get_warroom_data(request: WarRoomRequest) -> WarRoomResponse:
    """Get War Room intelligence view for a topic"""
    import re
    from datetime import datetime

    if not _db or not _embedder or not _vectordb:
        raise HTTPException(status_code=503, detail="Service not available")

    # Search for related documents
    query_vector = _embedder.embed(request.query)
    results = _vectordb.search(query_vector=query_vector, limit=50)

    # Aggregate all text for analysis
    all_text = request.context or ""
    sources = []

    for hit in results:
        payload = hit.get("payload", {})
        text = payload.get("text", "")
        source = payload.get("source", "")
        all_text += f"\n{text}"
        sources.append({
            "source": source,
            "text": text[:200],
            "score": hit.get("score", 0)
        })

    # Extract timeline events
    timeline = []
    date_patterns = [
        (r'(\d{4}-\d{2}-\d{2})[:\s-]+(.+?)(?=\n|$)', lambda m: m.group(1)),
        (r'((?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\w*\s+\d{1,2},?\s*\d{4})[:\s-]*(.+?)(?=\n|$)', lambda m: m.group(1)),
    ]
    seen_events = set()
    for pattern, date_extractor in date_patterns:
        for match in re.finditer(pattern, all_text, re.IGNORECASE):
            event = match.group(2).strip()[:100] if len(match.groups()) > 1 else ""
            if event and event not in seen_events:
                seen_events.add(event)
                timeline.append({
                    "date": date_extractor(match),
                    "event": event
                })
    timeline = timeline[:15]  # Limit

    # Extract people
    people = []
    seen_people = set()
    email_pattern = r'([A-Za-z][A-Za-z\s\.]+)\s*[<(]([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})[>)]'
    for match in re.finditer(email_pattern, all_text):
        name = match.group(1).strip()
        email = match.group(2)
        if name.lower() not in seen_people and len(name) > 2:
            seen_people.add(name.lower())
            domain = email.split('@')[1].split('.')[0] if '@' in email else ''
            people.append({
                "name": name,
                "email": email,
                "role": "",
                "org": domain.capitalize()
            })
    people = people[:20]

    # Extract topics
    topics = {"technical": [], "commercial": [], "process": []}
    tech_kw = ['technical', 'engineering', 'system', 'design', 'analysis', 'model', 'data', 'powerlink', 'grid']
    comm_kw = ['contract', 'price', 'cost', 'budget', 'fee', 'insurance', 'commercial', 'payment', 'invoice']
    proc_kw = ['approval', 'review', 'meeting', 'deadline', 'timeline', 'schedule', 'milestone']

    for line in all_text.split('\n'):
        line_clean = line.strip()
        if len(line_clean) > 20:
            lower = line_clean.lower()
            if any(k in lower for k in tech_kw) and len(topics["technical"]) < 5:
                topics["technical"].append(line_clean[:100])
            if any(k in lower for k in comm_kw) and len(topics["commercial"]) < 5:
                topics["commercial"].append(line_clean[:100])
            if any(k in lower for k in proc_kw) and len(topics["process"]) < 5:
                topics["process"].append(line_clean[:100])

    # Extract actions
    actions = []
    action_patterns = [
        r'(?:TODO|ACTION|TASK)[:\s]+(.+?)(?=\n|$)',
        r'(?:CRITICAL|URGENT|PENDING)[:\s]+(.+?)(?=\n|$)',
    ]
    for pattern in action_patterns:
        for match in re.finditer(pattern, all_text, re.IGNORECASE):
            action_text = match.group(1).strip()
            if 10 < len(action_text) < 200:
                status = "critical" if "critical" in match.group(0).lower() else "pending"
                actions.append({
                    "status": status,
                    "description": action_text,
                    "owner": "",
                    "due": ""
                })
    actions = actions[:15]

    # Extract issues
    issues = []
    issue_patterns = [
        r'(?:issue|problem|risk|blocker|concern)[:\s]+(.+?)(?=\n|$)',
        r'(?:BLOCKED|WARNING)[:\s]+(.+?)(?=\n|$)',
    ]
    for pattern in issue_patterns:
        for match in re.finditer(pattern, all_text, re.IGNORECASE):
            issue_text = match.group(1).strip()
            if len(issue_text) > 10:
                severity = "high" if "block" in match.group(0).lower() else "medium"
                issues.append({
                    "severity": severity,
                    "description": issue_text[:150],
                    "status": "open"
                })
    issues = issues[:10]

    # Format documents
    documents = []
    for src in sources[:20]:
        source_str = src.get("source", "")
        doc_type = "email" if ("@" in source_str or "email" in source_str.lower()) else "file"
        if ".pdf" in source_str.lower():
            doc_type = "pdf"
        documents.append({
            "type": doc_type,
            "title": source_str.split("/")[-1].split("\\")[-1][:50] if source_str else "Unknown",
            "date": "",
            "summary": src.get("text", "")[:100]
        })

    # Stats
    stats = {
        "documents": len(documents),
        "emails": len([d for d in documents if d["type"] == "email"]),
        "people": len(people),
        "actions": len(actions)
    }

    return WarRoomResponse(
        status="Active" if len(results) > 0 else "No Data",
        lastUpdate=datetime.now().strftime("%Y-%m-%d"),
        timeline=timeline,
        people=people,
        topics=topics,
        actions=actions,
        issues=issues,
        documents=documents,
        stats=stats
    )


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
            # Chatbot is ready if we have the components to create one on-demand
            "chatbot_ready": (_db is not None and _crypto is not None and
                             _crypto.is_unlocked and _embedder is not None and _vectordb is not None),
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


def _run_rebuild_background():
    """Background worker function for rebuild - runs in a separate thread"""
    import time
    from .models import Chunk, Document

    global _rebuild_state

    try:
        _rebuild_state["status"] = "running"
        _rebuild_state["start_time"] = time.time()
        _rebuild_state["indexed"] = 0
        _rebuild_state["skipped"] = 0
        _rebuild_state["errors"] = 0
        _rebuild_state["error_messages"] = []
        _rebuild_state["message"] = "Starting rebuild..."

        session = _db.session()
        chunks = session.exec(select(Chunk)).all()
        total_chunks = len(chunks)
        _rebuild_state["total_chunks"] = total_chunks

        if total_chunks == 0:
            _rebuild_state["status"] = "complete"
            _rebuild_state["message"] = "No chunks to index"
            return

        for i, chunk in enumerate(chunks):
            try:
                text = chunk.text if hasattr(chunk, 'text') else chunk.content

                if not text or len(text.strip()) < 10:
                    _rebuild_state["skipped"] += 1
                    continue

                # Get document source for metadata
                doc = session.get(Document, chunk.doc_id)
                source = doc.source if doc else "unknown"

                # Embed the text
                embedding = _embedder.embed(text)

                # Upsert to vector DB
                _vectordb.upsert(
                    doc_id=str(chunk.id),
                    vector=embedding,
                    payload={
                        "text": text[:2000],
                        "source": source,
                        "doc_id": str(chunk.doc_id),
                        "start_offset": chunk.start_offset,
                        "end_offset": chunk.end_offset,
                    }
                )
                _rebuild_state["indexed"] += 1

            except Exception as e:
                _rebuild_state["errors"] += 1
                if _rebuild_state["errors"] <= 10:
                    _rebuild_state["error_messages"].append(f"Chunk {chunk.id}: {str(e)}")

            # Update progress
            _rebuild_state["progress"] = round((i + 1) / total_chunks * 100, 1)
            elapsed = time.time() - _rebuild_state["start_time"]
            _rebuild_state["elapsed_seconds"] = round(elapsed, 1)
            if elapsed > 0:
                _rebuild_state["rate_per_second"] = round(_rebuild_state["indexed"] / elapsed, 2)
            _rebuild_state["message"] = f"Processing chunk {i + 1}/{total_chunks}..."

        # Complete
        _rebuild_state["status"] = "complete"
        _rebuild_state["progress"] = 100
        _rebuild_state["message"] = f"Rebuild complete: {_rebuild_state['indexed']} indexed, {_rebuild_state['errors']} errors"

    except Exception as e:
        _rebuild_state["status"] = "error"
        _rebuild_state["message"] = f"Rebuild failed: {str(e)}"


@app.post("/admin/rebuild-vectors")
async def rebuild_vectors():
    """
    Start rebuilding the vector database in the background.
    Returns immediately and tracks progress via /admin/rebuild-vectors/status
    """
    global _rebuild_state

    if not _db:
        raise HTTPException(status_code=500, detail="Database not initialized")
    if not _embedder:
        raise HTTPException(status_code=500, detail="Embedder not initialized")
    if not _vectordb:
        raise HTTPException(status_code=500, detail="Vector DB not initialized")

    # Check if already running
    if _rebuild_state["status"] == "running":
        return {
            "success": False,
            "message": "Rebuild already in progress",
            "status": _rebuild_state["status"],
            "progress": _rebuild_state["progress"]
        }

    # Reset state
    _rebuild_state = {
        "status": "running",
        "progress": 0,
        "total_chunks": 0,
        "indexed": 0,
        "skipped": 0,
        "errors": 0,
        "error_messages": [],
        "start_time": None,
        "elapsed_seconds": 0,
        "rate_per_second": 0,
        "message": "Starting..."
    }

    # Start background thread
    rebuild_thread = threading.Thread(target=_run_rebuild_background, daemon=True)
    rebuild_thread.start()

    return {
        "success": True,
        "message": "Rebuild started in background",
        "status": "running"
    }


@app.get("/admin/rebuild-vectors/status")
async def rebuild_vectors_status():
    """Get current rebuild status including live progress during rebuild"""
    global _rebuild_state

    if not _db:
        raise HTTPException(status_code=500, detail="Database not initialized")
    if not _vectordb:
        raise HTTPException(status_code=500, detail="Vector DB not initialized")

    # Get current vector count
    vector_count = _vectordb.count()

    # If rebuild is running, return live progress
    if _rebuild_state["status"] == "running":
        return {
            "status": _rebuild_state["status"],
            "progress": _rebuild_state["progress"],
            "total_chunks": _rebuild_state["total_chunks"],
            "indexed": _rebuild_state["indexed"],
            "skipped": _rebuild_state["skipped"],
            "errors": _rebuild_state["errors"],
            "error_messages": _rebuild_state["error_messages"],
            "elapsed_seconds": _rebuild_state["elapsed_seconds"],
            "rate_per_second": _rebuild_state["rate_per_second"],
            "message": _rebuild_state["message"],
            "vector_count": vector_count
        }

    # If rebuild is complete or errored, return final state
    if _rebuild_state["status"] in ["complete", "error"]:
        return {
            "status": _rebuild_state["status"],
            "progress": _rebuild_state["progress"],
            "total_chunks": _rebuild_state["total_chunks"],
            "indexed": _rebuild_state["indexed"],
            "skipped": _rebuild_state["skipped"],
            "errors": _rebuild_state["errors"],
            "error_messages": _rebuild_state["error_messages"],
            "elapsed_seconds": _rebuild_state["elapsed_seconds"],
            "rate_per_second": _rebuild_state["rate_per_second"],
            "message": _rebuild_state["message"],
            "vector_count": vector_count
        }

    # Idle state - return basic sync info
    from .models import Chunk
    session = _db.session()
    total_chunks = len(session.exec(select(Chunk)).all())

    return {
        "status": "idle",
        "total_chunks": total_chunks,
        "vector_count": vector_count,
        "sync_percentage": round((vector_count / total_chunks * 100), 1) if total_chunks > 0 else 0,
        "in_sync": vector_count >= total_chunks * 0.95  # Consider in sync if >= 95%
    }


# Saved Searches API
class SavedSearchRequest(BaseModel):
    folder: str = "general"
    query: str
    response: str
    sources: Optional[str] = None


class SavedSearchResponse(BaseModel):
    id: int
    folder: str
    query: str
    response: str
    sources: Optional[str] = None
    created_at: str
    updated_at: str


@app.get("/saved-searches")
async def get_saved_searches(folder: Optional[str] = None) -> List[SavedSearchResponse]:
    """Get all saved searches, optionally filtered by folder"""
    if not _db:
        raise HTTPException(status_code=503, detail="Database not available")

    from .models import SavedSearch

    session = _db.session()

    if folder:
        searches = session.exec(
            select(SavedSearch)
            .where(SavedSearch.folder == folder)
            .order_by(SavedSearch.created_at.desc())
        ).all()
    else:
        searches = session.exec(
            select(SavedSearch)
            .order_by(SavedSearch.created_at.desc())
        ).all()

    return [
        SavedSearchResponse(
            id=s.id,
            folder=s.folder,
            query=s.query,
            response=s.response,
            sources=s.sources,
            created_at=s.created_at.isoformat(),
            updated_at=s.updated_at.isoformat()
        )
        for s in searches
    ]


@app.get("/saved-searches/folders")
async def get_saved_search_folders() -> List[dict]:
    """Get list of folders with saved search counts"""
    if not _db:
        raise HTTPException(status_code=503, detail="Database not available")

    from .models import SavedSearch
    from sqlalchemy import func

    session = _db.session()

    # Count searches by folder
    folder_counts = session.exec(
        select(SavedSearch.folder, func.count(SavedSearch.id))
        .group_by(SavedSearch.folder)
    ).all()

    return [{"folder": f, "count": c} for f, c in folder_counts]


@app.post("/saved-searches")
async def create_saved_search(request: SavedSearchRequest) -> SavedSearchResponse:
    """Save a search query and response"""
    if not _db:
        raise HTTPException(status_code=503, detail="Database not available")

    from .models import SavedSearch
    from datetime import datetime

    session = _db.session()

    saved = SavedSearch(
        folder=request.folder,
        query=request.query,
        response=request.response,
        sources=request.sources,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )

    session.add(saved)
    session.commit()
    session.refresh(saved)

    return SavedSearchResponse(
        id=saved.id,
        folder=saved.folder,
        query=saved.query,
        response=saved.response,
        sources=saved.sources,
        created_at=saved.created_at.isoformat(),
        updated_at=saved.updated_at.isoformat()
    )


@app.delete("/saved-searches/{search_id}")
async def delete_saved_search(search_id: int):
    """Delete a saved search"""
    if not _db:
        raise HTTPException(status_code=503, detail="Database not available")

    from .models import SavedSearch

    session = _db.session()

    saved = session.get(SavedSearch, search_id)
    if not saved:
        raise HTTPException(status_code=404, detail="Saved search not found")

    session.delete(saved)
    session.commit()

    return {"success": True, "message": "Saved search deleted"}


@app.post("/admin/refresh-summaries")
async def refresh_summaries():
    """
    Refresh pre-computed summaries.
    Note: Summaries are defined in code (summaries.py) and reflect static data.
    This endpoint validates that summaries are accessible and returns their status.
    To update actual values, edit mydata/summaries.py.
    """
    from .summaries import SUMMARIES, get_summary

    try:
        # Validate all summaries are accessible
        summary_status = {}
        for name in SUMMARIES.keys():
            summary = get_summary(name)
            if summary:
                summary_status[name] = "ok"
            else:
                summary_status[name] = "error"

        return {
            "success": True,
            "message": f"Pre-computed summaries validated ({len(summary_status)} available)",
            "summaries": list(summary_status.keys()),
            "status": summary_status
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to refresh summaries: {str(e)}")
