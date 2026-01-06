@echo off
echo ========================================
echo SET PASSPHRASE FOR AUTO-START
echo ========================================
echo.
echo This will save your passphrase so the server
echo can start automatically without prompting.
echo.
echo WARNING: Your passphrase will be stored in
echo Windows environment variables. Only do this
echo if your laptop is secure.
echo.
pause
echo.

set /p PASS="Enter your Promethean Light passphrase: "

echo.
echo Saving passphrase...
setx MYDATA_PASSPHRASE "%PASS%"

echo.
echo [OK] Passphrase saved!
echo.
echo You can now run START_HERE.bat and it will
echo start automatically without asking for passphrase.
echo.
echo To remove the passphrase later:
echo   setx MYDATA_PASSPHRASE ""
echo.
pause
