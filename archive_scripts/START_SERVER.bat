@echo off
title Promethean Light - Network Server
color 0A

cls
echo.
echo ========================================================================
echo                     PROMETHEAN LIGHT SERVER
echo                      Network Access Mode
echo ========================================================================
echo.
echo  Server will be accessible to your team at:
echo.
echo    * http://10.210.250.5:8000
echo    * http://VYSUSGROUPdzZSm:8000
echo.
echo  Dashboard: http://10.210.250.5:8000/dashboard
echo.
echo ========================================================================
echo.

cd /d "%~dp0"

REM Set network access
set API_HOST=0.0.0.0
set API_PORT=8000

echo  Starting Promethean Light daemon...
echo  You will be prompted for your passphrase.
echo.
echo ========================================================================
echo.

REM Start the daemon
python -m mydata.daemon

echo.
echo ========================================================================
echo  Server stopped.
echo ========================================================================
echo.
pause
