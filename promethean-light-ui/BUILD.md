# Building Promethean Light UI

## Prerequisites

1. **Rust** - Install from https://rustup.rs/
2. **Node.js** (v18+) - Install from https://nodejs.org/
3. **Tauri CLI** - Will be installed via npm

## Quick Start (Development)

```bash
cd promethean-light-ui

# Install dependencies
npm install

# Run in development mode (requires Promethean Light daemon running)
npm run tauri dev
```

## Build for Production

```bash
# Build the optimized release binary
npm run tauri build
```

The final binary will be in `src-tauri/target/release/` and installers in `src-tauri/target/release/bundle/`.

Alternatively, use the batch files:
- `DEV.bat` - Start development mode
- `BUILD_RELEASE.bat` - Build production release

## Icon Generation

Before building, generate proper icons. Create a 1024x1024 PNG icon named `app-icon.png` then run:

```bash
npm run tauri icon app-icon.png
```

Or manually place icons in `src-tauri/icons/`:
- 32x32.png
- 128x128.png
- 128x128@2x.png
- icon.ico (Windows)
- icon.icns (macOS)

## File Structure

```
promethean-light-ui/
├── src/                    # SvelteKit frontend
│   ├── routes/             # Pages
│   ├── lib/
│   │   ├── components/     # Svelte components
│   │   │   ├── ChatPanel.svelte      # Main Q&A interface
│   │   │   ├── Sidebar.svelte        # Navigation & stats
│   │   │   ├── AdminPanel.svelte     # System admin
│   │   │   ├── AddNoteModal.svelte   # Add notes
│   │   │   └── FileUploadModal.svelte # File uploads
│   │   ├── stores.js       # State management
│   │   └── api.js          # API helpers (with debugging)
│   ├── app.css             # Global styles
│   └── app.html            # HTML template
├── src-tauri/              # Rust backend
│   ├── src/
│   │   ├── lib.rs          # Main Tauri app (network requests)
│   │   └── main.rs         # Entry point
│   ├── icons/              # App icons
│   ├── Cargo.toml          # Rust dependencies
│   └── tauri.conf.json     # Tauri config
└── package.json            # Node dependencies
```

## Features

- **Chat/Ask Mode**: RAG-powered Q&A with your data using Claude AI
- **Quick Query Lozenges**: One-click common queries (Team, Projects, Emails, Analysis)
- **System Tray**: Minimizes to tray, click to restore
- **Saved Searches**: Bookmark responses to folders (Reports, Research, General)
- **Real-time Stats**: Documents, chunks, tags, source counts
- **File Upload**: Drag-and-drop with duplicate detection
- **Add Notes**: Quick paste text snippets for indexing
- **Voice Input**: Speech-to-text queries (Chrome/Edge)
- **Dark Theme**: Native Windows 11 look
- **Admin Panel**: System status, database info, LLM configuration

## Debugging

The UI includes comprehensive debug logging. To view logs:

1. Open DevTools in the Tauri app (F12 or right-click > Inspect)
2. Go to the Console tab
3. Look for logs prefixed with `[PL timestamp] [Component]`

Example log output:
```
[PL 08:30:00.123] [DAEMON] Checking daemon connection...
[PL 08:30:00.456] [API] GET /stats
[PL 08:30:00.789] [STATS] Stats via HTTP: {total_documents: 3795, ...}
```

## Connecting to Daemon

The UI connects to `http://127.0.0.1:8000` by default. Make sure the Promethean Light daemon is running:

```bash
# From the main Promethean Light directory
START_PL2000.bat

# Or manually:
python -m mydata daemon
```

## Troubleshooting

### "Could not connect to daemon" error
1. Check the daemon terminal window is running
2. Click the **Refresh** button in the sidebar
3. Restart the daemon if it crashed

### LLM shows "None"
1. Ensure your Anthropic API key is set in environment or .env file
2. Click Refresh to re-fetch API status
3. Check Admin panel for detailed status

### Chat not returning results
1. Open DevTools (F12) and check Console for errors
2. Test the daemon directly: `curl http://127.0.0.1:8000/chat -X POST -H "Content-Type: application/json" -d "{\"message\": \"test\"}"`
3. Ensure the vector database has content (check stats)

## Binary Size

With the release profile optimizations, expect:
- Windows: ~5-8 MB
- macOS: ~4-6 MB
- Linux: ~4-6 MB
