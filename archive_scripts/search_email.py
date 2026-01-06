import sqlite3
import sys
from pathlib import Path

# Get search term from args
search = sys.argv[1] if len(sys.argv) > 1 else "interview"

conn = sqlite3.connect(str(Path.home() / ".mydata" / "mydata.db"))
cur = conn.cursor()

rows = cur.execute(f"""
    SELECT created_at, raw_text
    FROM documents
    WHERE source_type='email'
    AND LOWER(raw_text) LIKE '%{search.lower()}%'
    ORDER BY created_at DESC
    LIMIT 15
""").fetchall()

print(f"\nFOUND {len(rows)} EMAILS MATCHING '{search}':\n")
print("="*100)

for i, (date, text) in enumerate(rows, 1):
    # Extract subject
    subject = ""
    for line in text.split('\n'):
        if line.startswith('Subject:'):
            subject = line.replace('Subject:', '').strip().encode('ascii', 'ignore').decode('ascii')[:70]
            break

    # Clean preview
    preview = text[:600].encode('ascii', 'ignore').decode('ascii')

    print(f"\n[{i}] {date[:16]}")
    print(f"    Subject: {subject}")
    print(f"    Preview: {preview[:200]}...")
    print()

conn.close()
