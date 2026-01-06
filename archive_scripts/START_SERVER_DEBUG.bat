@echo off
title Promethean Light - DEBUG MODE
color 0C

cls
echo.
echo ========================================================================
echo                     PROMETHEAN LIGHT SERVER - DEBUG MODE
echo ========================================================================
echo.

cd /d "%~dp0"

REM Set network access
set API_HOST=0.0.0.0
set API_PORT=8000

echo [DEBUG] Current directory: %CD%
echo [DEBUG] API_HOST: %API_HOST%
echo [DEBUG] API_PORT: %API_PORT%
echo.
echo [DEBUG] Checking Python...
python --version
echo.
echo [DEBUG] Checking mydata module...
python -c "import mydata; print('Module found:', mydata.__file__)"
echo.
echo [DEBUG] Starting daemon with full error output...
echo ========================================================================
echo.

REM Start the daemon with error output
python -m mydata.daemon

echo.
echo ========================================================================
echo [DEBUG] Daemon exited with error code: %ERRORLEVEL%
echo ========================================================================
echo.
echo Press any key to see the error and exit...
pause
