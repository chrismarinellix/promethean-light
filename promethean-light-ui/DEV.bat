@echo off
title Promethean Light - DEV MODE
color 0B

echo ================================================
echo   Promethean Light UI - Development Mode
echo ================================================
echo.

cd /d "%~dp0"

:: ================================================
:: STEP 1: Check if daemon is already running
:: ================================================
echo [1/4] Checking daemon status...
curl -s http://127.0.0.1:8000/ >nul 2>&1
if %errorlevel%==0 (
    echo       Daemon already running - skipping startup
    goto :start_dev_ui
)

echo       Daemon not running - starting it now...
echo.

:: ================================================
:: STEP 2: Get passphrase and start daemon
:: ================================================
echo [2/4] Authentication required
set /p "MYDATA_PASSPHRASE=  Enter passphrase: "
echo.

set API_HOST=0.0.0.0
set API_PORT=8000

echo       Starting daemon...
start "PL2000 Daemon" /min cmd /c "set MYDATA_PASSPHRASE=%MYDATA_PASSPHRASE%&& set API_HOST=%API_HOST%&& set API_PORT=%API_PORT%&& python -u -m mydata daemon"

:: ================================================
:: STEP 3: Wait for daemon to be ready
:: ================================================
echo [3/4] Waiting for daemon...
set /a attempts=0
set /a maxattempts=60

:waitloop
timeout /t 2 /nobreak >nul
curl -s http://127.0.0.1:8000/ >nul 2>&1
if %errorlevel%==0 goto :daemonready

set /a attempts+=1
set /a mod=attempts %% 5
if %mod%==0 echo       Still starting... [%attempts%/%maxattempts%]
if %attempts% lss %maxattempts% goto :waitloop

echo ERROR: Daemon failed to start!
pause
exit /b 1

:daemonready
echo       Daemon ready!
echo.

:: ================================================
:: STEP 4: Start dev UI
:: ================================================
:start_dev_ui
echo [4/4] Starting dev UI...

:: Kill any existing dev servers on port 5199
set /a kill_attempts=0
:kill_loop
if %kill_attempts% gtr 5 (
    echo       Warning: Could not kill all processes on port 5199 after 5 attempts
    goto :done_killing
)
for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":5199.*LISTENING" 2^>nul') do (
    echo       Killing old dev server ^(PID: %%a^)
    taskkill /PID %%a /F >nul 2>&1
    set /a kill_attempts+=1
    timeout /t 1 /nobreak >nul
    goto kill_loop
)
:done_killing

timeout /t 2 /nobreak >nul

:: Check if node_modules exists
if not exist "node_modules" (
    echo       Installing dependencies...
    npm install
)

echo.
echo ================================================
echo   DEV MODE ACTIVE - Hot reload enabled!
echo   Close this window to stop everything.
echo ================================================
echo.

:: Run Tauri dev
npm run tauri dev

:: Keep window open if there's an error
if errorlevel 1 (
    echo.
    echo ================================================
    echo   ERROR: Dev server failed to start
    echo ================================================
    echo.
    pause
)
