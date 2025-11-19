#!/usr/bin/env python3
"""Get Promethean Light stats - for Claude to call"""

import json
from mydata.client import Client

client = Client()

try:
    stats = client.stats()
    print(json.dumps(stats, indent=2))
except RuntimeError as e:
    print(json.dumps({"error": str(e)}))
except Exception as e:
    print(json.dumps({"error": f"An unexpected error occurred: {e}"}))
