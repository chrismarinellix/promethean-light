#!/usr/bin/env python3
"""Add email account to Promethean Light - for Claude to call"""

import sys
import json
import requests
import getpass

email_address = sys.argv[1] if len(sys.argv) > 1 else ""
password = sys.argv[2] if len(sys.argv) > 2 else ""
imap_server = sys.argv[3] if len(sys.argv) > 3 else "imap.gmail.com"

if not email_address:
    print(json.dumps({"error": "No email address provided"}))
    sys.exit(1)

if not password:
    password = getpass.getpass("Email password: ")

try:
    response = requests.post(
        "http://localhost:8000/email/add",
        json={
            "email_address": email_address,
            "password": password,
            "imap_server": imap_server,
            "imap_port": 993
        },
        timeout=10
    )
    response.raise_for_status()
    result = response.json()

    print(json.dumps(result, indent=2))
except requests.exceptions.ConnectionError:
    print(json.dumps({"error": "Daemon not running. Start with START.bat"}))
except Exception as e:
    print(json.dumps({"error": str(e)}))
