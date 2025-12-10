@echo off
echo ================================================
echo   Promethean Light UI - Development Mode
echo ================================================
echo.
echo Make sure the Promethean Light daemon is running!
echo.

cd /d "%~dp0"

:: Check if node_modules exists
if not exist "node_modules" (
    echo Installing dependencies...
    npm install
)

:: Run Tauri dev
npm run tauri dev
