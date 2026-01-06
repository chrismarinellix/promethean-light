#!/usr/bin/env python3
"""Check database schema"""

import sqlite3
from pathlib import Path

def main():
    db_path = Path(__file__).parent / "mydata" / "mydata.db"
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Get all tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cursor.fetchall()

    for table_name in [t[0] for t in tables]:
        print(f"\nTable: {table_name}")
        print("=" * 80)
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = cursor.fetchall()
        for col in columns:
            print(f"  {col[1]} ({col[2]})")

    # Also show a sample row from documents table
    print("\n\nSample from documents table:")
    print("=" * 80)
    cursor.execute("SELECT * FROM documents LIMIT 1")
    row = cursor.fetchone()
    if row:
        cursor.execute("PRAGMA table_info(documents)")
        columns = [col[1] for col in cursor.fetchall()]
        for col, val in zip(columns, row):
            print(f"{col}: {str(val)[:100]}")

    conn.close()

if __name__ == "__main__":
    main()
