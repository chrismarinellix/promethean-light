#!/usr/bin/env python3
"""Get Promethean Light stats - for Claude to call"""

import json
import requests

try:
    response = requests.get("http://localhost:8000/stats", timeout=5)
    response.raise_for_status()
    stats = response.json()

    print(json.dumps(stats, indent=2))
except requests.exceptions.ConnectionError:
    print(json.dumps({"error": "Daemon not running. Start with START.bat"}))
except Exception as e:
    print(json.dumps({"error": str(e)}))
