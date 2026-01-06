@echo off
REM Start Promethean Light with network access enabled

echo ========================================
echo STARTING PROMETHEAN LIGHT SERVER
echo Network Access Mode
echo ========================================
echo.

REM Set environment variable for this session
set API_HOST=0.0.0.0
set API_PORT=8000

echo Configuration:
echo   API Host: %API_HOST% (network access enabled)
echo   API Port: %API_PORT%
echo.

echo Your team can access the server at:
for /f "tokens=2 delims=:" %%a in ('ipconfig ^| findstr /c:"IPv4 Address" ^| findstr /v "192.168.1.1"') do (
    set IP_ADDR=%%a
)
echo   http://%IP_ADDR:~1%:8000
echo   http://%COMPUTERNAME%:8000
echo.

echo Starting daemon...
python -m mydata.daemon

pause
