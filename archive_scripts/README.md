# Promethean Light - God Mode

```
╔══════════════════════════════════════════════════════════════════════╗
║    ██████╗ ██████╗  ██████╗ ███╗   ███╗███████╗████████╗██╗  ██╗   ║
║    ██╔══██╗██╔══██╗██╔═══██╗████╗ ████║██╔════╝╚══██╔══╝██║  ██║   ║
║    ██████╔╝██████╔╝██║   ██║██╔████╔██║█████╗     ██║   ███████║   ║
║    ██╔═══╝ ██╔══██╗██║   ██║██║╚██╔╝██║██╔══╝     ██║   ██╔══██║   ║
║    ██║     ██║  ██║╚██████╔╝██║ ╚═╝ ██║███████╗   ██║   ██║  ██║   ║
║             ██╗     ██╗ ██████╗ ██╗  ██╗████████╗                   ║
║             ██║     ██║██╔════╝ ██║  ██║╚══██╔══╝                   ║
║             ██║     ██║██║  ███╗███████║   ██║      ══ GOD MODE ══  ║
║             ██║     ██║██║   ██║██╔══██║   ██║                      ║
║             ███████╗██║╚██████╔╝██║  ██║   ██║                      ║
║         Encrypted · Local · ML-Powered Knowledge Base               ║
╚══════════════════════════════════════════════════════════════════════╝
```

A 100% local, encrypted, ML-powered personal knowledge base that ingests files, emails, and pasted text, then makes them instantly searchable with RAG-powered Q&A via Claude AI.

## What is Promethean Light?

Your personal **God Mode** for data:
- **Paste it** → Encrypted & organized
- **Drop files** → Auto-ingested
- **Connect email** → Searchable archive
- **Ask questions** → RAG-powered answers via Claude AI
- **Desktop UI** → Native Windows/macOS/Linux app
- **100% local storage** → Your data stays on your machine

## Features

- **RAG-Powered Chat**: Ask natural language questions, get answers with source citations
- **Military-Grade Encryption**: Argon2id + ChaCha20-Poly1305
- **On-Device ML**: BGE-Large embeddings (1024 dims), HDBSCAN clustering, auto-tagging
- **Email Ingestion**: Outlook (Windows via win32com, macOS via AppleScript)
- **File Watching**: Auto-ingest from Documents, Downloads, watched folders
- **Semantic Search**: Vector similarity via Qdrant + metadata filtering
- **Desktop UI**: Native Tauri app with system tray, dark theme
- **Quick Queries**: Pre-built lozenges for Team, Projects, Emails, Analysis
- **Voice Input**: Speech-to-text queries (Chrome/Edge)
- **Admin Panel**: System status, database info, LLM configuration
- **Saved Searches**: Bookmark responses to folders

## Quick Start

### Windows (Recommended)

```batch
# Start the full application (daemon + UI)
START_PL2000.bat

# Or for debugging:
START_PL2000_DEBUG.bat
```

### Manual Start

```bash
# 1. Set your passphrase
set MYDATA_PASSPHRASE=your_passphrase

# 2. Start the daemon
python -m mydata daemon

# 3. Launch the UI (in another terminal)
cd promethean-light-ui
npm run tauri dev
```

### First Time Setup

```bash
# 1. Install Python dependencies
pip install -e .

# 2. Set up encryption
mydata setup

# 3. Configure API key (for RAG chat)
set ANTHROPIC_API_KEY=your_key_here

# 4. Start the daemon
START_PL2000.bat
```

See [QUICKSTART.md](QUICKSTART.md) for detailed setup guide.

## Configuration

Promethean Light uses environment variables and a `.env` file for configuration.

**Required:**
```bash
MYDATA_PASSPHRASE=your_encryption_passphrase
ANTHROPIC_API_KEY=your_claude_api_key  # For RAG chat
```

