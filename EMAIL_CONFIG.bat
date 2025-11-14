@echo off
REM Configure email history settings

echo.
echo ═══════════════════════════════════════════════════════════
echo    PROMETHEAN - EMAIL CONFIGURATION
echo ═══════════════════════════════════════════════════════════
echo.
echo Current settings:
echo   History: Last 24 hours (default)
echo   Folders: Inbox + Sent Items
echo   Duplicates: Automatically prevented
echo.
echo.
echo How far back do you want to load emails?
echo.
echo   1. Last 2 hours (minimal)
echo   2. Last 24 hours (default)
echo   3. Last 7 days (1 week)
echo   4. Last 30 days (1 month)
echo.
set /p choice="Enter choice (1-4): "

if "%choice%"=="1" set HOURS=2
if "%choice%"=="2" set HOURS=24
if "%choice%"=="3" set HOURS=168
if "%choice%"=="4" set HOURS=720

echo.
echo ✓ Configuration set to last %HOURS% hours
echo.
echo Edit daemon.py line 168 to change:
echo   history_hours=%HOURS%
echo.
echo Then restart daemon (Ctrl+C, then START.bat)
echo.
pause
