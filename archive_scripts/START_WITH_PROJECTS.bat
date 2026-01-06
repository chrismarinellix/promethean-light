@echo off
cd /d "C:\Code\Promethian  Light"

echo.
echo ================================================================================
echo.
echo   ██████╗ ██████╗  ██████╗ ███╗   ███╗███████╗████████╗██╗  ██╗███████╗ █████╗ ███╗   ██╗
echo   ██╔══██╗██╔══██╗██╔═══██╗████╗ ████║██╔════╝╚══██╔══╝██║  ██║██╔════╝██╔══██╗████╗  ██║
echo   ██████╔╝██████╔╝██║   ██║██╔████╔██║█████╗     ██║   ███████║█████╗  ███████║██╔██╗ ██║
echo   ██╔═══╝ ██╔══██╗██║   ██║██║╚██╔╝██║██╔══╝     ██║   ██╔══██║██╔══╝  ██╔══██║██║╚██╗██║
echo   ██║     ██║  ██║╚██████╔╝██║ ╚═╝ ██║███████╗   ██║   ██║  ██║███████╗██║  ██║██║ ╚████║
echo   ╚═╝     ╚═╝  ╚═╝ ╚═════╝ ╚═╝     ╚═╝╚══════╝   ╚═╝   ╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝╚═══════╝
echo                                                                                         ║
echo   ██╗     ██╗ ██████╗ ██╗  ██╗████████╗════════════════════════════════════════════════╝
echo   ██║     ██║██╔════╝ ██║  ██║╚══██╔══╝
echo   ██║     ██║██║  ███╗███████║   ██║
echo   ██║     ██║██║   ██║██╔══██║   ██║
echo   ███████╗██║╚██████╔╝██║  ██║   ██║
echo   ╚══════╝╚═╝ ╚═════╝ ╚═╝  ╚═╝   ╚═╝
echo.
echo                          ─── G O D   M O D E + PROJECTS ───
echo.
echo ================================================================================
echo.
echo   What would you like to do?
echo.
echo   [1] Start Daemon + Launch Projects
echo   [2] Launch Projects Only (daemon already running)
echo   [3] Start Daemon Only (no projects)
echo.
echo ================================================================================
echo.

set /p choice="Enter your choice (1-3): "

if "%choice%"=="1" goto DAEMON_AND_PROJECTS
if "%choice%"=="2" goto PROJECTS_ONLY
if "%choice%"=="3" goto DAEMON_ONLY

echo.
echo Invalid choice. Exiting...
timeout /t 2 >nul
exit /b 1

:DAEMON_AND_PROJECTS
echo.
echo ================================================================================
echo STEP 1: Starting Daemon
echo ================================================================================
echo.
start "Promethean Light Daemon" cmd /k "cd /d C:\Code\Promethian  Light && python -m mydata daemon"
echo ✓ Daemon starting in new window...
echo.
timeout /t 3 >nul
echo ================================================================================
echo STEP 2: Launching Projects
echo ================================================================================
echo.
python project_launcher.py
exit /b 0

:PROJECTS_ONLY
echo.
echo ================================================================================
echo Launching Projects
echo ================================================================================
echo.
python project_launcher.py
exit /b 0

:DAEMON_ONLY
echo.
echo ================================================================================
echo Starting Daemon
echo ================================================================================
echo.
python -m mydata daemon
pause
exit /b 0
