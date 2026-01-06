@echo off
REM Build script for Promethean Light System Tray

echo ================================================================================
echo  PROMETHEAN LIGHT - SYSTEM TRAY BUILDER
echo ================================================================================
echo.

REM Check if Python is available
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python not found! Please install Python 3.8+
    pause
    exit /b 1
)

echo [1/4] Installing required dependencies...
pip install pillow pystray pyinstaller >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Failed to install dependencies
    pause
    exit /b 1
)
echo [OK] Dependencies installed

echo.
echo [2/4] Generating Prometheus icon...
python create_icon.py
if %errorlevel% neq 0 (
    echo [ERROR] Failed to create icon
    pause
    exit /b 1
)

echo.
echo [3/4] Building executable with PyInstaller...
echo      (This may take a few minutes...)
echo.

pyinstaller --onefile ^
    --windowed ^
    --icon=promethean.ico ^
    --name="Promethean Light" ^
    --add-data="promethean.ico;." ^
    --hidden-import=pystray ^
    --hidden-import=PIL ^
    --hidden-import=PIL._tkinter_finder ^
    system_tray.py

if %errorlevel% neq 0 (
    echo [ERROR] Build failed!
    pause
    exit /b 1
)

echo.
echo [4/4] Cleaning up build artifacts...
if exist build rmdir /s /q build
if exist "Promethean Light.spec" del /f /q "Promethean Light.spec"

echo.
echo ================================================================================
echo  BUILD COMPLETE!
echo ================================================================================
echo.
echo  Your executable is ready:
echo  Location: %cd%\dist\Promethean Light.exe
echo.
echo  To add to system tray:
echo  1. Right-click the .exe and create a shortcut
echo  2. Press Win+R, type: shell:startup
echo  3. Move the shortcut to the Startup folder
echo.
echo  Or simply run "Promethean Light.exe" now!
echo.
echo ================================================================================
pause
