@echo off
echo ========================================
echo PROMETHEAN LIGHT SERVER STARTUP
echo Network Access Mode
echo ========================================
echo.
echo This will start the server with network access enabled.
echo Your team will be able to access at:
echo   http://10.210.250.5:8000
echo   http://VYSUSGROUPdzZSm:8000
echo.
echo Please enter your Promethean Light passphrase.
echo It will be set temporarily for this session only.
echo.
set /p PASSPHRASE="Enter passphrase: "
echo.
echo Starting server with network access...
echo.

cd /d "C:\Code\Promethian  Light"
set API_HOST=0.0.0.0
set API_PORT=8000
set MYDATA_PASSPHRASE=%PASSPHRASE%
python -m mydata.daemon
