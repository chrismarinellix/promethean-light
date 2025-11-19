#!/usr/bin/env python3
"""Add note to Promethean Light - for Claude to call"""

import sys
import json
from mydata.client import Client

text = sys.argv[1] if len(sys.argv) > 1 else ""

if not text:
    print(json.dumps({"error": "No text provided"}))
    sys.exit(1)

client = Client()

try:
    result = client.add_text(text=text, source="claude")
    print(json.dumps({"success": True, "id": result["id"]}))
except RuntimeError as e:
    print(json.dumps({"error": str(e)}))
except Exception as e:
    print(json.dumps({"error": f"An unexpected error occurred: {e}"}))
