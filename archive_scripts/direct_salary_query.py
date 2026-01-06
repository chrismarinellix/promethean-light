import sqlite3
import os

# Connect to the database
db_path = r"C:\Code\Promethian  Light\mydata\mydata.db"
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Search for documents related to salary reviews
print("Searching for salary review related documents...")
print("="*80)

# Query documents with salary-related keywords
query = """
SELECT id, title, content, source, created_at
FROM documents
WHERE (
    lower(content) LIKE '%salary review%' OR
    lower(content) LIKE '%compensation review%' OR
    lower(content) LIKE '%reviewed%salary%' OR
    lower(content) LIKE '%pending%review%' OR
    lower(title) LIKE '%salary%' OR
    lower(title) LIKE '%compensation%'
)
ORDER BY created_at DESC
LIMIT 30
"""

cursor.execute(query)
rows = cursor.fetchall()

print(f"\nFound {len(rows)} documents\n")

for row in rows:
    doc_id, title, content, source, created_at = row
    print(f"\nDocument: {title}")
    print(f"Source: {source}")
    print(f"Created: {created_at}")

    # Show relevant excerpts
    content_lower = content.lower()
    if 'review' in content_lower and 'salary' in content_lower:
        # Try to extract relevant portions
        lines = content.split('\n')
        relevant_lines = [line for line in lines if 'review' in line.lower() or 'salary' in line.lower() or 'compensation' in line.lower()]
        if relevant_lines:
            print("Relevant excerpts:")
            for line in relevant_lines[:10]:  # Show first 10 relevant lines
                print(f"  - {line.strip()[:150]}")
    print("-"*80)

conn.close()
