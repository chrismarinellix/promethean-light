"""Get detailed pipeline summary with specific people and actions"""

import sqlite3
from pathlib import Path
from datetime import datetime, timedelta
from collections import defaultdict

# Connect to database
db_path = Path.home() / ".mydata" / "mydata.db"
conn = sqlite3.connect(str(db_path))
cur = conn.cursor()

# Calculate 4 weeks ago
four_weeks_ago = (datetime.now() - timedelta(weeks=4)).strftime('%Y-%m-%d')

print(f"\n{'='*100}")
print(f"DETAILED PIPELINE ANALYSIS - LAST 4 WEEKS")
print(f"{'='*100}\n")

# 1. RESIGNATIONS
print("\n" + "*"*100)
print("1. RESIGNATIONS & ATTRITION")
print("*"*100 + "\n")

resign_rows = cur.execute(f"""
    SELECT created_at, raw_text
    FROM documents
    WHERE created_at >= '{four_weeks_ago}'
    AND (LOWER(raw_text) LIKE '%resignation%' OR LOWER(raw_text) LIKE '%resign%')
    AND source_type='email'
    ORDER BY created_at DESC
    LIMIT 30
""").fetchall()

people_resigning = set()
for date, text in resign_rows:
    if 'chirag' in text.lower() and 'resign' in text.lower():
        people_resigning.add("Chirag Rohit")
    if 'robby' in text.lower() and 'resign' in text.lower():
        people_resigning.add("Robby Palackal")

print(f"Recent Resignations Identified: {len(people_resigning)}")
for person in people_resigning:
    print(f"  - {person}")
print()

# 2. INTERVIEWS & CANDIDATES
print("\n" + "*"*100)
print("2. ACTIVE INTERVIEWS & CANDIDATES")
print("*"*100 + "\n")

interview_rows = cur.execute(f"""
    SELECT created_at, raw_text
    FROM documents
    WHERE created_at >= '{four_weeks_ago}'
    AND (LOWER(raw_text) LIKE '%interview%')
    AND source_type='email'
    ORDER BY created_at DESC
    LIMIT 20
""").fetchall()

candidates = set()
for date, text in interview_rows:
    if 'parisa ataeian' in text.lower():
        candidates.add("Parisa Ataeian - Senior Power System Engineer")
    if 'nick jatan' in text.lower():
        candidates.add("Nick Jatan")

print(f"Active Candidates/Interviews: {len(candidates)}")
for candidate in candidates:
    print(f"  - {candidate}")
print()

# 3. RETENTION EFFORTS
print("\n" + "*"*100)
print("3. RETENTION & COUNTER-OFFERS")
print("*"*100 + "\n")

retention_rows = cur.execute(f"""
    SELECT created_at, raw_text
    FROM documents
    WHERE created_at >= '{four_weeks_ago}'
    AND (LOWER(raw_text) LIKE '%retention%' OR LOWER(raw_text) LIKE '%counter%')
    AND source_type='email'
    ORDER BY created_at DESC
    LIMIT 20
""").fetchall()

retention_people = set()
for date, text in retention_rows:
    if 'ajith' in text.lower() and 'retention' in text.lower():
        retention_people.add("Ajith")
    if 'naveen' in text.lower() and 'retention' in text.lower():
        retention_people.add("Naveen")

print(f"Retention Efforts: {len(retention_people)}")
for person in retention_people:
    print(f"  - {person}")
print()

# 4. VISA APPLICATIONS (KEY INDICATOR OF HIRING)
print("\n" + "*"*100)
print("4. VISA APPLICATIONS (HIRING PIPELINE)")
print("*"*100 + "\n")

visa_rows = cur.execute(f"""
    SELECT created_at, raw_text
    FROM documents
    WHERE created_at >= '{four_weeks_ago}'
    AND (LOWER(raw_text) LIKE '%visa%' OR LOWER(raw_text) LIKE '%ens%' OR LOWER(raw_text) LIKE '%482%')
    AND source_type='email'
    ORDER BY created_at DESC
    LIMIT 15
""").fetchall()

