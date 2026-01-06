@echo off
REM Disable network access for Promethean Light (localhost only)

echo ========================================
echo DISABLE NETWORK ACCESS
echo ========================================
echo.

echo Reverting to localhost-only mode...
setx API_HOST "127.0.0.1"
echo [OK] API_HOST set to 127.0.0.1 (localhost only)
echo.

echo Removing firewall rule...
powershell -Command "Start-Process netsh -ArgumentList 'advfirewall firewall delete rule name=\"Promethean Light API\"' -Verb RunAs"
echo [OK] Firewall rule removed
echo.

echo Network access disabled. Restart START.bat to apply changes.
echo.
pause
