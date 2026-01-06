import sqlite3
from pathlib import Path

db_path = Path.home() / ".mydata" / "mydata.db"
conn = sqlite3.connect(str(db_path))
cur = conn.cursor()

# Count total emails
total = cur.execute("SELECT COUNT(*) FROM documents WHERE source_type='email'").fetchone()[0]
print(f"\n{'='*80}")
print(f"TOTAL EMAILS IN DATABASE: {total}")
print(f"{'='*80}\n")

# Get latest 10 emails
rows = cur.execute("""
    SELECT id, source, created_at, raw_text
    FROM documents
    WHERE source_type='email'
    ORDER BY created_at DESC
    LIMIT 10
""").fetchall()

print(f"LATEST 10 EMAILS:\n")

for i, row in enumerate(rows, 1):
    email_id, source, created_at, raw_text = row

    # Extract sender from source (format: email://sender/uid)
    if "/" in source:
        parts = source.split("/")
        sender = parts[2] if len(parts) > 2 else source
    else:
        sender = source

    # Get preview
    preview = raw_text[:300] if len(raw_text) > 300 else raw_text

    print(f"[{i}] {created_at}")
    print(f"    From: {sender}")
    print(f"    Preview: {preview}")
    if len(raw_text) > 300:
        print("    ...")

    # Check for action items
    text_lower = raw_text.lower()
    actions = []

    if any(word in text_lower for word in ["please", "can you", "could you", "need you to", "action required"]):
        actions.append("[!] Action/Request")
    if any(word in text_lower for word in ["deadline", "due", "asap", "urgent", "eod", "eow"]):
        actions.append("[!!!] Urgent")
    if any(word in text_lower for word in ["review", "approve", "sign off", "feedback"]):
        actions.append("[R] Review")
    if any(word in text_lower for word in ["meeting", "call", "schedule", "zoom", "teams"]):
        actions.append("[M] Meeting")
    if any(word in text_lower for word in ["invoice", "payment", "expense", "budget"]):
        actions.append("[$] Financial")

    if actions:
        print(f"    >> ACTIONS: {', '.join(actions)}")

    print()

conn.close()
