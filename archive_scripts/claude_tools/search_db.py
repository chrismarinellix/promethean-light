#!/usr/bin/env python3
"""Search Promethean Light database - for Claude to call"""

import sys
import json
from mydata.client import Client

query = sys.argv[1] if len(sys.argv) > 1 else ""
limit = int(sys.argv[2]) if len(sys.argv) > 2 else 10

client = Client()

try:
    results = client.search(query=query, limit=limit)
    print(json.dumps(results, indent=2))
except RuntimeError as e:
    print(json.dumps({"error": str(e)}))
except Exception as e:
    print(json.dumps({"error": f"An unexpected error occurred: {e}"}))
