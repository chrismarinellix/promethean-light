# Promethean Light RAG System Skills

## Overview

Promethean Light is a local-first, encrypted RAG (Retrieval-Augmented Generation) system with:
- **Backend**: Python (FastAPI) with SQLite + Qdrant vector store
- **Frontend**: Svelte 4 + SvelteKit 2 + Tauri 2 desktop app
- **Location**: `C:\Code\Promethian  Light`

## Architecture Quick Reference

### Key Directories

```
mydata/                     # Python backend (RAG engine)
├── api.py                  # FastAPI server (port 8000)
├── embedder.py             # Sentence-transformers (BAAI/bge-large-en-v1.5)
├── vectordb.py             # Qdrant vector database wrapper
├── ingestion.py            # Document ingestion pipeline
├── hybrid_search.py        # Vector + BM25 hybrid ranking
├── chatbot.py              # OpenAI RAG integration
├── models.py               # SQLModel schemas (Document, Chunk, Tag, etc.)
├── database.py             # SQLite connection management
├── config.py               # Centralized configuration
├── daemon.py               # Background service orchestrator
└── crypto.py               # Fernet encryption + Argon2id

promethean-light-ui/        # Svelte/Tauri frontend
├── src/lib/
│   ├── api.js              # Backend API client (Tauri IPC + HTTP)
│   ├── stores.js           # Svelte writable stores
│   └── components/
│       ├── ChatPanel.svelte
│       ├── AdminPanel.svelte
│       ├── Sidebar.svelte
│       ├── SearchBar.svelte
│       └── SearchResults.svelte
├── src/routes/
│   ├── +layout.svelte      # Root layout (daemon startup)
│   └── +page.svelte        # Main app page
└── src-tauri/              # Tauri native bridge
```

### Data Storage Locations

- **SQLite DB**: `~/.mydata/mydata.db`
- **Qdrant vectors**: `~/.mydata/qdrant/`
- **Embedding models**: `~/.mydata/models/`

## Backend Development

### Adding a New API Endpoint

Location: `mydata/api.py`

```python
from fastapi import APIRouter, HTTPException
from mydata.database import get_session
from mydata.models import Document

@router.get("/documents/{doc_id}")
async def get_document(doc_id: int):
    with get_session() as session:
        doc = session.get(Document, doc_id)
        if not doc:
            raise HTTPException(status_code=404, detail="Document not found")
        return doc
```

### Adding a New Database Model

Location: `mydata/models.py`

```python
from sqlmodel import SQLModel, Field
from datetime import datetime
from typing import Optional

class NewEntity(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    metadata: Optional[str] = None
```

Then run migration or recreate tables.

### Performing Vector Search

```python
from mydata.vectordb import VectorDB
from mydata.embedder import Embedder

embedder = Embedder()
vectordb = VectorDB()

# Embed query
query_vector = embedder.embed("search query")

# Search with optional tag filter
results = vectordb.search(
    vector=query_vector,
    limit=10,
    tags=["project"],  # optional filter
    threshold=0.7
)
```

### Adding Documents to RAG

```python
from mydata.ingestion import IngestPipeline

pipeline = IngestPipeline()

# Add file
pipeline.add_file("/path/to/document.pdf")

# Add raw text
pipeline.add_text(
    text="Content to index",
    source="manual_entry",
    metadata={"category": "notes"}
)
```

### Hybrid Search (Vector + BM25)

```python
from mydata.hybrid_search import hybrid_search

results = hybrid_search(
    query="find all project proposals",
    limit=10,
    vector_weight=0.7,  # 70% semantic
    bm25_weight=0.3     # 30% keyword
)
```

## Frontend Development

### API Client Usage

Location: `promethean-light-ui/src/lib/api.js`

The API client auto-detects Tauri vs browser mode:

```javascript
import { searchDocuments, chat, getStats, checkDaemon } from '$lib/api.js';

// Search
const results = await searchDocuments('my query', 20);

// Chat with RAG
const response = await chat('What projects are active?', conversationId);

// Get system stats
const stats = await getStats();
```

### Svelte Stores

Location: `promethean-light-ui/src/lib/stores.js`

```javascript
import {
    searchQuery,
    searchResults,
    isSearching,
    chatMessages,
    daemonConnected,
    stats,
    activeSection
} from '$lib/stores.js';

// Subscribe to store
$: console.log($searchResults);

// Update store
searchQuery.set('new query');
activeSection.set('admin');
```

### Adding a New Component

Create in `promethean-light-ui/src/lib/components/`:

```svelte
<script>
    import { searchResults, isSearching } from '$lib/stores.js';
    import { searchDocuments } from '$lib/api.js';

    export let title = 'Default Title';

    async function handleSearch(query) {
        isSearching.set(true);
        try {
            const results = await searchDocuments(query);
            searchResults.set(results);
        } finally {
            isSearching.set(false);
        }
    }
</script>

<div class="component-wrapper">
    <h2>{title}</h2>
    {#if $isSearching}
        <p>Loading...</p>
    {:else}
        {#each $searchResults as result}
            <div class="result">{result.text}</div>
        {/each}
    {/if}
</div>

<style>
    .component-wrapper {
        background: var(--bg-secondary);
        padding: 1rem;
        border-radius: 8px;
    }
</style>
```

### CSS Variables (Design Tokens)

```css
/* Dark theme colors used throughout */
--bg-primary: #1a1a1a;
--bg-secondary: #252525;
--bg-tertiary: #2d2d2d;
--text-primary: #ffffff;
--text-secondary: #a0a0a0;
--accent-orange: #ff6b35;
--accent-blue: #4a9eff;
--border-color: #404040;
```

## Common Tasks

### Start Development Server

```bash
# Backend API (from project root)
python -m mydata.daemon

# Frontend dev (from promethean-light-ui/)
npm run dev

# Build Tauri app
npm run tauri build
```

### Rebuild Vector Database

```bash
python rebuild_vectordb.py
# Or via API: POST /admin/rebuild-vectors
```

### Add Note via CLI

```bash
python save_note.py "Text content to save"
```

### Check Database Schema

```bash
python check_schema.py
```

## API Endpoints Reference

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Health check |
| POST | `/add` | Add text document |
| POST | `/add/file` | Add file document |
| POST | `/search` | Semantic search |
| GET | `/documents/{id}` | Get document by ID |
| GET | `/stats` | Database statistics |
| POST | `/chat` | RAG chatbot query |
| GET | `/admin/info` | System information |
| POST | `/admin/rebuild-vectors` | Trigger rebuild |
| GET | `/admin/rebuild-vectors/status` | Rebuild progress |

## Configuration

Key settings in `mydata/config.py`:

```python
# Embedding
EMBEDDING_MODEL = "BAAI/bge-large-en-v1.5"
CHUNK_SIZE = 512
CHUNK_OVERLAP = 50

# Search
SIMILARITY_THRESHOLD = 0.7
HYBRID_VECTOR_WEIGHT = 0.7
HYBRID_BM25_WEIGHT = 0.3

# API
API_HOST = "127.0.0.1"
API_PORT = 8000
```

## Testing Changes

1. **Backend**: Run API and test with curl or the UI
2. **Frontend**: Use `npm run dev` for hot-reload
3. **Integration**: Test full flow from UI → API → Qdrant → Response

## Troubleshooting

- **Daemon won't start**: Check if port 8000 is in use
- **Search returns empty**: Verify Qdrant is running, check threshold
- **UI can't connect**: Ensure daemon is running, check CORS settings
- **Embedding slow**: First load caches model; subsequent loads are fast
