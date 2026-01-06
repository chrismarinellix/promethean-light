# Prometheus Light - God Mode: Quick Start

## 🚀 Installation

Prometheus Light uses a virtual environment (venv) to manage its Python dependencies. The `launch.ps1` (Windows) and `launch.sh` (Linux/macOS) scripts handle the creation and activation of this venv, as well as installing the necessary packages.

**Windows:**
```powershell
# Navigate to project directory
cd "C:\Code\Promethian  Light"

# Run launcher (creates venv, installs dependencies, shows banner and initializes)
.\launch.ps1
```

**Linux / macOS:**
```bash
# Navigate to project directory
cd "C:/Code/Promethian  Light"

# Make launcher executable (if not already)
chmod +x launch.sh

# Run launcher (creates venv, installs dependencies, shows banner and initializes)
./launch.sh
```

## 📋 First Time Setup

```bash
# Initialize encryption (creates master key and default .env file)
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
# The daemon's behavior is configured via the .env file.
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

# Start daemon to begin watching inbox (will use .env settings for polling)
mydata daemon
```

## ⚙️ Configuration

Prometheus Light's behavior is highly customizable through environment variables, typically managed in a `.env` file located in the project's root directory. A default `.env` file is created during `mydata setup`.

**Example `.env` file:**
```
# Prometheus Light Environment
MYDATA_HOME=$HOME/.mydata

# Daemon Settings
WATCH_DIRECTORIES="~/Documents,~/Projects,~/Downloads"
ML_LOOP_INTERVAL_SECONDS=300 # How often (in seconds) the ML organizer runs

# API Settings
API_HOST="127.0.0.1"
API_PORT=8000

# Email Watcher Settings (macOS Outlook example)
MAC_OUTLOOK_POLL_INTERVAL=60 # Polling interval in seconds
MAC_OUTLOOK_DAYS_BACK=30     # How many days back to fetch emails initially

# Email Watcher Settings (Windows Outlook example)
WIN_OUTLOOK_HISTORY_HOURS=1440 # Load last 60 days (2 months) on startup
WIN_OUTLOOK_WATCH_SENT=True    # Also watch sent emails (True/False)
```

Refer to `mydata/settings.py` for a complete list of configurable variables and their default values.

### Setting Passphrase via Environment Variable

To avoid typing the master passphrase every time (e.g., for automated daemon restarts):

Windows:
```powershell
$env:MYDATA_PASSPHRASE = "your_secret_passphrase"
```

Linux/macOS:
```bash
export MYDATA_PASSPHRASE="your_secret_passphrase"
```

**Warning:** Only set `MYDATA_PASSPHRASE` on secure, personal machines where it cannot be easily accessed by others.

## 🔒 Security Notes

- **All data is encrypted** with your master passphrase
- **100% local** - nothing leaves your machine
- **Zero API costs** - all ML runs on-device
- **Encrypted at rest** - no plaintext on disk
