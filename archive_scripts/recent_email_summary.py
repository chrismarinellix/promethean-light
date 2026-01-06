import sqlite3
import sys
from pathlib import Path
from datetime import datetime, timedelta

# Set UTF-8 encoding for output
sys.stdout.reconfigure(encoding='utf-8')

db_path = Path.home() / ".mydata" / "mydata.db"
conn = sqlite3.connect(str(db_path))
cur = conn.cursor()

# Get emails from last 7 days
rows = cur.execute("""
    SELECT id, source, created_at, raw_text
    FROM documents
    WHERE source_type='email'
    AND datetime(created_at) > datetime('now', '-7 days')
    ORDER BY created_at DESC
""").fetchall()

print(f"\n{'='*80}")
print(f"EMAIL SUMMARY - LAST 7 DAYS ({len(rows)} emails)")
print(f"{'='*80}\n")

urgent_emails = []
action_emails = []
general_emails = []

for row in rows:
    email_id, source, created_at, raw_text = row
    text_lower = raw_text.lower()

    # Extract sender
    if "/" in source:
        parts = source.split("/")
        sender = parts[2] if len(parts) > 2 else source
    else:
        sender = source

    # Extract subject
    subject = ""
    for line in raw_text.split('\n'):
        if line.startswith('Subject:'):
            subject = line.replace('Subject:', '').strip()
            break

    if not subject:
        subject = raw_text[:80].replace('\n', ' ')

    email_info = {
        'date': created_at,
        'sender': sender,
        'subject': subject,
        'text': raw_text
    }

    # Categorize
    is_urgent = any(word in text_lower for word in
                   ["deadline", "due", "asap", "urgent", "eod", "eow", "immediately", "priority", "overdue"])

    is_action = any(word in text_lower for word in
                   ["please", "can you", "could you", "need you to", "action required",
                    "review", "approve", "sign off", "feedback", "check this",
                    "decision", "decide", "waiting for", "follow up"])

    if is_urgent:
        urgent_emails.append(email_info)
    elif is_action:
        action_emails.append(email_info)
    else:
        general_emails.append(email_info)

# Show urgent emails
if urgent_emails:
    print(f"\n🔴 URGENT ({len(urgent_emails)} emails)")
    print("=" * 80)
    for i, email in enumerate(urgent_emails[:10], 1):
        print(f"\n[{i}] {email['date'][:19]}")
        print(f"    From: {email['sender'][:70]}")
        print(f"    Subject: {email['subject'][:70]}")

# Show action emails
if action_emails:
    print(f"\n\n⚠️  ACTION REQUIRED ({len(action_emails)} emails)")
    print("=" * 80)
    for i, email in enumerate(action_emails[:10], 1):
        print(f"\n[{i}] {email['date'][:19]}")
        print(f"    From: {email['sender'][:70]}")
        print(f"    Subject: {email['subject'][:70]}")

# Show general emails summary
if general_emails:
    print(f"\n\n📧 GENERAL ({len(general_emails)} emails)")
    print("=" * 80)
    for i, email in enumerate(general_emails[:5], 1):
        print(f"\n[{i}] {email['date'][:19]}")
        print(f"    From: {email['sender'][:70]}")
        print(f"    Subject: {email['subject'][:70]}")

print(f"\n{'='*80}\n")
print(f"SUMMARY: {len(urgent_emails)} urgent, {len(action_emails)} action items, {len(general_emails)} general")
print(f"Total: {len(rows)} emails in last 7 days\n")

conn.close()
