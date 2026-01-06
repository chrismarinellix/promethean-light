@echo off
REM Uninstall Promethean Light auto-start task

echo ========================================
echo UNINSTALL AUTO-START
echo ========================================
echo.

echo Removing scheduled task "Promethean Light Daemon"...
schtasks /delete /tn "Promethean Light Daemon" /f

if %errorlevel% equ 0 (
    echo [OK] Auto-start disabled
) else (
    echo [WARNING] Task not found or already removed
)

echo.
echo Auto-start has been disabled.
echo Promethean Light will no longer start automatically on boot.
echo.
pause
