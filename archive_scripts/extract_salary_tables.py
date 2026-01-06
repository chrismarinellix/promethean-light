import sqlite3
import sys
import re
from pathlib import Path

# Ensure UTF-8 output
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

db_path = Path.home() / ".mydata" / "mydata.db"
conn = sqlite3.connect(str(db_path))
cur = conn.cursor()

# Get the Staff.txt file
staff_file = cur.execute("""
    SELECT raw_text
    FROM documents
    WHERE source LIKE '%Staff.txt'
""").fetchone()

if staff_file:
    content = staff_file[0]
    lines = content.split('\n')

    print('\n' + '='*150)
    print('EXTRACTING KEY SALARY DATA AND NOTES')
    print('='*150 + '\n')

    # Find the main salary table sections
    capturing = False
    for i, line in enumerate(lines):
        # Look for salary table headers or key salary data
        if any(keyword in line for keyword in ['staff wages Employee', 'Employee ID', 'Valid From', 'BASE SALARY',
                                                'Bonus', 'RETENTION', 'Golden', 'momtaz', 'khadija', 'hayden',
                                                'ajith', 'naveen', 'robby']):
            # Print context
            start = max(0, i-2)
            end = min(len(lines), i+25)

            print(f'\n{"="*150}')
            print(f'SECTION STARTING AT LINE {i}')
            print(f'{"="*150}')

            for j in range(start, end):
                print(lines[j])
            print('\n')

conn.close()
