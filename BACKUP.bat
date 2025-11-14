@echo off
REM Backup Promethean Light database

echo.
echo ═══════════════════════════════════════════════════════════
echo    PROMETHEAN LIGHT - BACKUP
echo ═══════════════════════════════════════════════════════════
echo.

REM Create backup directory with timestamp
set BACKUP_DIR=%USERPROFILE%\.mydata_backups
set TIMESTAMP=%DATE:~-4%%DATE:~-10,2%%DATE:~-7,2%_%TIME:~0,2%%TIME:~3,2%%TIME:~6,2%
set TIMESTAMP=%TIMESTAMP: =0%
set BACKUP_PATH=%BACKUP_DIR%\backup_%TIMESTAMP%

if not exist "%USERPROFILE%\.mydata" (
    echo No Promethean Light data found. Run START.bat first.
    pause
    exit /b 1
)

echo Creating backup...
echo.

if not exist "%BACKUP_DIR%" mkdir "%BACKUP_DIR%"

xcopy "%USERPROFILE%\.mydata" "%BACKUP_PATH%\" /E /I /Y /Q

echo.
echo ✓ Backup complete!
echo.
echo Location: %BACKUP_PATH%
echo.
echo Your backups: %BACKUP_DIR%\
dir /b "%BACKUP_DIR%"
echo.
pause
