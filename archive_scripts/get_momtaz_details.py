"""Get detailed information about Momtaz"""

import sqlite3
from pathlib import Path
from datetime import datetime, timedelta

# Connect to database
db_path = Path.home() / ".mydata" / "mydata.db"
conn = sqlite3.connect(str(db_path))
cur = conn.cursor()

# Get all emails mentioning Momtaz
rows = cur.execute("""
    SELECT created_at, raw_text
    FROM documents
    WHERE source_type='email'
    AND LOWER(raw_text) LIKE '%momtaz%'
    ORDER BY created_at DESC
    LIMIT 20
""").fetchall()

print(f"\n{'='*100}")
print(f"MOMTAZ - DETAILED UPDATE")
print(f"{'='*100}\n")
print(f"Found {len(rows)} emails mentioning Momtaz\n")

for i, (date, text) in enumerate(rows, 1):
    print(f"\n{'*'*100}")
    print(f"EMAIL {i} - {date}")
    print(f"{'*'*100}\n")

    # Extract subject
    lines = text.split('\n')
    subject = ""
    from_addr = ""

    for line in lines[:30]:
        if line.startswith('Subject:'):
            subject = line.replace('Subject:', '').strip()
        if line.startswith('From:'):
            from_addr = line.replace('From:', '').strip()[:80]

    print(f"From: {from_addr}")
    print(f"Subject: {subject}")
    print(f"\nContent Preview:")
    print("-" * 100)

    # Find mentions of Momtaz in context
    for idx, line in enumerate(lines):
        if 'momtaz' in line.lower():
            # Print context around the mention (3 lines before and after)
            start = max(0, idx - 3)
            end = min(len(lines), idx + 4)
            context = '\n'.join(lines[start:end])
            try:
                print(context.encode('ascii', 'ignore').decode('ascii'))
            except:
                print(context)
            print("\n" + "~" * 80 + "\n")
            break

    if i >= 10:  # Limit to 10 most recent
        print(f"\n... and {len(rows) - 10} more emails")
        break

print(f"\n{'='*100}")
print("END OF MOMTAZ UPDATE")
print(f"{'='*100}\n")

conn.close()