visa_people = set()
for date, text in visa_rows:
    if 'komal' in text.lower():
        visa_people.add("Komal Gaikwad - ENS Visa Application")
    if 'dominic moncada' in text.lower():
        visa_people.add("Dominic Moncada - ENS Visa (subclass 186)")

print(f"Active Visa Applications: {len(visa_people)}")
for person in visa_people:
    print(f"  - {person}")
print()

# 5. REFERRAL PROGRAM
print("\n" + "*"*100)
print("5. RECRUITMENT & REFERRAL PROGRAM")
print("*"*100 + "\n")

referral_rows = cur.execute(f"""
    SELECT created_at, raw_text
    FROM documents
    WHERE created_at >= '{four_weeks_ago}'
    AND (LOWER(raw_text) LIKE '%referral%' OR LOWER(raw_text) LIKE '%hiring%')
    AND source_type='email'
    ORDER BY created_at DESC
    LIMIT 10
""").fetchall()

print(f"Referral Program Activity: {len(referral_rows)} related emails")
for date, text in referral_rows[:5]:
    subject = ""
    for line in text.split('\n')[:20]:
        if line.startswith('Subject:'):
            subject = line.replace('Subject:', '').strip()[:80]
            break
    if subject:
        try:
            print(f"  - {date[:10]}: {subject}")
        except UnicodeEncodeError:
            safe_subject = subject.encode('ascii', 'ignore').decode('ascii')
            print(f"  - {date[:10]}: {safe_subject}")
print()

# 6. HEADCOUNT & BUDGET
print("\n" + "*"*100)
print("6. HEADCOUNT & BUDGET DISCUSSIONS")
print("*"*100 + "\n")

budget_rows = cur.execute(f"""
    SELECT created_at, raw_text
    FROM documents
    WHERE created_at >= '{four_weeks_ago}'
    AND (LOWER(raw_text) LIKE '%headcount%' OR LOWER(raw_text) LIKE '%budget%' OR LOWER(raw_text) LIKE '%salary%')
    AND source_type='email'
    ORDER BY created_at DESC
    LIMIT 10
""").fetchall()

print(f"Budget/Headcount Discussions: {len(budget_rows)} emails")
for date, text in budget_rows[:5]:
    subject = ""
    for line in text.split('\n')[:20]:
        if line.startswith('Subject:'):
            subject = line.replace('Subject:', '').strip()[:80]
            break
    if subject:
        try:
            print(f"  - {date[:10]}: {subject}")
        except UnicodeEncodeError:
            safe_subject = subject.encode('ascii', 'ignore').decode('ascii')
            print(f"  - {date[:10]}: {safe_subject}")
print()

# 7. KEY ROLES MENTIONED
print("\n" + "*"*100)
print("7. KEY ROLES & POSITIONS MENTIONED")
print("*"*100 + "\n")

roles_count = {
    'Power System Engineer': 0,
    'Senior Engineer': 0,
    'Project Manager': 0,
    'Technical Lead': 0,
    'Graduate/Junior': 0
}

all_docs = cur.execute(f"""
    SELECT raw_text
    FROM documents
    WHERE created_at >= '{four_weeks_ago}'
    AND source_type='email'
""").fetchall()

for (text,) in all_docs:
    text_lower = text.lower()
    if 'power system engineer' in text_lower or 'power systems engineer' in text_lower:
        roles_count['Power System Engineer'] += 1
    if 'senior engineer' in text_lower or 'senior power' in text_lower:
        roles_count['Senior Engineer'] += 1
    if 'project manager' in text_lower or 'project management' in text_lower:
        roles_count['Project Manager'] += 1
    if 'technical lead' in text_lower or 'lead engineer' in text_lower:
        roles_count['Technical Lead'] += 1
    if 'graduate' in text_lower or 'junior' in text_lower:
        roles_count['Graduate/Junior'] += 1

print("Role mentions in emails:")
for role, count in sorted(roles_count.items(), key=lambda x: x[1], reverse=True):
    if count > 0:
        print(f"  {role:30s}: {count:4d} mentions")

print(f"\n{'='*100}")
print("END OF DETAILED ANALYSIS")
print(f"{'='*100}\n")

conn.close()
