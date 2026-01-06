@echo off
REM Reset Promethean Light (with automatic backup)

echo.
echo ═══════════════════════════════════════════════════════════
echo    PROMETHEAN LIGHT - RESET WITH BACKUP
echo ═══════════════════════════════════════════════════════════
echo.
echo WARNING: This will reset your vault.
echo A backup will be created first for safety.
echo.
pause

REM Create backup directory with timestamp
set BACKUP_DIR=%USERPROFILE%\.mydata_backups
set TIMESTAMP=%DATE:~-4%%DATE:~-10,2%%DATE:~-7,2%_%TIME:~0,2%%TIME:~3,2%%TIME:~6,2%
set TIMESTAMP=%TIMESTAMP: =0%
set BACKUP_PATH=%BACKUP_DIR%\backup_%TIMESTAMP%

echo.
echo Creating backup at: %BACKUP_PATH%
if not exist "%BACKUP_DIR%" mkdir "%BACKUP_DIR%"

if exist "%USERPROFILE%\.mydata" (
    xcopy "%USERPROFILE%\.mydata" "%BACKUP_PATH%\" /E /I /Y /Q
    echo ✓ Backup created!
) else (
    echo No existing data to backup.
)

echo.
echo Deleting current vault...
rmdir /s /q "%USERPROFILE%\.mydata" 2>nul

if exist "%USERPROFILE%\.mydata" (
    echo Failed to delete. Please close any open programs and try again.
    pause
    exit /b 1
)

echo.
echo ✓ Reset complete!
echo.
echo Your backup is safe at: %BACKUP_PATH%
echo.
echo To restore: xcopy "%BACKUP_PATH%" "%USERPROFILE%\.mydata\" /E /I /Y
echo.
echo Run START.bat to set up fresh vault.
echo.
pause
