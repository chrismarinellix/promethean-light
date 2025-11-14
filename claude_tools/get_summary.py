#!/usr/bin/env python3
"""Get pre-computed summary - INSTANT, 0 embedding tokens"""

import sys
import json
import requests

summary_name = sys.argv[1] if len(sys.argv) > 1 else "india_staff"

# Available: india_staff, australia_staff, retention_bonuses

try:
    response = requests.get(f"http://localhost:8000/summary/{summary_name}", timeout=5)
    response.raise_for_status()
    summary = response.json()

    print(json.dumps(summary, indent=2))
except requests.exceptions.ConnectionError:
    print(json.dumps({"error": "Daemon not running. Start with START.bat"}))
except Exception as e:
    print(json.dumps({"error": str(e)}))
