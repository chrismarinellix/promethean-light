#!/usr/bin/env python3
"""Get all tags from Promethean Light - for Claude to call"""

import json
from mydata.client import Client

client = Client()

try:
    tags = client.tags()
    print(json.dumps(tags, indent=2))
except RuntimeError as e:
    print(json.dumps({"error": str(e)}))
except Exception as e:
    print(json.dumps({"error": f"An unexpected error occurred: {e}"}))
