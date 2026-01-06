@echo off
REM Start Promethean Light with System Tray Icon
cd /d "%~dp0"
set API_HOST=127.0.0.1
set API_PORT=8000
set MYDATA_PASSPHRASE=prom

REM Start daemon in background, then tray
start /min cmd /c "python -m mydata daemon"

REM Wait for daemon to start
timeout /t 3 /nobreak >nul

REM Start system tray
pythonw archive_scripts\system_tray.py
