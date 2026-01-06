import sqlite3
import sys
from pathlib import Path

# Ensure UTF-8 output
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

db_path = Path.home() / ".mydata" / "mydata.db"
conn = sqlite3.connect(str(db_path))
cur = conn.cursor()

# Search for Khadija with pay/salary/progression related terms
print("\n" + "="*100)
print("SEARCHING FOR KHADIJA + PAY/SALARY/PROGRESSION/ROLE/TRAINING RELATED EMAILS")
print("="*100 + "\n")

results = cur.execute("""
    SELECT created_at, raw_text
    FROM documents
    WHERE source_type='email'
    AND raw_text LIKE '%Khadija%'
    AND (
        raw_text LIKE '%pay%'
        OR raw_text LIKE '%salary%'
        OR raw_text LIKE '%progression%'
        OR raw_text LIKE '%role%'
        OR raw_text LIKE '%training%'
        OR raw_text LIKE '%promotion%'
        OR raw_text LIKE '%increase%'
        OR raw_text LIKE '%raise%'
        OR raw_text LIKE '%career%'
        OR raw_text LIKE '%clarity%'
        OR raw_text LIKE '%development%'
    )
    ORDER BY created_at DESC
    LIMIT 10
""").fetchall()

print(f'Found {len(results)} relevant emails\n')

for i, (date, text) in enumerate(results, 1):
    print(f'\n{"#"*100}')
    print(f'EMAIL {i} - DATE: {date}')
    print(f'{"#"*100}\n')
    print(text)
    print(f'\n{"="*100}\n')

# Also search for emails FROM or TO Khadija specifically
print("\n" + "="*100)
print("SEARCHING FOR EMAILS FROM/TO KHADIJA DIRECTLY")
print("="*100 + "\n")

direct_emails = cur.execute("""
    SELECT created_at, raw_text
    FROM documents
    WHERE source_type='email'
    AND (
        source LIKE '%khadija%'
        OR source LIKE '%Khadija%'
        OR raw_text LIKE 'From: Khadija%'
        OR raw_text LIKE '%To: Khadija%'
        OR raw_text LIKE '%khadija.kobra%'
        OR raw_text LIKE '%khadija.Kobra%'
    )
    ORDER BY created_at DESC
    LIMIT 15
""").fetchall()

print(f'Found {len(direct_emails)} direct emails\n')

for i, (date, text) in enumerate(direct_emails, 1):
    print(f'\n{"#"*100}')
    print(f'DIRECT EMAIL {i} - DATE: {date}')
    print(f'{"#"*100}\n')
    # Show first 5000 chars
    print(text[:5000])
    if len(text) > 5000:
        print("\n... [TRUNCATED] ...\n")
    print(f'\n{"="*100}\n')

conn.close()
