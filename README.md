# Prometheus Light - God Mode

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

A 100% local, encrypted, ML-powered personal knowledge base that ingests files, emails, and pasted text, then makes them instantly searchable with zero cloud tokens.

## 🎯 What is Prometheus Light?

Your personal **God Mode** for data:
- **Paste it** → Encrypted & organized
- **Drop files** → Auto-ingested
- **Connect email** → Searchable archive
- **Ask questions** → Instant semantic search
- **100% local** → No cloud, no leaks, no costs

## ✨ Features

- 🔒 **Military-Grade Encryption**: Argon2id + ChaCha20-Poly1305
- 🤖 **On-Device ML**: bge-small embeddings, HDBSCAN clustering, auto-tagging
- 📧 **Email Ingestion**: IMAP support (Gmail, Outlook, etc.)
- 📁 **File Watching**: Auto-ingest from Documents, Downloads, etc.
- 🔍 **Semantic Search**: Vector similarity + metadata filtering
- 🏷️ **Auto-Tagging**: ML-powered organization
- 📊 **Pattern Detection**: Find trends in your data
- ⚡ **Fast**: Sub-100ms searches, < 100 MB model
- 💰 **Zero Cost**: No APIs, no subscriptions, no tokens

## 🚀 Quick Start

**Windows:**
```powershell
cd "C:\Code\Promethian  Light"
pip install -e .
.\launch.ps1
```

**Linux/macOS:**
```bash
cd "C:/Code/Promethian  Light"
pip install -e .
chmod +x launch.sh && ./launch.sh
```

**First time setup:**
```bash
mydata setup  # Creates encrypted vault
mydata daemon  # Start God Mode
```

See [QUICKSTART.md](QUICKSTART.md) for full guide.

## 📖 Daily Usage

```bash
# Start your session (shows retro banner)
./launch.ps1  # Windows
./launch.sh   # Linux/macOS

# Launch God Mode daemon
mydata daemon

# Add data
echo "Important note" | mydata add --stdin
mydata add ~/Documents/research.pdf

# Search
mydata ask "research findings"
mydata ls
mydata stats

# Email integration
mydata email-add your@gmail.com
```

## Architecture

```
CLI (Typer + Rich)
    ↓
FastAPI Server
    ↓
┌─────────────┬──────────────┬───────────────┐
│   SQLite    │   Qdrant     │   ML Models   │
│ (Encrypted) │  (Vectors)   │  (On-device)  │
└─────────────┴──────────────┴───────────────┘
```

## Commands

- `mydata setup` - Initialize encryption
- `mydata daemon` - Start background services
- `mydata add <file>` - Ingest file
- `mydata ask <query>` - Semantic search
- `mydata ls` - List documents
- `mydata clusters` - Show auto-detected topics
- `mydata email add` - Configure email ingestion
- `mydata backup` - Create encrypted backup

## Data Volume

- **Typical laptop (16 GB RAM)**: 500k documents, 50 GB
- **Search latency**: < 100 ms
- **Embedding size**: 384 dimensions (33 MB model)

## Security

- Master key derived with Argon2id
- SQLite encrypted with ChaCha20-Poly1305
- Embeddings encrypted before storage
- No plaintext on disk (except during active processing)

## License

MIT
