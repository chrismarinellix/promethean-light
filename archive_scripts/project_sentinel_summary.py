"""Extract all Project Sentinel entries with key data"""
import sqlite3
from pathlib import Path
import re
from datetime import datetime
import sys
import io

# Set UTF-8 encoding for output
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

db_path = Path.home() / '.mydata' / 'mydata.db'
conn = sqlite3.connect(str(db_path))
conn.row_factory = sqlite3.Row

# Search for Project Sentinel in documents and chunks
cursor = conn.execute('''
    SELECT DISTINCT d.id, d.source, d.source_type, d.created_at, d.updated_at, d.cluster_id,
           d.raw_text
    FROM documents d
    LEFT JOIN chunks c ON d.id = c.doc_id
    WHERE d.raw_text LIKE '%Project Sentinel%'
       OR c.text LIKE '%Project Sentinel%'
    ORDER BY d.created_at DESC
    LIMIT 100
''')

results = cursor.fetchall()

print(f"\n{'='*100}")
print(f"PROJECT SENTINEL ENTRIES - FOUND {len(results)} DOCUMENTS")
print(f"{'='*100}\n")

for idx, row in enumerate(results, 1):
    print(f"\n[{idx}] ID: {row['id']}")
    print(f"    Type: {row['source_type']}")
    print(f"    Created: {row['created_at']}")

    # Get tags
    tag_cursor = conn.execute('SELECT tag, confidence FROM tags WHERE doc_id = ?', (row['id'],))
    tags = tag_cursor.fetchall()
    if tags:
        tag_list = [f"{t['tag']}({t['confidence']:.2f})" for t in tags]
        print(f"    Tags: {', '.join(tag_list)}")

    # Extract key info from email
    text = row['raw_text']

    # Extract sender/from
    from_match = re.search(r'From: (.+?)(?:\n|Subject:)', text, re.IGNORECASE)
    if from_match:
        sender = from_match.group(1).strip()
        # Clean up Exchange paths
        if '/CN=RECIPIENTS/CN=' in sender:
            sender_match = re.search(r'/CN=RECIPIENTS/CN=.*?-(.+?)(?:/|$)', sender)
            if sender_match:
                sender = sender_match.group(1)
        print(f"    From: {sender}")

    # Extract subject
    subject_match = re.search(r'Subject: (.+?)(?:\n|Date:)', text, re.IGNORECASE)
    if subject_match:
        subject = subject_match.group(1).strip()
        print(f"    Subject: {subject}")

    # Extract date
    date_match = re.search(r'Date: (.+?)(?:\n|$)', text, re.IGNORECASE)
    if date_match:
        email_date = date_match.group(1).strip()
        print(f"    Email Date: {email_date[:10]}")

    # Extract preview (first meaningful line after headers)
    lines = text.split('\n')
    preview_lines = []
    skip_headers = True
    for line in lines:
        line = line.strip()
        if skip_headers:
            if line and not line.startswith(('From:', 'Subject:', 'Date:', '***', 'Microsoft', 'Hi ', 'Hello')):
                if 'Project Sentinel' in line or len(line) > 20:
                    skip_headers = False
        if not skip_headers and line:
            if len(line) > 15 and not line.startswith(('http', '___', '===', 'Microsoft Teams')):
                preview_lines.append(line)
            if len(preview_lines) >= 3:
                break

    if preview_lines:
        print(f"    Preview: {' '.join(preview_lines)[:200]}...")

    print(f"    {'-'*96}")

conn.close()

print(f"\n{'='*100}")
print(f"Total: {len(results)} Project Sentinel documents")
print(f"{'='*100}\n")
