@echo off
REM Enable network access for Promethean Light server

echo ========================================
echo PROMETHEAN LIGHT - NETWORK ACCESS SETUP
echo ========================================
echo.

REM Step 1: Set environment variable for network binding
echo [1/4] Configuring API to listen on all network interfaces...
setx API_HOST "0.0.0.0"
echo [OK] API_HOST set to 0.0.0.0 (network access enabled)
echo.

REM Step 2: Get local IP address
echo [2/4] Finding your local IP address...
for /f "tokens=2 delims=:" %%a in ('ipconfig ^| findstr /c:"IPv4 Address"') do (
    set IP_ADDR=%%a
)
set IP_ADDR=%IP_ADDR:~1%
echo [OK] Your IP address: %IP_ADDR%
echo.

REM Step 3: Configure Windows Firewall
echo [3/4] Configuring Windows Firewall...
echo This requires administrator privileges.
echo.
powershell -Command "Start-Process netsh -ArgumentList 'advfirewall firewall add rule name=\"Promethean Light API\" dir=in action=allow protocol=TCP localport=8000' -Verb RunAs"
echo [OK] Firewall rule added for port 8000
echo.

REM Step 4: Get hostname
echo [4/4] Finding your computer hostname...
echo [OK] Hostname: %COMPUTERNAME%
echo.

echo ========================================
echo SETUP COMPLETE
echo ========================================
echo.
echo Your team can now access Promethean Light at:
echo.
echo   Option 1 (IP):       http://%IP_ADDR%:8000
echo   Option 2 (Hostname): http://%COMPUTERNAME%:8000
echo.
echo IMPORTANT:
echo   1. Restart Promethean Light for changes to take effect
echo   2. Your laptop must be running for team access
echo   3. Share the URLs above with your team
echo.
echo Next Steps:
echo   - Run START.bat to restart with network access enabled
echo   - Test access from another computer
echo   - Configure auto-start with INSTALL_TO_STARTUP.bat
echo.
pause
