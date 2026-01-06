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

print(f"\n{'='*100}")
print(f"DETAILED EMAIL SUMMARY - LAST 7 DAYS ({len(rows)} emails)")
print(f"{'='*100}\n")

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
        subject = raw_text[:100].replace('\n', ' ')

    # Get preview (first 800 chars, cleaned)
    preview = raw_text[:800].replace('\r\n', '\n').replace('\r', '\n')

    email_info = {
        'date': created_at,
        'sender': sender,
        'subject': subject,
        'preview': preview,
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

# Show ALL urgent emails with full details
if urgent_emails:
    print(f"\n{'#'*100}")
    print(f"🔴 URGENT EMAILS ({len(urgent_emails)} total)")
    print(f"{'#'*100}\n")

    for i, email in enumerate(urgent_emails, 1):
        print(f"\n{'='*100}")
        print(f"URGENT #{i}")
        print(f"{'='*100}")
        print(f"Date: {email['date']}")
        print(f"From: {email['sender']}")
        print(f"Subject: {email['subject']}")
        print(f"\n{'-'*100}")
        print("PREVIEW:")
        print(f"{'-'*100}")
        print(email['preview'])
        if len(email['text']) > 800:
            print("\n[... content continues ...]")
        print(f"\n{'='*100}\n")

# Show ALL action emails with full details
if action_emails:
    print(f"\n{'#'*100}")
    print(f"⚠️  ACTION REQUIRED EMAILS ({len(action_emails)} total)")
    print(f"{'#'*100}\n")

    for i, email in enumerate(action_emails, 1):
        print(f"\n{'='*100}")
        print(f"ACTION #{i}")
        print(f"{'='*100}")
        print(f"Date: {email['date']}")
        print(f"From: {email['sender']}")
        print(f"Subject: {email['subject']}")
        print(f"\n{'-'*100}")
        print("PREVIEW:")
        print(f"{'-'*100}")
        print(email['preview'])
        if len(email['text']) > 800:
            print("\n[... content continues ...]")
        print(f"\n{'='*100}\n")

# Show general emails with details
if general_emails:
    print(f"\n{'#'*100}")
    print(f"📧 GENERAL EMAILS ({len(general_emails)} total)")
    print(f"{'#'*100}\n")

    for i, email in enumerate(general_emails, 1):
        print(f"\n{'='*100}")
        print(f"GENERAL #{i}")
        print(f"{'='*100}")
        print(f"Date: {email['date']}")
        print(f"From: {email['sender']}")
        print(f"Subject: {email['subject']}")
        print(f"\n{'-'*100}")
        print("PREVIEW:")
        print(f"{'-'*100}")
        print(email['preview'])
        if len(email['text']) > 800:
            print("\n[... content continues ...]")
        print(f"\n{'='*100}\n")

print(f"\n{'#'*100}")
print(f"FINAL SUMMARY")
print(f"{'#'*100}")
print(f"🔴 Urgent: {len(urgent_emails)} emails")
print(f"⚠️  Action Required: {len(action_emails)} emails")
print(f"📧 General: {len(general_emails)} emails")
print(f"Total: {len(rows)} emails in last 7 days")
print(f"{'#'*100}\n")

conn.close()
