import sqlite3
from pathlib import Path

db_path = Path.home() / ".mydata" / "mydata.db"
conn = sqlite3.connect(str(db_path))
cur = conn.cursor()

# Search for emails from Robby
rows = cur.execute("""
    SELECT id, source, created_at, raw_text
    FROM documents
    WHERE source_type='email'
    AND (
        LOWER(source) LIKE '%robby%'
        OR LOWER(raw_text) LIKE '%from: %robby%'
        OR LOWER(raw_text) LIKE '%robby.palac%'
    )
    ORDER BY created_at DESC
""").fetchall()

print(f"\n{'='*120}")
print(f"EMAILS FROM ROBBY PALACKAL: {len(rows)} found")
print(f"{'='*120}\n")

for i, row in enumerate(rows[:30], 1):  # Show first 30
    email_id, source, created_at, raw_text = row

    # Extract subject
    subject = ""
    from_line = ""
    for line in raw_text.split('\n'):
        if line.startswith('Subject:'):
            subject = line.replace('Subject:', '').strip().encode('ascii', 'ignore').decode('ascii')[:80]
        if line.startswith('From:') and 'robby' in line.lower():
            from_line = line.replace('From:', '').strip()[:60]

    if not subject:
        subject = raw_text[:80].encode('ascii', 'ignore').decode('ascii')

    print(f"[{i}] {created_at[:19]}")
    print(f"    Subject: {subject}")
    if from_line:
        print(f"    From: {from_line}")

    # Show preview (first 300 chars after headers)
    lines = raw_text.split('\n')
    content_start = 0
    for idx, line in enumerate(lines):
        if line.strip() == '' and idx > 5:  # Find first blank line after headers
            content_start = idx + 1
            break

    content = ' '.join(lines[content_start:content_start+10])[:400]
    content = content.encode('ascii', 'ignore').decode('ascii')
    print(f"    Preview: {content}...")

    # Check if it's about resignation
    if any(word in raw_text.lower() for word in ['resign', 'leaving', 'departure', 'last day', 'handover']):
        print(f"    >>> [RESIGNATION RELATED]")

    print()

conn.close()
