@echo off
REM Uninstall automated backup from Windows Task Scheduler

echo.
echo ╔══════════════════════════════════════════════════════════╗
echo ║  PROMETHEAN LIGHT - UNINSTALL BACKUP SCHEDULE            ║
echo ╚══════════════════════════════════════════════════════════╝
echo.

REM Check for admin privileges
net session >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo ✗ ERROR: This script requires Administrator privileges
    echo   Right-click and select "Run as administrator"
    echo.
    pause
    exit /b 1
)

echo Removing scheduled task...
echo.

schtasks /delete /tn "PrometheanLightBackup" /f

if %ERRORLEVEL% EQU 0 (
    echo ✓ Backup schedule removed successfully!
    echo.
    echo The scheduled backup has been disabled.
    echo You can still run manual backups with BACKUP_NOW.bat
) else (
    echo ✗ Task not found or failed to remove
)

echo.
pause
