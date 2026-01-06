@echo off
REM Install automated daily backup to Windows Task Scheduler
REM Best practice: Runs at 2:00 AM daily when system is idle

echo.
echo ╔══════════════════════════════════════════════════════════╗
echo ║  PROMETHEAN LIGHT - INSTALL BACKUP SCHEDULE              ║
echo ╚══════════════════════════════════════════════════════════╝
echo.
echo This will create a Windows Task to backup Promethean Light:
echo   • Runs daily at 2:00 AM
echo   • Backs up SQLite DB, Qdrant vector DB, and program files
echo   • Location: V:\mel_energy_office\Business Dev\Data Base Backup
echo   • Retention: 7 daily, 4 weekly, 12 monthly backups
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

REM Get current directory
set "SCRIPT_DIR=%~dp0"
set "PYTHON_SCRIPT=%SCRIPT_DIR%backup_system.py"

REM Verify Python script exists
if not exist "%PYTHON_SCRIPT%" (
    echo ✗ ERROR: backup_system.py not found!
    echo   Expected: %PYTHON_SCRIPT%
    echo.
    pause
    exit /b 1
)

echo Creating scheduled task...
echo.

REM Delete existing task if present
schtasks /delete /tn "PrometheanLightBackup" /f >nul 2>&1

REM Create new scheduled task
REM Runs at 2:00 AM daily, highest privileges, whether user is logged on or not
schtasks /create ^
    /tn "PrometheanLightBackup" ^
    /tr "python \"%PYTHON_SCRIPT%\"" ^
    /sc daily ^
    /st 02:00 ^
    /rl highest ^
    /f

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ✓ Backup schedule installed successfully!
    echo.
    echo Task Details:
    echo   Name: PrometheanLightBackup
    echo   Schedule: Daily at 2:00 AM
    echo   Script: %PYTHON_SCRIPT%
    echo.
    echo You can verify this in Task Scheduler:
    echo   1. Press Win+R
    echo   2. Type: taskschd.msc
    echo   3. Look for "PrometheanLightBackup"
    echo.
    echo To run backup immediately, use BACKUP_NOW.bat
) else (
    echo.
    echo ✗ Failed to create scheduled task!
    echo   Check that you ran this as Administrator
)

echo.
pause
