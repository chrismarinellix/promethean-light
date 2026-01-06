@echo off
REM Configure laptop for 24/7 server operation

echo ========================================
echo LAPTOP 24/7 SERVER CONFIGURATION
echo ========================================
echo.
echo This script will configure your laptop to:
echo   - Never sleep when plugged in
echo   - Never turn off display when plugged in
echo   - Keep running when lid is closed
echo   - Optimize for server performance
echo.
echo Press any key to continue or Ctrl+C to cancel...
pause > nul
echo.

echo [1/5] Configuring power settings for AC (plugged in)...
powercfg /change monitor-timeout-ac 0
powercfg /change standby-timeout-ac 0
powercfg /change hibernate-timeout-ac 0
powercfg /change disk-timeout-ac 0
echo [OK] Power timeouts disabled when plugged in
echo.

echo [2/5] Setting high performance power plan...
powercfg /setactive 8c5e7fda-e8bf-4a96-9a85-a6e23a8c635c
echo [OK] High performance plan activated
echo.

echo [3/5] Configuring lid close action...
echo NOTE: You'll need to manually set this in Power Options:
echo   1. Open Control Panel ^> Power Options
echo   2. Click "Choose what closing the lid does"
echo   3. Set "When I close the lid" to "Do nothing" for "Plugged in"
echo.
echo Opening Power Options now...
timeout /t 2 /nobreak > nul
control powercfg.cpl,,3
echo.

echo [4/5] Disabling USB selective suspend...
powercfg /setacvalueindex SCHEME_CURRENT 2a737441-1930-4402-8d77-b2bebba308a3 48e6b7a6-50f5-4782-a5d4-53bb8f07e226 0
powercfg /setactive SCHEME_CURRENT
echo [OK] USB selective suspend disabled
echo.

echo [5/5] Current power configuration:
echo.
powercfg /query SCHEME_CURRENT SUB_SLEEP | findstr /C:"Current AC Power Setting Index"
echo.

echo ========================================
echo CONFIGURATION COMPLETE
echo ========================================
echo.
echo Your laptop is now configured for 24/7 operation.
echo.
echo IMPORTANT REMINDERS:
echo   1. Keep laptop plugged into AC power at all times
echo   2. Use a cooling pad to prevent overheating
echo   3. Ensure good ventilation around laptop
echo   4. Monitor temperature periodically
echo   5. Keep Windows Update on manual mode (to prevent auto-restarts)
echo.
echo NEXT STEPS:
echo   - Run ENABLE_NETWORK_ACCESS.bat to enable team access
echo   - Run INSTALL_AUTO_START.bat to start on boot
echo   - Test server access from another computer
echo.
pause
