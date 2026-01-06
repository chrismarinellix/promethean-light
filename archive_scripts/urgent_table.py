import sqlite3
from pathlib import Path
from datetime import datetime

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

    # Clean up sender
    if sender.startswith("/O=EXCHANGELABS"):
        sender = "Internal"
    sender = sender[:40]

    # Extract subject
    subject = ""
    for line in raw_text.split('\n'):
        if line.startswith('Subject:'):
            subject = line.replace('Subject:', '').strip()
            break
    if not subject:
        subject = raw_text[:60]

    # Clean up special characters
    subject = subject.encode('ascii', 'ignore').decode('ascii')

    # Parse date
    try:
        dt = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
        date_str = dt.strftime('%b %d %H:%M')
    except:
        date_str = created_at[:16]

    email_info = {
        'date': date_str,
        'sender': sender,
        'subject': subject[:60],
        'full': raw_text
    }

    # Check for urgent
    is_urgent = any(word in text_lower for word in
                   ["deadline", "due", "asap", "urgent", "eod", "eow", "immediately", "priority"])

    # Check for action
    is_action = any(word in text_lower for word in
                   ["please", "can you", "could you", "need you to", "action required",
                    "review", "approve", "sign off", "feedback", "check this",
                    "decision", "decide"])

    if is_urgent:
        urgent_emails.append(email_info)
    if is_action:
        action_emails.append(email_info)

# Print URGENT emails table
print("\n" + "="*120)
print(f"URGENT EMAILS (Last 30 days): {len(urgent_emails)} found - Showing top 20")
print("="*120)
print(f"{'#':<4} {'DATE':<12} {'FROM':<35} {'SUBJECT':<65}")
print("-"*120)

for i, email in enumerate(urgent_emails[:20], 1):
    print(f"{i:<4} {email['date']:<12} {email['sender']:<35} {email['subject']:<65}")

# Print ACTION emails table
print("\n" + "="*120)
print(f"EMAILS REQUIRING ACTION (Last 30 days): {len(action_emails)} found - Showing top 20")
print("="*120)
print(f"{'#':<4} {'DATE':<12} {'FROM':<35} {'SUBJECT':<65}")
print("-"*120)

for i, email in enumerate(action_emails[:20], 1):
    print(f"{i:<4} {email['date']:<12} {email['sender']:<35} {email['subject']:<65}")

print("\n" + "="*120)
print(f"SUMMARY: {len(urgent_emails)} urgent, {len(action_emails)} requiring action in last 30 days")
print("="*120 + "\n")

conn.close()
