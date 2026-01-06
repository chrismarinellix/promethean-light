@echo off
REM Install Promethean Light to auto-start on system boot

echo ========================================
echo INSTALL AUTO-START ON BOOT
echo ========================================
echo.
echo This will create a Windows Task Scheduler task to:
echo   - Start Promethean Light automatically on boot
echo   - Run even if not logged in
echo   - Restart on failure
echo   - Run with highest privileges
echo.
echo Press any key to continue or Ctrl+C to cancel...
pause > nul
echo.

REM Get current directory
set SCRIPT_DIR=%~dp0
set START_SCRIPT=%SCRIPT_DIR%START_NETWORK_SERVER.bat

echo Creating scheduled task...
echo.

REM Create task XML file
set TASK_XML=%TEMP%\promethean_light_task.xml

(
echo ^<?xml version="1.0" encoding="UTF-16"?^>
echo ^<Task version="1.2" xmlns="http://schemas.microsoft.com/windows/2004/02/mit/task"^>
echo   ^<RegistrationInfo^>
echo     ^<Description^>Promethean Light - Personal Knowledge Base Server^</Description^>
echo     ^<URI^>\Promethean Light Daemon^</URI^>
echo   ^</RegistrationInfo^>
echo   ^<Triggers^>
echo     ^<BootTrigger^>
echo       ^<Enabled^>true^</Enabled^>
echo       ^<Delay^>PT1M^</Delay^>
echo     ^</BootTrigger^>
echo   ^</Triggers^>
echo   ^<Principals^>
echo     ^<Principal^>
echo       ^<UserId^>%USERNAME%^</UserId^>
echo       ^<LogonType^>InteractiveToken^</LogonType^>
echo       ^<RunLevel^>HighestAvailable^</RunLevel^>
echo     ^</Principal^>
echo   ^</Principals^>
echo   ^<Settings^>
echo     ^<MultipleInstancesPolicy^>IgnoreNew^</MultipleInstancesPolicy^>
echo     ^<DisallowStartIfOnBatteries^>false^</DisallowStartIfOnBatteries^>
echo     ^<StopIfGoingOnBatteries^>false^</StopIfGoingOnBatteries^>
echo     ^<AllowHardTerminate^>true^</AllowHardTerminate^>
echo     ^<StartWhenAvailable^>true^</StartWhenAvailable^>
echo     ^<RunOnlyIfNetworkAvailable^>false^</RunOnlyIfNetworkAvailable^>
echo     ^<IdleSettings^>
echo       ^<StopOnIdleEnd^>false^</StopOnIdleEnd^>
echo       ^<RestartOnIdle^>false^</RestartOnIdle^>
echo     ^</IdleSettings^>
echo     ^<AllowStartOnDemand^>true^</AllowStartOnDemand^>
echo     ^<Enabled^>true^</Enabled^>
echo     ^<Hidden^>false^</Hidden^>
echo     ^<RunOnlyIfIdle^>false^</RunOnlyIfIdle^>
echo     ^<WakeToRun^>false^</WakeToRun^>
echo     ^<ExecutionTimeLimit^>PT0S^</ExecutionTimeLimit^>
echo     ^<Priority^>7^</Priority^>
echo     ^<RestartOnFailure^>
echo       ^<Interval^>PT1M^</Interval^>
echo       ^<Count^>3^</Count^>
echo     ^</RestartOnFailure^>
echo   ^</Settings^>
echo   ^<Actions Context="Author"^>
echo     ^<Exec^>
echo       ^<Command^>"%START_SCRIPT%"^</Command^>
echo       ^<WorkingDirectory^>%SCRIPT_DIR%^</WorkingDirectory^>
echo     ^</Exec^>
echo   ^</Actions^>
echo ^</Task^>
) > "%TASK_XML%"

echo Task XML created at: %TASK_XML%
echo.

REM Import task into Task Scheduler
schtasks /create /tn "Promethean Light Daemon" /xml "%TASK_XML%" /f

if %errorlevel% equ 0 (
    echo.
    echo ========================================
    echo SUCCESS
    echo ========================================
    echo.
    echo Promethean Light will now start automatically:
    echo   - On system boot ^(1 minute delay^)
    echo   - Even if not logged in
    echo   - Will restart on failure ^(up to 3 times^)
    echo.
    echo To test the task:
    echo   schtasks /run /tn "Promethean Light Daemon"
    echo.
    echo To view task status:
    echo   schtasks /query /tn "Promethean Light Daemon" /v
    echo.
    echo To remove auto-start:
    echo   Run UNINSTALL_AUTO_START.bat
    echo.
) else (
    echo.
    echo ========================================
    echo ERROR
    echo ========================================
    echo.
    echo Failed to create scheduled task.
    echo Try running this script as Administrator.
    echo.
)

REM Cleanup
del "%TASK_XML%"

pause
