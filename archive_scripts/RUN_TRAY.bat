@echo off
REM Quick launcher for Promethean Light System Tray (testing without building exe)

cd /d "C:\Code\Promethian  Light"

echo.
echo ================================================================================
echo  PROMETHEAN LIGHT - SYSTEM TRAY (DEV MODE)
echo ================================================================================
echo.
echo  Starting system tray application...
echo  (Look for the torch icon in your system tray)
echo.
echo ================================================================================
echo.

REM Install dependencies if needed
pip install pillow pystray >nul 2>&1

REM Run the system tray app
pythonw system_tray.py

if %errorlevel% neq 0 (
    echo.
    echo [ERROR] Failed to start. Trying with console output...
    python system_tray.py
    pause
)
