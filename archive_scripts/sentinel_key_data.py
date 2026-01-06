"""Extract key data points from Project Sentinel entries"""
import sqlite3
from pathlib import Path
import re
from collections import defaultdict
from datetime import datetime

db_path = Path.home() / '.mydata' / 'mydata.db'
conn = sqlite3.connect(str(db_path))
conn.row_factory = sqlite3.Row

# Get all Project Sentinel documents
cursor = conn.execute('''
    SELECT DISTINCT d.id, d.source, d.source_type, d.created_at, d.raw_text
    FROM documents d
    LEFT JOIN chunks c ON d.id = c.doc_id
    WHERE d.raw_text LIKE '%Project Sentinel%'
       OR c.text LIKE '%Project Sentinel%'
    ORDER BY d.created_at DESC
''')

results = cursor.fetchall()

# Categories
submission_entries = []
updates = []
meetings = []
retention_related = []
misc = []

print("\n" + "="*100)
print("PROJECT SENTINEL - KEY DATA SUMMARY")
print("="*100)

for row in results:
    text = row['raw_text']
    subject_match = re.search(r'Subject: (.+?)(?:\n|Date:)', text, re.IGNORECASE)
    subject = subject_match.group(1).strip() if subject_match else "N/A"

    date_match = re.search(r'Date: (\d{4}-\d{2}-\d{2})', text)
    email_date = date_match.group(1) if date_match else row['created_at'][:10]

    # Categorize
    if 'Submission' in subject or 'submission' in text[:500]:
        # Try to extract submission number
        sub_num_match = re.search(r'Submission\s+No[.\s]*(\d+)', text, re.IGNORECASE)
        sub_num = sub_num_match.group(1) if sub_num_match else "Unknown"

        # Try to extract submitter
        from_match = re.search(r'From: (.+?)(?:\n|Subject:)', text, re.IGNORECASE)
        sender = "N/A"
        if from_match:
            sender = from_match.group(1).strip()
            if '/CN=' in sender:
                sender_match = re.search(r'-([A-Z0-9.]+)(?:/|$)', sender)
                if sender_match:
                    sender = sender_match.group(1)

        submission_entries.append({
            'number': sub_num,
            'subject': subject,
            'date': email_date,
            'sender': sender,
            'preview': text[text.find('Hi'):text.find('Hi')+300] if 'Hi' in text else text[:300]
        })
    elif 'Update' in subject or 'update' in subject:
        updates.append({'subject': subject, 'date': email_date})
    elif 'meeting' in subject.lower() or 'accepted:' in subject.lower():
        meetings.append({'subject': subject, 'date': email_date})
    elif 'retention' in subject.lower() or 'Retention' in subject:
        retention_related.append({'subject': subject, 'date': email_date})
    else:
        misc.append({'subject': subject, 'date': email_date})

print(f"\nTOTAL ENTRIES: {len(results)}")
print(f"  - Submissions: {len(submission_entries)}")
print(f"  - Updates: {len(updates)}")
print(f"  - Meetings: {len(meetings)}")
print(f"  - Retention-related: {len(retention_related)}")
print(f"  - Other: {len(misc)}")

print("\n" + "="*100)
print("SUBMISSION ENTRIES")
print("="*100)

# Group by submission number
submissions_by_num = defaultdict(list)
for entry in submission_entries:
    submissions_by_num[entry['number']].append(entry)

for num in sorted(submissions_by_num.keys()):
    print(f"\n--- SUBMISSION #{num} ---")
    for entry in submissions_by_num[num]:
        print(f"  Date: {entry['date']}")
        print(f"  Subject: {entry['subject']}")
        print(f"  From: {entry['sender']}")
        if entry['preview'].strip():
            # Clean preview
            preview = entry['preview'].replace('\n', ' ').replace('\r', '')
            preview = re.sub(r'\s+', ' ', preview)
            print(f"  Preview: {preview[:250]}...")
        print()

print("\n" + "="*100)
print("KEY UPDATES")
print("="*100)
for update in updates[:10]:  # Show first 10
    print(f"  [{update['date']}] {update['subject']}")

print("\n" + "="*100)
print("MEETINGS")
print("="*100)
for meeting in meetings[:10]:  # Show first 10
    print(f"  [{meeting['date']}] {meeting['subject']}")

print("\n" + "="*100)
print("RETENTION-RELATED")
print("="*100)
for ret in retention_related:
    print(f"  [{ret['date']}] {ret['subject']}")

# Extract key facts from full text
print("\n" + "="*100)
print("KEY FACTS EXTRACTED")
print("="*100)

cursor = conn.execute('''
    SELECT raw_text FROM documents
    WHERE raw_text LIKE '%Project Sentinel%'
    ORDER BY created_at ASC LIMIT 1
''')
first_doc = cursor.fetchone()
if first_doc:
    text = first_doc[0]
    # Look for the introduction/description
    if 'excited to introduce' in text.lower():
        intro_start = text.lower().find('excited to introduce')
        intro_section = text[intro_start:intro_start+500]
        print("\nProgram Description:")
        print(intro_section[:400] + "...")

# Look for funding/approval mentions
cursor = conn.execute('''
    SELECT raw_text, created_at FROM documents
    WHERE raw_text LIKE '%funding%' AND raw_text LIKE '%Project Sentinel%'
    ORDER BY created_at ASC LIMIT 5
''')
funding_docs = cursor.fetchall()
if funding_docs:
    print("\n\nFunding/Approvals:")
    for doc in funding_docs:
        if 'received funding' in doc[0]:
            idx = doc[0].lower().find('received funding')
            print(f"  [{doc[1][:10]}] {doc[0][idx:idx+200]}...")

conn.close()

print("\n" + "="*100)
