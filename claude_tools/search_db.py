#!/usr/bin/env python3
"""Search Promethean Light database - for Claude to call"""

import sys
import json
import requests

query = sys.argv[1] if len(sys.argv) > 1 else ""
limit = int(sys.argv[2]) if len(sys.argv) > 2 else 10

try:
    response = requests.post(
        "http://localhost:8000/search",
        json={"query": query, "limit": limit},
        timeout=10
    )
    response.raise_for_status()
    results = response.json()

    print(json.dumps(results, indent=2))
except requests.exceptions.ConnectionError:
    print(json.dumps({"error": "Daemon not running. Start with START.bat"}))
except Exception as e:
    print(json.dumps({"error": str(e)}))
