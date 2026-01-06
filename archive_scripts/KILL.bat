@echo off
REM Kill all running Promethean Light processes

echo.
echo Stopping all Promethean Light processes...
echo.

taskkill /F /FI "WINDOWTITLE eq *mydata*" 2>nul
taskkill /F /FI "IMAGENAME eq python.exe" /FI "MEMUSAGE gt 50000" 2>nul

timeout /t 2 /nobreak >nul

echo.
echo ✓ Processes stopped
echo.
echo You can now run START.bat
echo.
pause
