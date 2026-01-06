@echo off
REM View Promethean Light System Status Dashboard
echo.
echo ========================================
echo  Promethean Light - Status Dashboard
echo ========================================
echo.
echo Opening status dashboard in browser...
echo.

REM Open the status dashboard in default browser
start http://localhost:8000/status

echo.
echo Dashboard opened at: http://localhost:8000/status
echo.
echo Auto-refreshes every 30 seconds
echo Keep this window open to return to command prompt
echo.
pause
