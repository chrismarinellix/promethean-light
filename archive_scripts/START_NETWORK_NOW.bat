@echo off
cd /d "C:\Code\Promethian  Light"
set API_HOST=0.0.0.0
set API_PORT=8000
python -m mydata.daemon
