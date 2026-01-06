import sqlite3
import sys
from pathlib import Path

# Ensure UTF-8 output
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

db_path = Path.home() / ".mydata" / "mydata.db"
conn = sqlite3.connect(str(db_path))
cur = conn.cursor()

# Get all Alinta/Mt Challenger emails
print("\n" + "="*100)
print("ALINTA / MT CHALLENGER PROJECT EMAILS - MOST RECENT")
print("="*100)

alinta_emails = cur.execute("""
    SELECT created_at, raw_text
    FROM documents
    WHERE source_type='email'
    AND (raw_text LIKE '%Mt Challenger%' OR raw_text LIKE '%Q7193%')
    ORDER BY created_at DESC
    LIMIT 3
""").fetchall()

for i, (created_at, raw_text) in enumerate(alinta_emails, 1):
    print(f"\n{'#'*100}")
    print(f"ALINTA EMAIL #{i} - DATE: {created_at}")
    print(f"{'#'*100}\n")
    print(raw_text)
    print("\n" + "="*100 + "\n")

conn.close()
