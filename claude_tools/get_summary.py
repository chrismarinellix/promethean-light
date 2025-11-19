#!/usr/bin/env python3
"""Get pre-computed summary - INSTANT, 0 embedding tokens"""

import sys
import json
from mydata.client import Client

summary_name = sys.argv[1] if len(sys.argv) > 1 else "india_staff"

# Available: india_staff, australia_staff, retention_bonuses

client = Client()

try:
    summary = client.get_summary(summary_name=summary_name)
    print(json.dumps(summary, indent=2))
except RuntimeError as e:
    print(json.dumps({"error": str(e)}))
except Exception as e:
    print(json.dumps({"error": f"An unexpected error occurred: {e}"}))
