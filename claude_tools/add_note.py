#!/usr/bin/env python3
"""Add note to Promethean Light - for Claude to call"""

import sys
import json
import requests

text = sys.argv[1] if len(sys.argv) > 1 else ""

if not text:
    print(json.dumps({"error": "No text provided"}))
    sys.exit(1)

try:
    response = requests.post(
        "http://localhost:8000/add",
        json={"text": text, "source": "claude"},
        timeout=30
    )
    response.raise_for_status()
    result = response.json()

    print(json.dumps({"success": True, "id": result["id"]}))
except requests.exceptions.ConnectionError:
    print(json.dumps({"error": "Daemon not running. Start with START.bat"}))
except Exception as e:
    print(json.dumps({"error": str(e)}))
