@echo off
REM Silent daemon start for auto-start/scheduled task
cd /d "%~dp0"
set API_HOST=0.0.0.0
set API_PORT=8000
set MYDATA_PASSPHRASE=prom
python -m mydata daemon
