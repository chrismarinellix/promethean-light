# Prometheus Light - God Mode: Quick Start

## 🚀 Installation

### Windows

```powershell
# Navigate to project directory
cd "C:\Code\Promethian  Light"

# Install package
pip install -e .

# Run launcher (shows banner and initializes)
.\launch.ps1
```

### Linux / macOS

```bash
# Navigate to project directory
cd "C:/Code/Promethian  Light"

# Install package
pip install -e .

# Make launcher executable
chmod +x launch.sh

# Run launcher
./launch.sh
```

## 📋 First Time Setup

```bash
# Initialize encryption (creates master key)
mydata setup

# You'll be prompted for a passphrase - remember this!
# All your data will be encrypted with this passphrase
```

## 🎯 Daily Workflow

### Start Your Session

Windows:
```powershell
.\launch.ps1
```

Linux/macOS:
```bash
./launch.sh
```

This shows the retro ASCII banner and puts you in God Mode!

### Basic Commands

```bash
# Start the background daemon (file watcher + email + ML)
mydata daemon

# Add files
mydata add ~/Documents/notes.txt
mydata add ~/Documents/*.pdf

# Add text from clipboard/stdin
echo "Buy 100 shares of TSLA @ $250" | mydata add --stdin

# Search your knowledge base
mydata ask "TSLA stock notes"
mydata ask "dentist appointment"

# List all documents
mydata ls

# Show statistics
mydata stats

# List auto-detected tags
mydata tags

# Show clusters (topics)
mydata clusters
```

## 📧 Email Integration (Optional)

```bash
# Add Gmail account
mydata email-add your@gmail.com

# You'll need a Gmail App Password:
# 1. Enable 2FA on your Google account
# 2. Go to: https://myaccount.google.com/apppasswords
# 3. Generate app password
# 4. Use that password when prompted

# Start daemon to begin watching inbox
mydata daemon
```

## 🔒 Security Notes

- **All data is encrypted** with your master passphrase
- **100% local** - nothing leaves your machine
- **Zero API costs** - all ML runs on-device
- **Encrypted at rest** - no plaintext on disk

### Setting Passphrase via Environment Variable

To avoid typing passphrase every time:

Windows:
```powershell
$env:MYDATA_PASSPHRASE = "your-passphrase"
```

Linux/macOS:
```bash
export MYDATA_PASSPHRASE="your-passphrase"
```

**Warning:** Only do this on secure, personal machines.

## 📊 Understanding the System

### Data Flow

```
Your Data
    ↓
┌─────────────────────────────────────┐
│  File Watcher / Email / Paste       │
│  (Automatic ingestion)              │
└─────────────┬───────────────────────┘
              ↓
┌─────────────────────────────────────┐
│  Encryption Layer                   │
│  (Everything encrypted at rest)     │
└─────────────┬───────────────────────┘
              ↓
┌─────────────────────────────────────┐
│  Text Chunking                      │
│  (512 token chunks with overlap)    │
└─────────────┬───────────────────────┘
              ↓
┌─────────────────────────────────────┐
│  ML Embeddings (bge-small)          │
│  (384-dim vectors, on-device)       │
└─────────────┬───────────────────────┘
              ↓
┌─────────────┬───────────────────────┐
│   SQLite    │   Qdrant (Vectors)    │
│  (Metadata) │   (Semantic search)   │
└─────────────┴───────────────────────┘
              ↓
┌─────────────────────────────────────┐
│  ML Organizer (Background)          │
│  - Auto-tagging                     │
│  - Clustering (HDBSCAN)             │
│  - Pattern detection                │
└─────────────────────────────────────┘
```

### Where is Data Stored?

All data lives in: `~/.mydata/` (or `C:\Users\YourName\.mydata\` on Windows)

```
~/.mydata/
├── master.key              # Encrypted master key
├── salt.bin               # Encryption salt
├── mydata.db              # SQLite database (metadata)
├── qdrant/                # Vector database
├── storage/
│   ├── files/             # Encrypted original files
│   └── embeddings/        # Encrypted embeddings (backup)
└── models/                # Downloaded ML models (cached)
```

## 🎨 Customization

### Watch Different Directories

Edit `mydata/daemon.py` or set environment variable:

```bash
export WATCH_DIRECTORIES="~/Documents,~/Projects,~/Downloads"
```

### Adjust ML Frequency

Edit `mydata/daemon.py`, change `time.sleep(300)` to your preferred interval.

## 🆘 Troubleshooting

### "Module not found" errors

```bash
pip install -e .
```

### Forgot passphrase?

Unfortunately, there's no recovery. Delete `~/.mydata/` and start fresh with `mydata setup`.

### Slow embeddings?

First run downloads the model (~33 MB). Subsequent runs are fast. CPU-only is fine for small batches.

### Permission errors (Linux/macOS)

```bash
chmod 600 ~/.mydata/master.key
chmod 600 ~/.mydata/salt.bin
```

## 🚀 Advanced Usage

### API Server Mode

```bash
# Start FastAPI server
uvicorn mydata.api:app --host 0.0.0.0 --port 8000

# API endpoints available at http://localhost:8000
# Docs: http://localhost:8000/docs
```

### Docker Deployment

```bash
# Build and run
docker-compose up -d

# View logs
docker-compose logs -f

# Stop
docker-compose down
```

## 📈 Performance Tips

- **SSD recommended** for Qdrant vector search
- **16 GB RAM** comfortable for 500k documents
- **First embedding** downloads model (~1 min), then cached
- **Search latency** < 100ms for most queries

## 🎓 Next Steps

1. Run `mydata daemon` in a terminal and leave it running
2. Drop files into your watch directories
3. Paste important text: `echo "..." | mydata add --stdin`
4. Search anytime: `mydata ask "your query"`
5. Check stats: `mydata stats`

Enjoy **God Mode**! 🚀
