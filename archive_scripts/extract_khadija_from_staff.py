import sqlite3
import sys
from pathlib import Path

# Ensure UTF-8 output
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

db_path = Path.home() / ".mydata" / "mydata.db"
conn = sqlite3.connect(str(db_path))
cur = conn.cursor()

# Get the Staff.txt file using LIKE to avoid escaping issues
staff_file = cur.execute("""
    SELECT raw_text
    FROM documents
    WHERE source LIKE '%Staff.txt'
""").fetchone()

if staff_file:
    content = staff_file[0]

    # Split into lines and find Khadija section
    lines = content.split('\n')

    print('\n' + '='*100)
    print('KHADIJA INFORMATION FROM STAFF.TXT FILE')
    print('='*100 + '\n')

    # Find all mentions of Khadija
    for i, line in enumerate(lines):
        if 'khadija' in line.lower():
            # Print context around Khadija mentions (5 lines before, 15 lines after)
            start = max(0, i-5)
            end = min(len(lines), i+20)
            print(f'\n{"#"*100}')
            print(f'FOUND KHADIJA MENTION AT LINE {i}')
            print(f'{"#"*100}\n')
            for j in range(start, end):
                marker = ' >>> ' if j == i else '     '
                print(f'{marker}{lines[j]}')
            print('\n')
else:
    print('Staff.txt file not found in database')

conn.close()
