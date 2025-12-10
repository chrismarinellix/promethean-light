@echo off
echo ================================================
echo   Promethean Light UI - Building Release
echo ================================================
echo.

cd /d "%~dp0"

:: Check if node_modules exists
if not exist "node_modules" (
    echo Installing dependencies...
    npm install
)

echo Building optimized release...
npm run tauri build

echo.
echo ================================================
echo   Build Complete!
echo ================================================
echo.
echo Find the installer at:
echo   src-tauri\target\release\bundle\nsis\
echo.
echo Find the executable at:
echo   src-tauri\target\release\promethean-light-ui.exe
echo.
pause
