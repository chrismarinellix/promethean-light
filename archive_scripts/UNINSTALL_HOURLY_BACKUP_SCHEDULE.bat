@echo off
REM Uninstall Windows Task Scheduler for Hourly Backups
REM Must run as Administrator

echo.
echo ===============================================================
echo   UNINSTALL HOURLY BACKUP SCHEDULE
echo ===============================================================
echo.
echo This will remove the hourly backup task from Windows Task Scheduler
echo.
echo NOTE: This will NOT delete existing backup files.
echo       Backups remain in: V:\mel_energy_office\Business Dev\Data Base Backup\hourly
echo.
pause

REM Check for admin privileges
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo [ERROR] This script must be run as Administrator
    echo Right-click and select "Run as administrator"
    pause
    exit /b 1
)

echo.
echo Removing hourly backup task...

schtasks /Delete /TN "PrometheanLightHourlyBackup" /F

if errorlevel 1 (
    echo.
    echo [WARNING] Task may not exist or could not be deleted
) else (
    echo.
    echo ===============================================================
    echo [OK] Hourly backup schedule removed successfully!
    echo ===============================================================
)

echo.
echo Task Name: PrometheanLightHourlyBackup has been removed
echo.
echo To reinstall: Run INSTALL_HOURLY_BACKUP_SCHEDULE.bat as Administrator
echo.
pause
