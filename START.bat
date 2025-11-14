@echo off
REM Quick start script for Prometheus Light

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

echo Starting God Mode...
echo Press Ctrl+C to stop
echo.
echo [DEBUG] Detailed logs: %USERPROFILE%\.mydata\logs\
echo.
python -m mydata daemon
pause