**Optional `.env` settings:**
```
# Data location
MYDATA_HOME=C:\Users\you\.mydata

# Daemon Settings
WATCH_DIRECTORIES="~/Documents,~/Downloads"
ML_LOOP_INTERVAL_SECONDS=300

# API Settings
API_HOST=127.0.0.1
API_PORT=8000

# Email Watcher (Windows Outlook)
WIN_OUTLOOK_HISTORY_HOURS=1440
WIN_OUTLOOK_WATCH_SENT=True
```

Refer to `mydata/settings.py` for all configurable variables.

## Using the UI

The Promethean Light UI provides a visual interface:

1. **Ask Tab**: Chat with your data using natural language
   - Quick query lozenges for common questions
   - Voice input support
   - Save responses to folders

2. **Admin Tab**: System administration
   - View connection status
   - Check LLM configuration
   - Database statistics

3. **Sidebar**: Navigation and stats
   - Document/email/note counts
   - Tag cloud
   - Saved searches

### Debugging

Open DevTools (F12) to see detailed logs:
```
[PL 08:30:00.123] [DAEMON] Checking daemon connection...
[PL 08:30:00.456] [API] GET /stats
[PL 08:30:00.789] [CHAT] Sending message...
```

## CLI Usage

```bash
# Start daemon
python -m mydata daemon

# Add data
mydata add ~/Documents/research.pdf
echo "Important note" | mydata add --stdin

# Search
mydata search "research findings"
mydata stats
```

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│              Promethean Light UI (Tauri)                │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────┐  │
│  │   Chat/Ask  │  │   Sidebar   │  │   Admin Panel   │  │
│  └─────────────┘  └─────────────┘  └─────────────────┘  │
└──────────────────────────┬──────────────────────────────┘
                           │ HTTP (127.0.0.1:8000)
                           ▼
┌─────────────────────────────────────────────────────────┐
│                    FastAPI Server                       │
│  /chat  /search  /stats  /add  /api-keys  /admin       │
└──────────────────────────┬──────────────────────────────┘
                           │
         ┌─────────────────┼─────────────────┐
         ▼                 ▼                 ▼
┌─────────────┐   ┌──────────────┐   ┌───────────────┐
│   SQLite    │   │    Qdrant    │   │   Claude AI   │
│ (Encrypted) │   │  (Vectors)   │   │  (RAG Chat)   │
└─────────────┘   └──────────────┘   └───────────────┘
         │                 │
         └────────┬────────┘
                  ▼
         ┌──────────────┐
         │  BGE-Large   │
         │  Embeddings  │
         │  (1024 dim)  │
         └──────────────┘
```

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Health check |
| `/chat` | POST | RAG-powered Q&A |
| `/search` | POST | Semantic search |
| `/stats` | GET | Database statistics |
| `/add` | POST | Add text content |
| `/add/file` | POST | Upload file |
| `/tags` | GET | Get all tags |
| `/api-keys/status` | GET | Check LLM configuration |
| `/database/info` | GET | Database details |
| `/saved-searches` | GET/POST | Saved responses |

## Troubleshooting

### "Could not connect to daemon"
1. Check daemon terminal is running
2. Click Refresh in sidebar
3. Restart with `START_PL2000.bat`

### LLM shows "None"
1. Set `ANTHROPIC_API_KEY` environment variable
2. Click Refresh to re-check
3. Check Admin panel for status

### Chat returns errors
1. Open DevTools (F12) for logs
2. Test: `curl http://127.0.0.1:8000/chat -X POST -d "{\"message\":\"test\"}"`
3. Check daemon terminal for Python errors

## Data Volume

- **Typical usage**: 10k+ documents
- **Search latency**: < 100 ms
- **Embedding model**: BGE-Large (1024 dimensions)
- **Database**: SQLite + Qdrant (local)

## Security

- Master key derived with Argon2id
- SQLite encrypted with ChaCha20-Poly1305
- All data stored locally
- API key stored in environment (not in code)

## License

MIT
