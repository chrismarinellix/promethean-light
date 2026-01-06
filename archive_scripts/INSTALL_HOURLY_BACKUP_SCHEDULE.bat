@echo off
REM Install Windows Task Scheduler for Hourly Backups (8am-6pm)
REM Must run as Administrator

echo.
echo ===============================================================
echo   INSTALL HOURLY BACKUP SCHEDULE
echo ===============================================================
echo.
echo This will create a Windows Task Scheduler job to run
echo hourly backups every hour from 8am to 6pm (work hours only)
echo.
echo Location: V:\mel_energy_office\Business Dev\Data Base Backup\hourly
echo Retention: Last 24 hourly backups
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
echo Creating hourly backup task...

REM Delete existing task if present
schtasks /Delete /TN "PrometheanLightHourlyBackup" /F >nul 2>&1

REM Create new task that runs every hour from 8am to 6pm
schtasks /Create ^
    /TN "PrometheanLightHourlyBackup" ^
    /TR "\"%~dp0BACKUP_HOURLY.bat\"" ^
    /SC HOURLY ^
    /ST 08:00 ^
    /ET 18:00 ^
    /RI 60 ^
    /RU "%USERNAME%" ^
    /RL HIGHEST ^
    /F

if errorlevel 1 (
    echo.
    echo [ERROR] Failed to create scheduled task
    pause
    exit /b 1
)

echo.
echo ===============================================================
echo [OK] Hourly backup schedule installed successfully!
echo ===============================================================
echo.
echo Task Name: PrometheanLightHourlyBackup
echo Schedule: Every hour from 8:00 AM to 6:00 PM
echo Next Run: Check Task Scheduler (taskschd.msc)
echo.
echo The backup will:
echo - Run every hour during work hours (8am-6pm)
echo - Keep last 24 hourly backups
echo - Use incremental backups (fast, ~5-10 seconds)
echo - Skip runs outside work hours automatically
echo.
echo To view/modify: Press Win+R, type 'taskschd.msc', press Enter
echo.
pause
