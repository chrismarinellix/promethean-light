import sqlite3
import sys
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

    print('\n' + '='*150)
    print('FULL STAFF.TXT CONTENT - SEARCHING FOR ALL SALARY, BONUS, AND PERFORMANCE DATA')
    print('='*150 + '\n')

    # Print the entire file - it should have all the info
    print(content)
else:
    print('Staff.txt file not found')

conn.close()
