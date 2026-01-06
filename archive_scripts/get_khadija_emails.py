import sqlite3
import sys
from pathlib import Path

# Ensure UTF-8 output
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

db_path = Path.home() / ".mydata" / "mydata.db"
conn = sqlite3.connect(str(db_path))
cur = conn.cursor()

# Search for Khadija mentions
results = cur.execute("""
    SELECT created_at, raw_text
    FROM documents
    WHERE source_type='email'
    AND (raw_text LIKE '%Khadija%' OR raw_text LIKE '%khadija%')
    ORDER BY created_at DESC
    LIMIT 20
""").fetchall()

print(f'\n{"="*100}')
print(f'Found {len(results)} emails mentioning Khadija')
print(f'{"="*100}\n')

for i, (date, text) in enumerate(results, 1):
    print(f'\n{"#"*100}')
    print(f'EMAIL {i} - DATE: {date}')
    print(f'{"#"*100}\n')
    print(text)
    print(f'\n{"="*100}\n')

conn.close()
