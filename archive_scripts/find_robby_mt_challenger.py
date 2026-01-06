#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Search for emails from Robby about Mt Challenger"""

import sqlite3
import sys
from pathlib import Path

# Fix encoding for Windows console
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')

def main():
    db_path = Path.home() / ".mydata" / "mydata.db"

    if not db_path.exists():
        print(f"Database not found at: {db_path}")
        return

    conn = sqlite3.connect(str(db_path))
    cur = conn.cursor()

    # Count total documents
    total = cur.execute("SELECT COUNT(*) FROM documents WHERE source_type='email'").fetchone()[0]
    print(f"Total emails in database: {total}\n")

    # Search for emails from Robby mentioning Mt Challenger or Challenger
    print("Searching for emails from Robby about Mt Challenger...\n")

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
        ORDER BY created_at DESC
    """).fetchall()

    if not rows:
        print("No emails found from Robby about Mt Challenger.")
        print("\nLet me show all emails from Robby instead...\n")

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
            LIMIT 30
        """).fetchall()

        if not rows:
            print("No emails found from Robby at all.")
            conn.close()
            return

    print(f"\n{'='*120}")
    print(f"FOUND {len(rows)} EMAIL(S)")
    print(f"{'='*120}\n")

    for i, row in enumerate(rows, 1):
        email_id, source, created_at, raw_text = row

        # Extract metadata
        subject = ""
        from_line = ""
        date_line = ""

        for line in raw_text.split('\n'):
            if line.startswith('Subject:'):
                subject = line.replace('Subject:', '').strip()[:100]
            if line.startswith('From:'):
                from_line = line.replace('From:', '').strip()[:80]
            if line.startswith('Date:'):
                date_line = line.replace('Date:', '').strip()[:50]

        if not subject:
            subject = raw_text[:100]

        print(f"[{i}] {created_at[:19] if created_at else 'No date'}")
        print(f"    Subject: {subject}")
        if from_line:
            print(f"    From: {from_line}")
        if date_line:
            print(f"    Date: {date_line}")

        # Look for Mt Challenger / Challenger mentions
        text_lower = raw_text.lower()
        if 'challenger' in text_lower:
            # Find and show context around "challenger"
            idx = text_lower.find('challenger')
            start = max(0, idx - 250)
            end = min(len(raw_text), idx + 250)
            context = raw_text[start:end].replace('\n', ' ').replace('\r', '')

            # Clean up
            context = ' '.join(context.split())  # Normalize whitespace

            print(f"\n    Context around 'Challenger':")
            print(f"    ...{context}...")
        else:
            # Show general preview
            lines = raw_text.split('\n')
            content_start = 0
            for idx, line in enumerate(lines):
                if line.strip() == '' and idx > 5:
                    content_start = idx + 1
                    break

            content = ' '.join(lines[content_start:content_start+8])[:350]
            content = ' '.join(content.split())  # Normalize whitespace
            print(f"\n    Preview: {content}...")

        print()

    conn.close()

if __name__ == "__main__":
    main()
