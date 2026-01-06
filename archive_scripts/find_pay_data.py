import sqlite3
import sys
from pathlib import Path

# Ensure UTF-8 output
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

db_path = Path.home() / ".mydata" / "mydata.db"
conn = sqlite3.connect(str(db_path))
cur = conn.cursor()

print('\n' + '='*100)
print('SEARCHING ALL DOCUMENTS FOR PAY/SALARY DATA')
print('='*100 + '\n')

# First, let's see what document types we have
types = cur.execute("""
    SELECT DISTINCT source_type, COUNT(*)
    FROM documents
    GROUP BY source_type
""").fetchall()

print('Document types in database:')
for dtype, count in types:
    print(f'  - {dtype}: {count} documents')

print('\n' + '='*100)
print('SEARCHING FOR DOCUMENTS WITH KHADIJA NAME')
print('='*100 + '\n')

# Search specifically for Khadija in all documents
khadija_docs = cur.execute("""
    SELECT created_at, source_type, source, raw_text
    FROM documents
    WHERE raw_text LIKE '%Khadija%'
    ORDER BY created_at DESC
    LIMIT 25
""").fetchall()

print(f'Found {len(khadija_docs)} documents mentioning Khadija\n')

for i, (date, stype, source, text) in enumerate(khadija_docs, 1):
    print(f'\n{"#"*100}')
    print(f'DOC {i} - DATE: {date} - TYPE: {stype}')
    print(f'SOURCE: {source[:150] if len(source) > 150 else source}')
    print(f'{"#"*100}\n')

    # Show first 4000 chars
    preview = text[:4000]
    print(preview)
    if len(text) > 4000:
        print('\n... [TRUNCATED] ...\n')
    print(f'\n{"="*100}\n')

print('\n' + '='*100)
print('NOW SEARCHING FOR STAFF/SALARY/BUDGET FILES')
print('='*100 + '\n')

# Search for staff/salary files by source name
staff_files = cur.execute("""
    SELECT created_at, source_type, source, substr(raw_text, 1, 5000) as preview
    FROM documents
    WHERE source LIKE '%staff%'
    OR source LIKE '%Staff%'
    OR source LIKE '%salary%'
    OR source LIKE '%Salary%'
    OR source LIKE '%budget%'
    OR source LIKE '%Budget%'
    OR source LIKE '%APAC%'
    OR source LIKE '%pay%'
    ORDER BY created_at DESC
    LIMIT 10
""").fetchall()

print(f'Found {len(staff_files)} staff/salary/budget files\n')

for i, (date, stype, source, preview) in enumerate(staff_files, 1):
    print(f'\n{"#"*100}')
    print(f'FILE {i} - DATE: {date} - TYPE: {stype}')
    print(f'SOURCE: {source}')
    print(f'{"#"*100}\n')
    print(preview)
    print(f'\n{"="*100}\n')

conn.close()
