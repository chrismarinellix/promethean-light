@echo off
REM Test network access to Promethean Light API

echo ========================================
echo NETWORK ACCESS TEST
echo ========================================
echo.

REM Get IP address
for /f "tokens=2 delims=:" %%a in ('ipconfig ^| findstr /c:"IPv4 Address"') do (
    set IP_ADDR=%%a
)
set IP_ADDR=%IP_ADDR:~1%

echo Your IP: %IP_ADDR%
echo Your Hostname: %COMPUTERNAME%
echo.

echo Testing API server...
echo.

echo [1] Testing localhost access...
curl -s http://localhost:8000/stats
if %errorlevel% equ 0 (
    echo [OK] Localhost access working
) else (
    echo [FAIL] Localhost access failed - is the server running?
    echo Run START.bat to start the server
    goto :end
)
echo.

echo [2] Testing network access via IP...
curl -s http://%IP_ADDR%:8000/stats
if %errorlevel% equ 0 (
    echo [OK] Network access via IP working
) else (
    echo [FAIL] Network access failed
    echo.
    echo Troubleshooting:
    echo   1. Run ENABLE_NETWORK_ACCESS.bat
    echo   2. Check firewall settings
    echo   3. Restart START.bat
)
echo.

echo [3] Testing network access via hostname...
curl -s http://%COMPUTERNAME%:8000/stats
if %errorlevel% equ 0 (
    echo [OK] Network access via hostname working
) else (
    echo [WARNING] Hostname access failed (this is sometimes normal)
    echo Team can still use IP address: http://%IP_ADDR%:8000
)
echo.

echo ========================================
echo TEAM ACCESS URLS
echo ========================================
echo.
echo Share these URLs with your team:
echo.
echo   http://%IP_ADDR%:8000
echo   http://%COMPUTERNAME%:8000
echo.
echo API Endpoints:
echo   /search?q=query          - Search documents
echo   /stats                   - System statistics
echo   /recent?limit=10         - Recent documents
echo   /tags                    - All tags
echo   /clusters                - Topic clusters
echo.

:end
echo.
pause
