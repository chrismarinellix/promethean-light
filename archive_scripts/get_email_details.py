import sqlite3
import sys
from pathlib import Path

# Ensure UTF-8 output
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

db_path = Path.home() / ".mydata" / "mydata.db"
conn = sqlite3.connect(str(db_path))
cur = conn.cursor()

# Get latest 10 emails with full content
rows = cur.execute("""
    SELECT id, source, created_at, raw_text
    FROM documents
    WHERE source_type='email'
    ORDER BY created_at DESC
    LIMIT 10
""").fetchall()

for i, row in enumerate(rows, 1):
    email_id, source, created_at, raw_text = row

    print(f"\n{'='*80}")
    print(f"EMAIL #{i}")
    print(f"{'='*80}")
    print(f"Date: {created_at}")
    print(f"Source: {source}")
    print(f"\nFull Content:")
    print(f"{'-'*80}")
    print(raw_text)
    print(f"{'-'*80}\n")

conn.close()
