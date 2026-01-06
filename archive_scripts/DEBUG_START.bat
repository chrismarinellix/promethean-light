@echo off
title Promethean Light - FULL DEBUG
color 0E

cls
echo ========================================================================
echo                    FULL DEBUG MODE
echo ========================================================================
echo.

cd /d "%~dp0"
echo [1] Current Directory: %CD%
echo.

echo [2] Setting environment variables...
set API_HOST=0.0.0.0
set API_PORT=8000
echo     API_HOST = %API_HOST%
echo     API_PORT = %API_PORT%
echo.

echo [3] Checking Python installation...
python --version 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Python not found!
    pause
    exit /b 1
)
echo.

echo [4] Checking Python path...
where python
echo.

echo [5] Checking if mydata module exists...
python -c "import sys; print('Python executable:', sys.executable); print('Python version:', sys.version)" 2>&1
echo.

echo [6] Testing mydata import...
python -c "import mydata; print('mydata location:', mydata.__file__)" 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Failed to import mydata module!
    pause
    exit /b 1
)
echo.

echo [7] Testing mydata.daemon import...
python -c "from mydata import daemon; print('daemon module OK')" 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Failed to import daemon!
    pause
    exit /b 1
)
echo.

echo [8] Testing crypto unlock...
python -c "from mydata.crypto import CryptoManager; import os; cm = CryptoManager(); print('Crypto initialized'); print('Key file exists:', cm.key_file.exists()); print('MYDATA_PASSPHRASE env:', 'SET' if os.environ.get('MYDATA_PASSPHRASE') else 'NOT SET')" 2>&1
echo.

echo [9] Checking database...
python -c "from mydata.database import Database; db = Database(); print('Database OK')" 2>&1
echo.

echo [10] Now starting daemon with full output...
echo ========================================================================
echo.
python -m mydata.daemon
set ERROR_CODE=%ERRORLEVEL%
echo.
echo ========================================================================
echo [EXIT] Daemon stopped with error code: %ERROR_CODE%
echo ========================================================================
echo.

if %ERROR_CODE% NEQ 0 (
    echo Something went wrong. Error code: %ERROR_CODE%
) else (
    echo Clean exit.
)

echo.
echo Press any key to close...
pause > nul
