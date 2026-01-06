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
print('SEARCH: Khadija + HR/Salary/Compensation/Performance Terms')
print('='*100 + '\n')

# Search for any documents about Khadija with HR/compensation terms
results = cur.execute("""
    SELECT created_at, source_type, source, raw_text
    FROM documents
    WHERE raw_text LIKE '%Khadija%'
    AND (
        raw_text LIKE '%HR%'
        OR raw_text LIKE '%javed%'
        OR raw_text LIKE '%Javed%'
        OR raw_text LIKE '%gitanjali%'
        OR raw_text LIKE '%Gitanjali%'
        OR raw_text LIKE '%annual review%'
        OR raw_text LIKE '%performance%'
        OR raw_text LIKE '%appraisal%'
        OR raw_text LIKE '%$ %'
        OR raw_text LIKE '%AUD%'
        OR raw_text LIKE '%compensation%'
        OR raw_text LIKE '%Power System Engineer%'
        OR raw_text LIKE '%Senior Engineer%'
        OR raw_text LIKE '%grade%'
        OR raw_text LIKE '%level%'
        OR raw_text LIKE '%MIEAust%'
        OR raw_text LIKE '%title%'
    )
    ORDER BY created_at DESC
    LIMIT 15
""").fetchall()

print(f'Found {len(results)} documents\n')

for i, (date, stype, source, text) in enumerate(results, 1):
    print(f'\n{"#"*100}')
    print(f'DOCUMENT {i} - DATE: {date} - TYPE: {stype}')
    print(f'SOURCE: {source[:100] if len(source) > 100 else source}')
    print(f'{"#"*100}\n')
    # Show first 6000 chars
    preview = text[:6000]
    print(preview)
    if len(text) > 6000:
        print('\n... [CONTENT TRUNCATED] ...\n')
    print(f'\n{"="*100}\n')

conn.close()
