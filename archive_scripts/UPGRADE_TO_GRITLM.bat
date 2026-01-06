@echo off
REM Upgrade Promethean Light to GritLM-7B embeddings

cd /d "C:\Code\Promethian  Light"

echo.
echo ================================================================================
echo.
echo   ██████╗ ██████╗ ██╗████████╗██╗     ███╗   ███╗    ███████╗██████╗
echo  ██╔════╝ ██╔══██╗██║╚══██╔══╝██║     ████╗ ████║    ╚════██║██╔══██╗
echo  ██║  ███╗██████╔╝██║   ██║   ██║     ██╔████╔██║        ██╔╝██████╔╝
echo  ██║   ██║██╔══██╗██║   ██║   ██║     ██║╚██╔╝██║       ██╔╝ ██╔══██╗
echo  ╚██████╔╝██║  ██║██║   ██║   ███████╗██║ ╚═╝ ██║    ██████╗██████╔╝
echo   ╚═════╝ ╚═╝  ╚═╝╚═╝   ╚═╝   ╚══════╝╚═╝     ╚═╝    ╚═════╝╚═════╝
echo.
echo                    EMBEDDING MODEL UPGRADE WIZARD
echo.
echo ================================================================================
echo.
echo  Upgrading to: GritLM-7B (4096-dimensional embeddings)
echo.
echo  IMPORTANT NOTES:
echo  - This is a 14GB model download (first time only)
echo  - Requires 8-16GB RAM
echo  - Search will be 2x slower but DRAMATICALLY better quality
echo  - Your existing data will be backed up automatically
echo.
echo ================================================================================
echo.
echo  Press any key to begin upgrade, or Ctrl+C to cancel...
pause >nul

echo.
echo [1/2] Installing/upgrading dependencies...
pip install --upgrade sentence-transformers torch

if %errorlevel% neq 0 (
    echo.
    echo [ERROR] Failed to install dependencies!
    echo.
    pause
    exit /b 1
)

echo.
echo [2/2] Running migration script...
echo.
python migrate_to_gritlm.py

if %errorlevel% neq 0 (
    echo.
    echo [ERROR] Migration failed! Check error messages above.
    echo.
    pause
    exit /b 1
)

echo.
echo.
echo ================================================================================
echo  UPGRADE COMPLETE!
echo ================================================================================
echo.
echo  You can now start Promethean Light with God-Mode search quality!
echo.
echo  Run: START.bat
echo.
echo ================================================================================
pause
