# Promethean Light - Status Dashboard

## 📊 Real-Time Database & Ingestion Monitoring

A beautiful, auto-refreshing web dashboard that shows you the current state of your Promethean Light database and ingestion system.

## Features

✨ **Live Statistics**
- Total documents ingested
- Vector chunks (searchable segments)
- Auto-generated tags and clusters
- Documents ingested today and in last 24 hours

📈 **Ingestion Timeline**
- Latest ingestion timestamp
- Earliest document timestamp
- Database age calculation

📁 **Document Breakdown**
- Documents by type (emails, files, etc.)
- Recent documents list with timestamps

⚙️ **System Status**
- Daemon status (running/offline)
- Crypto unlock status
- API endpoint health

🔄 **Auto-Refresh**
- Updates every 30 seconds automatically
- Real-time monitoring without manual refresh

## How to Use

### Option 1: Start with Dashboard (Recommended)

```bash
START_WITH_DASHBOARD.bat
```

This will:
1. Start the Promethean Light daemon in background
2. Automatically open the status dashboard in your browser
3. Keep the daemon running

### Option 2: View Dashboard Separately

If daemon is already running:

```bash
VIEW_STATUS.bat
```

Or simply navigate to: http://localhost:8000/status

### Option 3: Manual Access

1. Make sure daemon is running (`START.bat`)
2. Open browser to: http://localhost:8000/status

## After Code Changes

**IMPORTANT:** If you update the code (like adding the dashboard), you need to restart the daemon:

```bash
# Stop the daemon
taskkill /F /IM python.exe

# Start with dashboard
START_WITH_DASHBOARD.bat
```

## Dashboard Sections

### Stats Cards (Top)
- 📚 Total Documents - All documents in database
- 🔍 Vector Chunks - Searchable text segments
- 🏷️ Auto-Tags - ML-generated tags
- ⚡ Last 24 Hours - Recent activity

### Ingestion Timeline
Shows when documents were first and last added, plus database age.

### Documents by Type
Visual breakdown of document types (emails, PDFs, text files, etc.)

### Recent Documents
Last 10 documents ingested in the past 24 hours with timestamps.

### System Status
- Daemon health check
- Encryption status
- API endpoint URL

## Troubleshooting

### Dashboard shows "Error: Could not connect to daemon"

**Solution:** Start the daemon first
```bash
START.bat
```

### Dashboard shows old data

**Solution:** Refresh the page or wait 30 seconds for auto-refresh

### New endpoint not found (404)

**Solution:** Restart the daemon to load new code
```bash
taskkill /F /IM python.exe
START_WITH_DASHBOARD.bat
```

### Port 8000 already in use

**Solution:** Check if another instance is running
```bash
netstat -ano | findstr :8000
taskkill /F /PID <process_id>
```

## Access URLs

- **Status Dashboard:** http://localhost:8000/status
- **API Root:** http://localhost:8000/
- **API Stats:** http://localhost:8000/stats
- **Dashboard Stats:** http://localhost:8000/dashboard/stats (JSON)
- **Main Dashboard:** http://localhost:8000/static/dashboard.html

## Integration with Claude Code

You can set up Claude Code to automatically show the dashboard when you navigate to the Promethean Light folder:

1. Add to your shell profile (`.bashrc` or `.zshrc`):
   ```bash
   cd() {
       builtin cd "$@"
       if [[ "$PWD" == *"Promethian  Light"* ]]; then
           if command -v start &> /dev/null; then
               start http://localhost:8000/status 2>/dev/null
           fi
       fi
   }
   ```

2. Or create an alias:
   ```bash
   alias pl='cd "C:\Code\Promethian  Light" && VIEW_STATUS.bat'
   ```

## API Endpoint

The dashboard fetches data from: `GET /dashboard/stats`

Response includes:
- `total_documents` - Total count
- `total_chunks` - Vector DB chunks
- `total_tags` - Auto-generated tags
- `total_clusters` - Document clusters
- `docs_today` - Documents added today
- `docs_last_24h` - Documents added in last 24 hours
- `latest_ingestion` - Last ingestion timestamp
- `earliest_ingestion` - First document timestamp
- `docs_by_type` - Array of {type, count}
- `recent_documents` - Array of recent docs
- `daemon_status` - "running" or "offline"
- `crypto_unlocked` - Boolean

## Files Created

```
mydata/
  api.py                           # Updated with /dashboard/stats endpoint
  static/
    status.html                     # Status dashboard page
    dashboard.html                  # Main company dashboard (existing)

START_WITH_DASHBOARD.bat            # Start daemon + open dashboard
VIEW_STATUS.bat                     # Open dashboard (daemon must be running)
STATUS_DASHBOARD_README.md          # This file
```

## Tips

1. **Leave dashboard open** in a browser tab for continuous monitoring
2. **Bookmark** http://localhost:8000/status for quick access
3. **Auto-refresh** happens every 30 seconds, but you can manually refresh anytime
4. **Responsive design** works on mobile/tablet if accessing from other devices on network

---

**Created:** November 24, 2025
**Version:** 1.0
