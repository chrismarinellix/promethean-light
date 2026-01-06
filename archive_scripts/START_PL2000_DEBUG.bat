@echo off
title PL2000-GM Server - FULL DEBUG
color 0C

cls
echo.
echo ========================================================================
echo                         PL2000-GM SERVER - DEBUG
echo              Personal Knowledge Base - God Mode
echo ========================================================================
echo.
echo  Server accessible at:
echo    * http://10.210.250.5:8000
echo    * http://VYSUSGROUPdzZSm:8000
echo.
echo  Dashboard: http://10.210.250.5:8000/dashboard
echo  Database: %USERPROFILE%\.mydata\mydata.db
echo.
echo ========================================================================
echo.

cd /d "%~dp0"

REM Set network access
set API_HOST=0.0.0.0
set API_PORT=8000

REM Prompt for passphrase BEFORE starting Python
echo  Please enter your PL2000 passphrase:
set /p "MYDATA_PASSPHRASE=  Passphrase: "

echo.
echo  Starting PL2000-GM daemon with full debug output...
echo  MYDATA_PASSPHRASE is SET: %MYDATA_PASSPHRASE%
echo.
echo ========================================================================
echo.

REM Start with passphrase in environment and capture ALL output
python -m mydata.daemon 2>&1

set ERROR_CODE=%ERRORLEVEL%

echo.
echo ========================================================================
echo  Server stopped with error code: %ERROR_CODE%
echo ========================================================================
echo.

if %ERROR_CODE% NEQ 0 (
    echo  ERROR: Something went wrong (code %ERROR_CODE%)
    echo  Common issues:
    echo    - Incorrect passphrase
    echo    - Port 8000 already in use
    echo    - Missing dependencies
) else (
    echo  Clean exit (no errors reported)
)

echo.
pause
