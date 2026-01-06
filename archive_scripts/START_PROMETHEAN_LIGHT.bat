@echo off
title Promethean Light

cd /d "C:\Code\Promethian  Light"

:: Start the daemon in background (note: "mydata daemon" not "mydata.daemon")
start /min "PL Daemon" cmd /c "python -m mydata daemon"

:: Wait a moment for daemon to start
timeout /t 5 /nobreak >nul

:: Launch the UI
start "" "C:\Code\Promethian  Light\promethean-light-ui\src-tauri\target\debug\promethean-light-ui.exe"
