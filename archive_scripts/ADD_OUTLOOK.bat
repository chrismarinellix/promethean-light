@echo off
REM Add Outlook/Vysus Group email to Promethean Light

echo.
echo ═══════════════════════════════════════════════════════════
echo    PROMETHEAN LIGHT - Add Outlook Email
echo ═══════════════════════════════════════════════════════════
echo.
echo Adding: chris.marinelli@vysusgroup.com
echo IMAP Server: outlook.office365.com
echo.
echo You'll need your email password or App Password
echo.

python -c "import getpass, requests, json; pwd = getpass.getpass('Email password: '); r = requests.post('http://localhost:8000/email/add', json={'email_address': 'chris.marinelli@vysusgroup.com', 'password': pwd, 'imap_server': 'outlook.office365.com', 'imap_port': 993}, timeout=10); print(json.dumps(r.json(), indent=2))"

echo.
echo.
echo ✓ Email added!
echo.
echo Now RESTART the daemon (Ctrl+C in daemon window, then START.bat)
echo to begin watching your inbox!
echo.
pause
