import sqlite3
from pathlib import Path

db_path = Path.home() / ".mydata" / "mydata.db"
conn = sqlite3.connect(str(db_path))
cur = conn.cursor()

# Get all emails from last 30 days
rows = cur.execute("""
    SELECT id, source, created_at, raw_text
    FROM documents
    WHERE source_type='email'
    AND datetime(created_at) > datetime('now', '-30 days')
    ORDER BY created_at DESC
""").fetchall()

urgent_emails = []
action_emails = []

for row in rows:
    email_id, source, created_at, raw_text = row
    text_lower = raw_text.lower()

    # Extract sender
    if "/" in source:
        parts = source.split("/")
        sender = parts[2] if len(parts) > 2 else source
    else:
        sender = source

    # Extract subject (from raw_text)
    subject = ""
    for line in raw_text.split('\n'):
        if line.startswith('Subject:'):
            subject = line.replace('Subject:', '').strip()
            break

    email_info = {
        'date': created_at,
        'sender': sender,
        'subject': subject if subject else raw_text[:60] + '...',
        'preview': raw_text[:400],
        'full': raw_text
    }

    # Check for urgent keywords
    is_urgent = any(word in text_lower for word in
                   ["deadline", "due", "asap", "urgent", "eod", "eow", "immediately", "priority"])

    # Check for action keywords
    is_action = any(word in text_lower for word in
                   ["please", "can you", "could you", "need you to", "action required",
                    "review", "approve", "sign off", "feedback", "check this",
                    "decision", "decide"])

    if is_urgent:
        urgent_emails.append(email_info)
    if is_action:
        action_emails.append(email_info)

# Display urgent emails
print("\n" + "="*80)
print(f"URGENT EMAILS (Last 30 days): {len(urgent_emails)}")
print("="*80 + "\n")

for i, email in enumerate(urgent_emails[:15], 1):  # Show top 15
    print(f"[{i}] {email['date'][:19]}")
    print(f"    From: {email['sender'][:60]}")
    print(f"    Subject: {email['subject'][:70]}")

    # Find the urgent keyword in context
    text_lower = email['full'].lower()
    for word in ["deadline", "due", "asap", "urgent", "eod", "eow", "immediately", "priority"]:
        if word in text_lower:
            # Find context around keyword
            idx = text_lower.find(word)
            start = max(0, idx - 50)
            end = min(len(email['full']), idx + 100)
            context = email['full'][start:end].replace('\n', ' ')
            print(f"    >>> URGENT: ...{context}...")
            break

    print()

# Display action emails
print("\n" + "="*80)
print(f"EMAILS REQUIRING ACTION (Last 30 days): {len(action_emails)}")
print("="*80 + "\n")

for i, email in enumerate(action_emails[:15], 1):  # Show top 15
    print(f"[{i}] {email['date'][:19]}")
    print(f"    From: {email['sender'][:60]}")
    print(f"    Subject: {email['subject'][:70]}")

    # Find the action keyword in context
    text_lower = email['full'].lower()
    for word in ["please", "can you", "could you", "need you to", "action required",
                 "review", "approve", "sign off", "feedback", "decision"]:
        if word in text_lower:
            idx = text_lower.find(word)
            start = max(0, idx - 40)
            end = min(len(email['full']), idx + 120)
            context = email['full'][start:end].replace('\n', ' ')
            print(f"    >>> ACTION: ...{context}...")
            break

    print()

conn.close()
