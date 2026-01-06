@echo off
REM Install Promethean Light to Windows Startup

echo ================================================================================
echo  PROMETHEAN LIGHT - STARTUP INSTALLER
echo ================================================================================
echo.

REM Check if executable exists
if not exist "dist\Promethean Light.exe" (
    echo [ERROR] Executable not found!
    echo.
    echo Please run build_tray.bat first to create the executable.
    echo.
    pause
    exit /b 1
)

echo  This will add Promethean Light to your Windows startup.
echo  The system tray icon will appear automatically when you login.
echo.
echo  Press any key to continue, or Ctrl+C to cancel...
pause >nul

echo.
echo [1/2] Creating shortcut...

REM Use PowerShell to create shortcut
powershell -Command "$WshShell = New-Object -comObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup\Promethean Light.lnk'); $Shortcut.TargetPath = '%CD%\dist\Promethean Light.exe'; $Shortcut.WorkingDirectory = '%CD%'; $Shortcut.Description = 'Promethean Light - God Mode System Tray'; $Shortcut.Save()"

if %errorlevel% neq 0 (
    echo [ERROR] Failed to create shortcut
    pause
    exit /b 1
)

echo [OK] Shortcut created

echo.
echo [2/2] Verifying installation...

if exist "%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup\Promethean Light.lnk" (
    echo [OK] Installation successful!
) else (
    echo [ERROR] Shortcut not found
    pause
    exit /b 1
)

echo.
echo ================================================================================
echo  INSTALLATION COMPLETE!
echo ================================================================================
echo.
echo  Promethean Light will now start automatically when you login.
echo.
echo  To test it now, run: dist\Promethean Light.exe
echo.
echo  To remove from startup:
echo  1. Press Win+R
echo  2. Type: shell:startup
echo  3. Delete "Promethean Light" shortcut
echo.
echo ================================================================================
pause
