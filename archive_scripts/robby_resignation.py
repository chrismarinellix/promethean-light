import sqlite3
from pathlib import Path

db_path = Path.home() / ".mydata" / "mydata.db"
conn = sqlite3.connect(str(db_path))
cur = conn.cursor()

# Search for Robby resignation emails
rows = cur.execute("""
    SELECT id, source, created_at, raw_text
    FROM documents
    WHERE source_type='email'
    AND (
        (LOWER(raw_text) LIKE '%robby%' AND LOWER(raw_text) LIKE '%resign%')
        OR (LOWER(raw_text) LIKE '%robby%' AND LOWER(raw_text) LIKE '%retention%')
        OR (LOWER(raw_text) LIKE '%robby%' AND LOWER(raw_text) LIKE '%leaving%')
        OR LOWER(raw_text) LIKE '%robby - project handover%'
    )
    ORDER BY created_at DESC
""").fetchall()

print(f"\n{'='*120}")
print(f"ROBBY RESIGNATION & RETENTION EMAILS: {len(rows)} found")
print(f"{'='*120}\n")

for i, row in enumerate(rows[:20], 1):  # Show first 20
    email_id, source, created_at, raw_text = row

    # Extract subject
    subject = ""
    for line in raw_text.split('\n'):
        if line.startswith('Subject:'):
            subject = line.replace('Subject:', '').strip().encode('ascii', 'ignore').decode('ascii')[:80]
            break

    if not subject:
        subject = raw_text[:80].encode('ascii', 'ignore').decode('ascii')

    print(f"[{i}] {created_at[:19]}")
    print(f"    Subject: {subject}")

    # Find resignation context
    text_lower = raw_text.lower()
    for keyword in ['resign', 'retention', 'leaving', 'last day', 'handover', 'ajith']:
        if keyword in text_lower:
            idx = text_lower.find(keyword)
            start = max(0, idx - 80)
            end = min(len(raw_text), idx + 200)
            context = raw_text[start:end].replace('\n', ' ').encode('ascii', 'ignore').decode('ascii')
            print(f"    >>> {keyword.upper()}: ...{context}...")
            break

    print()

conn.close()
