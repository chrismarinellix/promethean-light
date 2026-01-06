@echo off
cd /d "C:\Code\Promethian  Light"

echo.
echo ================================================================================
echo.
echo   ██████╗ ██████╗  ██████╗      ██╗███████╗ ██████╗████████╗███████╗
echo   ██╔══██╗██╔══██╗██╔═══██╗     ██║██╔════╝██╔════╝╚══██╔══╝██╔════╝
echo   ██████╔╝██████╔╝██║   ██║     ██║█████╗  ██║        ██║   ███████╗
echo   ██╔═══╝ ██╔══██╗██║   ██║██   ██║██╔══╝  ██║        ██║   ╚════██║
echo   ██║     ██║  ██║╚██████╔╝╚█████╔╝███████╗╚██████╗   ██║   ███████║
echo   ╚═╝     ╚═╝  ╚═╝ ╚═════╝  ╚════╝ ╚══════╝ ╚═════╝   ╚═╝   ╚══════╝
echo.
echo                      CLAUDE CODE PROJECT LAUNCHER
echo.
echo ================================================================================
echo.
echo   Launch multiple projects in Windows Terminal tabs with Claude Code ready!
echo.
echo ================================================================================
echo.

python project_launcher.py

if %errorlevel% neq 0 (
    echo.
    echo [ERROR] Project launcher failed!
    echo.
    pause
    exit /b 1
)
