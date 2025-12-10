@echo off
title PL2000-GM Server
color 0A

cls
echo.
echo ========================================================================
echo                         PL2000-GM SERVER
echo              Personal Knowledge Base - God Mode
echo ========================================================================
echo.

cd /d "%~dp0"

REM =========================================================================
REM STEP 1: KILL ANY EXISTING PROCESSES (CLEAN SLATE)
REM =========================================================================
echo  [1/5] Cleaning up existing processes...

REM Kill any existing PL2000 daemon windows
taskkill /FI "WINDOWTITLE eq PL2000 Daemon" /F >nul 2>&1

REM Kill any Python processes using our port (mydata daemon)
for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":8000.*LISTENING" 2^>nul') do (
    echo        Killing process on port 8000 (PID: %%a)
    taskkill /PID %%a /F >nul 2>&1
)

REM Kill any orphaned mydata daemon processes
wmic process where "commandline like '%%mydata%%daemon%%'" call terminate >nul 2>&1
wmic process where "commandline like '%%mydata.daemon%%'" call terminate >nul 2>&1

REM Give processes time to die
timeout /t 2 /nobreak >nul

REM Verify port is free
netstat -ano | findstr ":8000.*LISTENING" >nul 2>&1
if %errorlevel%==0 (
    echo        WARNING: Port 8000 still in use. Forcing cleanup...
    for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":8000.*LISTENING"') do (
        taskkill /PID %%a /F >nul 2>&1
    )
    timeout /t 2 /nobreak >nul
)

echo        Done - system clean
echo.

REM =========================================================================
REM STEP 2: SHOW CONNECTION INFO
REM =========================================================================
echo  Server will be accessible at:
echo    * http://127.0.0.1:8000 (localhost)
echo.
echo  Dashboard: http://127.0.0.1:8000/dashboard
echo  Database: %USERPROFILE%\.mydata\mydata.db
echo.
echo ========================================================================
echo.

REM =========================================================================
REM STEP 3: GET PASSPHRASE
REM =========================================================================
echo  [2/5] Authentication required
set /p "MYDATA_PASSPHRASE=  Enter passphrase: "
echo.

REM Set network access
set API_HOST=0.0.0.0
set API_PORT=8000

REM =========================================================================
REM STEP 4: START DAEMON (with passphrase in environment)
REM =========================================================================
echo  [3/5] Starting PL2000-GM daemon...
echo        (Initial load may take 1-2 minutes for ML models)
echo.

REM Start daemon in background - use cmd /v to enable delayed expansion
REM This ensures MYDATA_PASSPHRASE is passed to the child process
start "PL2000 Daemon" /min cmd /c "set MYDATA_PASSPHRASE=%MYDATA_PASSPHRASE%&& set API_HOST=%API_HOST%&& set API_PORT=%API_PORT%&& python -u -m mydata daemon"

REM =========================================================================
REM STEP 5: WAIT FOR DAEMON TO BE READY
REM =========================================================================
echo  [4/5] Waiting for daemon to be ready...
set /a attempts=0
set /a maxattempts=60

:waitloop
timeout /t 2 /nobreak >nul

REM Check if daemon is responding
curl -s http://127.0.0.1:8000/ >nul 2>&1
if %errorlevel%==0 goto :daemonready

set /a attempts+=1

REM Show progress every 5 attempts
set /a mod=attempts %% 5
if %mod%==0 (
    echo        Still starting... [%attempts%/%maxattempts%]
)

if %attempts% lss %maxattempts% goto :waitloop

REM Timeout - daemon didn't start
echo.
echo  ERROR: Daemon failed to start after %maxattempts% attempts.
echo         Check the PL2000 Daemon window for errors.
echo.
echo  Press any key to exit...
pause >nul
goto :cleanup

:daemonready
echo        Daemon is ready!
echo.

REM Quick verification that search works
curl -s -X POST http://127.0.0.1:8000/search -H "Content-Type: application/json" -d "{\"query\":\"test\",\"limit\":1}" >nul 2>&1
if %errorlevel%==0 (
    echo        Database connection verified!
) else (
    echo        WARNING: Database may not be fully loaded yet
)
echo.

REM =========================================================================
REM STEP 6: LAUNCH UI
REM =========================================================================
echo  [5/5] Launching Promethean Light UI...

REM Check if the UI executable exists
if exist "%~dp0promethean-light-ui\src-tauri\target\release\promethean-light-ui.exe" (
    start "" "%~dp0promethean-light-ui\src-tauri\target\release\promethean-light-ui.exe"
    echo        UI launched!
) else (
    echo        UI executable not found - opening web dashboard instead
    start "" "http://127.0.0.1:8000/dashboard"
)

echo.
echo ========================================================================
echo                    PL2000-GM IS RUNNING!
echo ========================================================================
echo.
echo  Status: ONLINE
echo  Daemon: Running (minimized window)
echo  UI: Launched
echo.
echo  To stop: Close this window or press any key
echo.
echo ========================================================================
pause >nul

:cleanup
REM Kill daemon when user closes
echo.
echo  Shutting down...
taskkill /FI "WINDOWTITLE eq PL2000 Daemon" /F >nul 2>&1

REM Also kill by port just in case
for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":8000.*LISTENING" 2^>nul') do (
    taskkill /PID %%a /F >nul 2>&1
)

echo  Server stopped.
timeout /t 2 /nobreak >nul
