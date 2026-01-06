# Promethean Light - System Tray Application

A sleek system tray application for Promethean Light with a beautiful Prometheus torch icon!

## Features

- **System Tray Icon**: Beautiful Prometheus torch icon with flame animation
- **Quick Access Menu**:
  - Start/Stop God Mode with one click
  - Open Web Interface (http://localhost:8000)
  - Quick Access Menu for common queries
  - Easy quit option
- **Auto-Start Support**: Can be added to Windows startup
- **Notifications**: Toast notifications for status updates

## Quick Start

### Option 1: Run Without Building (Testing)

Double-click `RUN_TRAY.bat` to test the system tray app immediately.

### Option 2: Build Executable (Recommended)

1. Double-click `build_tray.bat`
2. Wait for build to complete (2-3 minutes)
3. Find your executable in `dist\Promethean Light.exe`
4. Run it!

## Adding to System Startup

To have Promethean Light start automatically when Windows boots:

### Method 1: Manual
1. Run `build_tray.bat` to create the executable
2. Right-click `dist\Promethean Light.exe` → Create Shortcut
3. Press `Win + R`, type: `shell:startup`, press Enter
4. Move the shortcut to the Startup folder

### Method 2: Using Shell Command
```batch
# Create shortcut in startup folder
powershell "$WshShell = New-Object -comObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup\Promethean Light.lnk'); $Shortcut.TargetPath = '%CD%\dist\Promethean Light.exe'; $Shortcut.Save()"
```

## Icon Details

The Prometheus torch icon features:
- Stylized torch with flames
- Gradient fire colors (red-orange → yellow)
- Subtle glow effect
- Bronze/brown torch base
- Multi-resolution support (16x16 to 128x128)

## System Tray Menu

When you click the tray icon, you'll see:

```
╔════════════════════════════╗
║  Start God Mode            ║  ← Start the daemon
║  Stop God Mode             ║  ← Stop the daemon (shown when running)
║  ──────────────            ║
║  Quick Access Menu         ║  ← Interactive query menu
║  Web Interface             ║  ← Open browser to API
║  ──────────────            ║
║  Quit                      ║  ← Exit tray app
╚════════════════════════════╝
```

## Requirements

- Windows 10/11
- Python 3.8+
- Pillow (for icon generation)
- pystray (for system tray)
- PyInstaller (for building executable)

All dependencies are auto-installed by the build script.

## Troubleshooting

### Icon doesn't appear
- Check if another Promethean Light instance is running
- Try running `RUN_TRAY.bat` to see console output

### Build fails
- Ensure Python 3.8+ is installed
- Run: `pip install --upgrade pillow pystray pyinstaller`
- Check antivirus isn't blocking PyInstaller

### Daemon won't start
- Ensure you've run `python -m mydata setup` first
- Check if port 8000 is already in use
- Look for error messages in the daemon console window

## File Structure

```
Promethian  Light/
├── system_tray.py          # Main tray application
├── create_icon.py          # Icon generator
├── promethean.ico          # Generated icon file
├── build_tray.bat          # Build executable script
├── RUN_TRAY.bat           # Quick test launcher
├── tray_requirements.txt   # Dependencies
└── dist/
    └── Promethean Light.exe  # Built executable
```

## Customization

### Change Icon
Edit `create_icon.py` to modify:
- Colors (line 13-18)
- Flame shape (line 37-54)
- Glow effect (line 25-34)

Then run `python create_icon.py` to regenerate.

### Change Menu Items
Edit `system_tray.py`, function `create_menu()` (around line 98)

## Support

For issues, check:
- Console output when running via `RUN_TRAY.bat`
- Daemon logs: `%USERPROFILE%\.mydata\logs\`
- GitHub issues: https://github.com/anthropics/claude-code/issues

---

**Enjoy your God Mode! 🔥**
