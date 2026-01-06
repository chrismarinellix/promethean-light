@echo off
REM Promethean Light - Run Hourly Backup (8am-6pm)
REM Usage: Double-click to run manual hourly backup

echo.
echo ===============================================================
echo   PROMETHEAN LIGHT - HOURLY BACKUP
echo ===============================================================
echo.
echo Running hourly backup (work hours only: 8am-6pm)...
echo.

cd /d "%~dp0"
python backup_system.py --hourly

if errorlevel 1 (
    echo.
    echo [ERROR] Hourly backup failed! Check logs for details.
    echo.
    pause
    exit /b 1
) else (
    echo.
    echo [OK] Hourly backup completed successfully!
    echo.
)

REM Auto-close after 3 seconds if run from scheduler
timeout /t 3 /nobreak >nul 2>&1
