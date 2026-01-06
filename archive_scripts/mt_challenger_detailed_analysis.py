#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Detailed chronological analysis of Mt Challenger project emails"""

import sqlite3
import sys
from pathlib import Path
from datetime import datetime

# Fix encoding for Windows console
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')

def extract_email_metadata(raw_text):
    """Extract key metadata from email"""
    lines = raw_text.split('\n')
    metadata = {
        'subject': '',
        'from': '',
        'to': '',
        'date': '',
        'body': ''
    }

    header_end = 0
    for idx, line in enumerate(lines[:30]):
        if line.startswith('Subject:'):
            metadata['subject'] = line[8:].strip()
        elif line.startswith('From:'):
            metadata['from'] = line[5:].strip()
        elif line.startswith('To:'):
            metadata['to'] = line[3:].strip()
        elif line.startswith('Date:'):
            metadata['date'] = line[5:].strip()
        elif line.strip() == '' and idx > 5:
            header_end = idx + 1
            break

    # Get body text
    if header_end > 0:
        metadata['body'] = '\n'.join(lines[header_end:])
    else:
        metadata['body'] = raw_text

    return metadata

def main():
    db_path = Path.home() / ".mydata" / "mydata.db"
    conn = sqlite3.connect(str(db_path))
    cur = conn.cursor()

    # Get all Mt Challenger emails from Robby, ordered chronologically
    rows = cur.execute("""
        SELECT id, source, created_at, raw_text
        FROM documents
        WHERE source_type='email'
        AND (
            LOWER(source) LIKE '%robby%'
            OR LOWER(raw_text) LIKE '%from: %robby%'
            OR LOWER(raw_text) LIKE '%robby.palac%'
        )
        AND (
            LOWER(raw_text) LIKE '%mt challenger%'
            OR LOWER(raw_text) LIKE '%mt. challenger%'
            OR LOWER(raw_text) LIKE '%challenger%'
        )
        ORDER BY created_at ASC
    """).fetchall()

    print("=" * 120)
    print("MT CHALLENGER PROJECT - DETAILED CHRONOLOGICAL ANALYSIS")
    print(f"Total emails found: {len(rows)}")
    print("=" * 120)
    print()

    # Group by date
    emails_by_date = {}
    for email_id, source, created_at, raw_text in rows:
        metadata = extract_email_metadata(raw_text)

        # Parse date
        try:
            dt = datetime.fromisoformat(created_at.replace('+00:00', ''))
            date_key = dt.strftime('%Y-%m-%d')
        except:
            date_key = created_at[:10] if created_at else 'Unknown'

        if date_key not in emails_by_date:
            emails_by_date[date_key] = []

        emails_by_date[date_key].append({
            'id': email_id,
            'timestamp': created_at,
            'metadata': metadata,
            'raw_text': raw_text
        })

    # Print chronologically
    for date in sorted(emails_by_date.keys()):
        print(f"\n{'='*120}")
        print(f"DATE: {date}")
        print(f"{'='*120}")

        for email in emails_by_date[date]:
            meta = email['metadata']

            print(f"\nTime: {email['timestamp']}")
            print(f"Subject: {meta['subject'][:100]}")
            print(f"From: {meta['from'][:80]}")

            # Extract key content - look for important markers
            body = meta['body']
            body_lower = body.lower()

            # Check for key issues
            issues = []
            if 'insurance' in body_lower or 'liability' in body_lower:
                issues.append("INSURANCE/LIABILITY")
            if 'contract' in body_lower or 'terms' in body_lower or 't&c' in body_lower:
                issues.append("CONTRACT/T&Cs")
            if 'legal' in body_lower:
                issues.append("LEGAL REVIEW")
            if 'price' in body_lower or 'pricing' in body_lower or 'fee' in body_lower:
                issues.append("PRICING")
            if 'scope' in body_lower:
                issues.append("SCOPE")
            if 'chasing' in body_lower or 'urgent' in body_lower or 'asap' in body_lower:
                issues.append("URGENT/CHASING")
            if 'approved' in body_lower or 'approval' in body_lower:
                issues.append("APPROVAL")
            if 'powerlink' in body_lower or 'plq' in body_lower:
                issues.append("POWERLINK")

            if issues:
                print(f"Key Issues: {', '.join(issues)}")

            # Print relevant excerpts (first 800 chars of body)
            clean_body = ' '.join(body.split())
            if len(clean_body) > 800:
                print(f"\nContent:\n{clean_body[:800]}...")
            else:
                print(f"\nContent:\n{clean_body}")

            print("-" * 120)

    conn.close()

if __name__ == "__main__":
    main()
