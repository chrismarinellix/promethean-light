#!/usr/bin/env python3
"""Add email account to Promethean Light - for Claude to call"""

import sys
import json
import getpass
from mydata.client import Client

email_address = sys.argv[1] if len(sys.argv) > 1 else ""
password = sys.argv[2] if len(sys.argv) > 2 else ""
imap_server = sys.argv[3] if len(sys.argv) > 3 else "imap.gmail.com"

if not email_address:
    print(json.dumps({"error": "No email address provided"}))
    sys.exit(1)

if not password:
    password = getpass.getpass("Email password: ")

client = Client()

try:
    result = client.add_email(email_address=email_address, password=password, imap_server=imap_server)
    print(json.dumps(result, indent=2))
except RuntimeError as e:
    print(json.dumps({"error": str(e)}))
except Exception as e:
    print(json.dumps({"error": f"An unexpected error occurred: {e}"}))
