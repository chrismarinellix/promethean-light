#!/usr/bin/env python3
"""Add note to Promethean Light - for Claude to call"""

import sys
import json
from pathlib import Path

# Add parent directory to path for imports
parent_dir = Path(__file__).parent.parent
sys.path.insert(0, str(parent_dir))

from mydata.client import Client

text = sys.argv[1] if len(sys.argv) > 1 else ""

if not text:
    print(json.dumps({"error": "No text provided"}))
    sys.exit(1)

# Always use localhost for client connection
client = Client(base_url="http://127.0.0.1:8000")

# Check if server is running
if not client.is_alive():
    print(json.dumps({"error": "Server not running. Start with: START_PL2000.bat or START_DAEMON_SILENT.bat"}))
    sys.exit(1)

# Add via server API
try:
    result = client.add_text(text=text, source="claude")
    print(json.dumps({"success": True, "id": result["id"]}))
except Exception as e:
    print(json.dumps({"error": f"Failed to add: {e}"}))
    sys.exit(1)
