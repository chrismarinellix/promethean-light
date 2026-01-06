import sqlite3
import sys
from pathlib import Path

# Ensure UTF-8 output
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

db_path = Path.home() / ".mydata" / "mydata.db"
conn = sqlite3.connect(str(db_path))
cur = conn.cursor()

# Get Sandy Creek email
print("\n" + "="*100)
print("SANDY CREEK SF PROJECT EMAIL")
print("="*100)

sandy = cur.execute("""
    SELECT raw_text
    FROM documents
    WHERE source_type='email'
    AND raw_text LIKE '%Sandy Creek SF%'
    ORDER BY created_at DESC
    LIMIT 1
""").fetchone()

if sandy:
    print(sandy[0])
else:
    print("Not found")

# Get all Alinta/Mt Challenger emails
print("\n\n" + "="*100)
print("ALINTA / MT CHALLENGER PROJECT EMAILS")
print("="*100)

alinta_emails = cur.execute("""
    SELECT created_at, raw_text
    FROM documents
    WHERE source_type='email'
    AND (raw_text LIKE '%Mt Challenger%' OR raw_text LIKE '%Alinta%')
    ORDER BY created_at DESC
    LIMIT 5
""").fetchall()

for i, (created_at, raw_text) in enumerate(alinta_emails, 1):
    print(f"\n{'='*100}")
    print(f"ALINTA EMAIL #{i} - {created_at}")
    print("="*100)
    print(raw_text)
    print()

conn.close()
