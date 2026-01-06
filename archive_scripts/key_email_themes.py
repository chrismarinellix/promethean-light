import sqlite3
import sys
from pathlib import Path
from collections import defaultdict

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

print(f"\n{'='*120}")
print(f"KEY THEMES & ACTION ITEMS - LAST 7 DAYS")
print(f"{'='*120}\n")

# Categorize by project/topic
projects = defaultdict(list)

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

    email_info = {
        'date': created_at,
        'sender': sender,
        'subject': subject,
        'text': raw_text
    }

    # Categorize by project/topic
    if 'vysus' in text_lower and 'invoice' in text_lower and 'overdue' in text_lower:
        projects['OVERDUE INVOICES'].append(email_info)
    elif 'sandy creek' in text_lower or 'bess' in text_lower and 'hybrid' in text_lower:
        projects['SANDY CREEK - HYBRID PV+BESS'].append(email_info)
    elif 'momtaz' in text_lower or 'visa' in text_lower or 'fragomen' in text_lower:
        projects['MOMTAZUR RAHMAN - VISA/IMMIGRATION'].append(email_info)
    elif 'alinta' in text_lower and ('challenger' in text_lower or 'proposal' in text_lower):
        projects['ALINTA MT CHALLENGER - PROPOSAL'].append(email_info)
    elif 'ic7' in text_lower or 'psse' in text_lower:
        projects['IC7 MODEL DEVELOPMENT'].append(email_info)
    elif 'morven' in text_lower:
        projects['MORVEN SOLAR FARM & BESS'].append(email_info)
    elif 'boulder creek' in text_lower or 'boulde' in text_lower:
        projects['BOULDER CREEK'].append(email_info)
    elif 'gerogery' in text_lower:
        projects['GEROGERY'].append(email_info)
    elif 'dongle' in text_lower and 'theft' in text_lower:
        projects['DONGLE THEFT INCIDENT'].append(email_info)
    elif 'salary' in text_lower or 'regrading' in text_lower or 'budget' in text_lower:
        projects['HR - SALARY & BUDGETS'].append(email_info)
    elif 'training' in text_lower or 'handover' in text_lower:
        projects['TRAINING & HANDOVERS'].append(email_info)
    elif 'bowling' in text_lower or 'dinner' in text_lower or 'team' in text_lower:
        projects['TEAM EVENTS'].append(email_info)
    elif 'birdwood' in text_lower:
        projects['BIRDWOOD ENERGY'].append(email_info)
    elif 'lightsource' in text_lower or 'lightsourcebp' in text_lower:
        projects['LIGHTSOURCE BP'].append(email_info)
    else:
        projects['GENERAL/OTHER'].append(email_info)

# Display by category
for category, emails in sorted(projects.items()):
    if not emails:
        continue

    print(f"\n{'#'*120}")
    print(f"📁 {category} ({len(emails)} emails)")
    print(f"{'#'*120}\n")

    for i, email in enumerate(emails, 1):
        # Determine urgency/action
        text_lower = email['text'].lower()

        tags = []
        if any(word in text_lower for word in ["deadline", "due", "asap", "urgent", "eod", "eow", "immediately", "overdue"]):
            tags.append("🔴 URGENT")
        if any(word in text_lower for word in ["please", "can you", "could you", "need you to", "action required"]):
            tags.append("⚠️ ACTION")
        if any(word in text_lower for word in ["review", "approve", "feedback"]):
            tags.append("✍️ REVIEW")
        if any(word in text_lower for word in ["decision", "decide"]):
            tags.append("🎯 DECISION")

        tag_str = " ".join(tags) if tags else "ℹ️ INFO"

        print(f"{i}. [{tag_str}] {email['date'][:10]}")
        print(f"   From: {email['sender'][:80]}")
        print(f"   Subject: {email['subject'][:90]}")

        # Show key excerpt if urgent/action
        if tags:
            # Find key phrases
            preview = email['text'][:600].replace('\n', ' ')
            print(f"   Preview: {preview[:200]}...")

        print()

print(f"\n{'='*120}")
print("CATEGORY SUMMARY:")
print(f"{'='*120}")
for category, emails in sorted(projects.items()):
    if emails:
        urgent = sum(1 for e in emails if any(word in e['text'].lower() for word in ["deadline", "due", "asap", "urgent", "overdue"]))
        print(f"{category:.<60} {len(emails)} emails ({urgent} urgent)")

print(f"\nTotal emails in last 7 days: {len(rows)}")
print(f"{'='*120}\n")

conn.close()
