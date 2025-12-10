@echo off
echo Creating Promethean Light startup shortcut...

set SCRIPT_PATH=%~dp0RUN_TRAY.bat
set STARTUP_FOLDER=%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup
set SHORTCUT_PATH=%STARTUP_FOLDER%\Promethean Light.lnk

powershell -Command "$ws = New-Object -ComObject WScript.Shell; $s = $ws.CreateShortcut('%SHORTCUT_PATH%'); $s.TargetPath = '%SCRIPT_PATH%'; $s.WorkingDirectory = '%~dp0'; $s.Description = 'Promethean Light System Tray'; $s.Save()"

if exist "%SHORTCUT_PATH%" (
    echo.
    echo SUCCESS! Promethean Light will now start automatically when Windows starts.
    echo.
    echo Shortcut created at:
    echo %SHORTCUT_PATH%
    echo.
) else (
    echo.
    echo FAILED to create shortcut. Try running as administrator.
    echo.
)

pause
