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
print('SEARCHING FOR ALL MENTIONS OF ED / EDUARDO LAYGO')
print('='*100 + '\n')

# Search for Ed/Eduardo mentions in all documents
results = cur.execute("""
    SELECT created_at, source_type, source, raw_text
    FROM documents
    WHERE raw_text LIKE '%Ed Laygo%'
    OR raw_text LIKE '%Eduardo%'
    OR raw_text LIKE '%ed.laygo%'
    ORDER BY created_at DESC
    LIMIT 30
""").fetchall()

print(f'Found {len(results)} documents mentioning Ed/Eduardo\n')

for i, (date, stype, source, text) in enumerate(results, 1):
    print(f'\n{"#"*100}')
    print(f'DOCUMENT {i} - DATE: {date} - TYPE: {stype}')
    print(f'SOURCE: {source[:120] if len(source) > 120 else source}')
    print(f'{"#"*100}\n')

    # Show context around Ed mentions
    lines = text.split('\n')
    for j, line in enumerate(lines):
        if 'ed laygo' in line.lower() or 'eduardo' in line.lower():
            # Print context
            start = max(0, j-3)
            end = min(len(lines), j+8)
            for k in range(start, end):
                marker = ' >>> ' if k == j else '     '
                print(f'{marker}{lines[k]}')
            print('\n---\n')
            break

    print(f'\n{"="*100}\n')

conn.close()
