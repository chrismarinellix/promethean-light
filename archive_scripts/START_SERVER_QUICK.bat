@echo off
echo ========================================
echo PROMETHEAN LIGHT - QUICK START
echo ========================================
echo.
echo Starting server with network access on port 8000...
echo Your team can access at: http://10.210.250.5:8000
echo.

cd /d "C:\Code\Promethian  Light"

REM Set environment for network access
set API_HOST=0.0.0.0
set API_PORT=8000

REM Start the daemon
echo Please enter your passphrase when prompted...
echo.
python -m mydata.daemon

pause
