@echo off
REM Manual backup trigger for Promethean Light
REM Run this anytime to create an immediate backup

echo.
echo ╔══════════════════════════════════════════════════════════╗
echo ║  PROMETHEAN LIGHT - MANUAL BACKUP                        ║
echo ╚══════════════════════════════════════════════════════════╝
echo.

cd /d "%~dp0"

python backup_system.py

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ✓ Backup completed successfully!
) else (
    echo.
    echo ✗ Backup failed! Check the logs in V:\mel_energy_office\Business Dev\Data Base Backup\logs
)

echo.
pause
