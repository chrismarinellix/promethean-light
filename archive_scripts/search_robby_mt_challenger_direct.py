#!/usr/bin/env python3
"""Direct database search for emails from Robby about Mt Challenger"""

import sqlite3
from pathlib import Path

def main():
    db_path = Path(__file__).parent / "mydata" / "mydata.db"

    if not db_path.exists():
        print(f"Database not found at: {db_path}")
        return

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Search for emails from Robby mentioning Mt Challenger or Challenger
    print("Searching for emails from Robby about Mt Challenger...\n")

    # First, let's see what tables we have
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cursor.fetchall()
    print("Available tables:", [t[0] for t in tables])
    print()

    # Check total document count first
    cursor.execute("SELECT COUNT(*) FROM documents")
    total_docs = cursor.fetchone()[0]
    print(f"Total documents in database: {total_docs}\n")

    # Search in documents table (emails are stored here)
    # First try with Mt Challenger or Challenger filter
    query = """
        SELECT id, source, raw_text, created_at
        FROM documents
        WHERE (raw_text LIKE '%robby%' OR raw_text LIKE '%Robby%')
          AND (raw_text LIKE '%Mt Challenger%' OR raw_text LIKE '%Mt. Challenger%'
               OR raw_text LIKE '%Challenger%')
        ORDER BY created_at DESC
        LIMIT 50
    """

    try:
        cursor.execute(query)
        results = cursor.fetchall()

        if not results:
            print("No documents found from Robby about Mt Challenger.")

            # Try a broader search - just mentioning Robby
            print("\nSearching for any documents mentioning Robby...\n")
            cursor.execute("""
                SELECT id, source, raw_text, created_at
                FROM documents
                WHERE raw_text LIKE '%robby%' OR raw_text LIKE '%Robby%'
                ORDER BY created_at DESC
                LIMIT 20
            """)
            results = cursor.fetchall()

            if not results:
                print("No documents found mentioning Robby at all.")
                conn.close()
                return

        print(f"Found {len(results)} document(s):\n")
        print("=" * 80)

        for i, (doc_id, source, text, created_at) in enumerate(results, 1):
            print(f"\n{i}. Document ID: {doc_id}")
            print(f"   Source: {source or 'Unknown'}")
            print(f"   Created: {created_at or 'Unknown'}")

            # Try to extract email metadata from text
            lines = text.split('\n') if text else []
            subject = None
            sender = None
            date = None

            for line in lines[:20]:  # Check first 20 lines for metadata
                if line.startswith('Subject:'):
                    subject = line[8:].strip()
                elif line.startswith('From:'):
                    sender = line[5:].strip()
                elif line.startswith('Date:'):
                    date = line[5:].strip()

            if subject:
                print(f"   Subject: {subject}")
            if sender:
                print(f"   From: {sender}")
            if date:
                print(f"   Date: {date}")

            # Show preview of content
            if text:
                # Look for Mt Challenger mentions
                text_lower = text.lower()
                if 'challenger' in text_lower:
                    # Find the section with Challenger
                    idx = text_lower.find('challenger')
                    start = max(0, idx - 200)
                    end = min(len(text), idx + 200)
                    preview = text[start:end].replace('\n', ' ').replace('\r', '')
                    print(f"\n   ...{preview}...")
                else:
                    preview = text[:400].replace('\n', ' ').replace('\r', '')
                    print(f"\n   Preview: {preview}...")

            print("-" * 80)

    except sqlite3.Error as e:
        print(f"Database error: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    main()
