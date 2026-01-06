@echo off
REM Windows installation script for Prometheus Light

echo.
echo ╔══════════════════════════════════════════════════════════════════════╗
echo ║         PROMETHEUS LIGHT - GOD MODE INSTALLER                        ║
echo ╚══════════════════════════════════════════════════════════════════════╝
echo.

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found. Please install Python 3.11+ first.
    echo Download from: https://www.python.org/downloads/
    pause
    exit /b 1
)

echo [1/4] Installing Prometheus Light...
pip install -e .

if errorlevel 1 (
    echo [ERROR] Installation failed
    pause
    exit /b 1
)

echo.
echo [2/4] Creating data directory...
if not exist "%USERPROFILE%\.mydata" mkdir "%USERPROFILE%\.mydata"

echo.
echo [3/4] Setting up environment...
echo # Prometheus Light Environment > .env
echo MYDATA_HOME=%USERPROFILE%\.mydata >> .env

echo.
echo [4/4] Running first-time setup...
echo.
mydata setup

echo.
echo ╔══════════════════════════════════════════════════════════════════════╗
echo ║                    INSTALLATION COMPLETE!                            ║
echo ╚══════════════════════════════════════════════════════════════════════╝
echo.
echo Next steps:
echo   1. Run:  .\launch.ps1
echo   2. Add email:  mydata email-add chris.marinelli@vysusgroup.com
echo   3. Start daemon:  mydata daemon
echo.
echo For help: mydata --help
echo Full guide: USAGE_GUIDE.md
echo.
pause
