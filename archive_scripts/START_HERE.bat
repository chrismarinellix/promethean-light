@echo off
title Promethean Light Server
color 0A

echo.
echo ========================================
echo   PROMETHEAN LIGHT SERVER
echo   Network Access Mode
echo ========================================
echo.
echo Server will be accessible at:
echo   http://10.210.250.5:8000
echo   http://VYSUSGROUPdzZSm:8000
echo.
echo ========================================
echo.

cd /d "%~dp0"
set API_HOST=0.0.0.0
set API_PORT=8000

python -m mydata.daemon

echo.
echo Server stopped.
pause
