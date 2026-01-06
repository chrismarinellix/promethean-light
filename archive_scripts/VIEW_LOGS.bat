@echo off
REM View debug logs

echo.
echo ═══════════════════════════════════════════════════════════
echo             PROMETHEUS LIGHT - DEBUG LOGS
echo ═══════════════════════════════════════════════════════════
echo.

set LOGDIR=%USERPROFILE%\.mydata\logs

if not exist "%LOGDIR%" (
    echo No logs found yet. Run START.bat first.
    pause
    exit /b
)

echo Log directory: %LOGDIR%
echo.
echo Recent logs:
echo.
dir /b /o-d "%LOGDIR%\*.log"
echo.
echo.

REM Get most recent log
for /f "delims=" %%f in ('dir /b /o-d "%LOGDIR%\*.log" 2^>nul') do (
    set LATEST=%%f
    goto :found
)

:found
if defined LATEST (
    echo Opening latest log: %LATEST%
    echo.
    echo ═══════════════════════════════════════════════════════════
    type "%LOGDIR%\%LATEST%"
    echo ═══════════════════════════════════════════════════════════
) else (
    echo No logs found.
)

echo.
pause
