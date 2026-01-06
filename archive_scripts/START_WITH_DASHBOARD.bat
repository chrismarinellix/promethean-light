@echo off
REM Start Prometheus Light with Status Dashboard
setlocal

cd /d "C:\Code\Promethian  Light"

echo.
echo  ===============================================================================
echo.
echo  ██████╗ ██████╗  ██████╗ ███╗   ███╗███████╗████████╗██╗  ██╗███████╗ █████╗ ███╗   ██╗
echo  ██╔══██╗██╔══██╗██╔═══██╗████╗ ████║██╔════╝╚══██╔══╝██║  ██║██╔════╝██╔══██╗████╗  ██║
echo  ██████╔╝██████╔╝██║   ██║██╔████╔██║█████╗     ██║   ███████║█████╗  ███████║██╔██╗ ██║
echo  ██╔═══╝ ██╔══██╗██║   ██║██║╚██╔╝██║██╔══╝     ██║   ██╔══██║██╔══╝  ██╔══██║██║╚██╗██║
echo  ██║     ██║  ██║╚██████╔╝██║ ╚═╝ ██║███████╗   ██║   ██║  ██║███████╗██║  ██║██║ ╚████║
echo  ╚═╝     ╚═╝  ╚═╝ ╚═════╝ ╚═╝     ╚═╝╚══════╝   ╚═╝   ╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝╚═══════╝
echo                                                                                         ║
echo  ██╗     ██╗ ██████╗ ██╗  ██╗████████╗════════════════════════════════════════════════╝
echo  ██║     ██║██╔════╝ ██║  ██║╚══██╔══╝
echo  ██║     ██║██║  ███╗███████║   ██║
echo  ██║     ██║██║   ██║██╔══██║   ██║
echo  ███████╗██║╚██████╔╝██║  ██║   ██║
echo  ╚══════╝╚═╝ ╚═════╝ ╚═╝  ╚═╝   ╚═╝
echo.
echo                                ─── G O D   M O D E ───
echo.
echo                      [ ENCRYPTED · LOCAL · ML-POWERED DATABASE ]
echo.
echo  ===============================================================================
echo.

REM Check if initialized
if not exist "%USERPROFILE%\.mydata\master.key" (
    echo [FIRST TIME] Running setup...
    echo You'll be asked for a master passphrase - remember it!
    echo.
    python -m mydata setup
    echo.
    echo.
    echo Setup complete! Now starting daemon...
    timeout /t 2 >nul
    echo.
)

echo Starting God Mode daemon in background...
echo.

REM Start daemon in background
start /min cmd /c python -m mydata daemon

REM Wait for daemon to start
echo Waiting for daemon to initialize...
timeout /t 5 /nobreak >nul

REM Open status dashboard
echo Opening status dashboard in browser...
start http://localhost:8000/status

echo.
echo  ✓ Daemon started (running in background)
echo  ✓ Status dashboard opened: http://localhost:8000/status
echo.
echo  Quick commands:
echo    • View dashboard: VIEW_STATUS.bat
echo    • Stop daemon:    taskkill /F /IM python.exe
echo    • View logs:      type "%USERPROFILE%\.mydata\logs\prometheus_*.log"
echo.
echo Press any key to exit (daemon will continue running)...
pause >nul
