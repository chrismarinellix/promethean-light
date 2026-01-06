"""Search for all pipeline-related information from the last 4 weeks"""

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

# Pipeline-related keywords
pipeline_keywords = [
    'pipeline', 'candidate', 'recruitment', 'hiring', 'interview',
    'offer', 'position', 'vacancy', 'applicant', 'shortlist',
    'onboard', 'resign', 'attrition', 'headcount', 'backfill',
    'cv', 'resume', 'job', 'role', 'talent', 'acquisition',
    'probation', 'start date', 'notice period', 'reference check'
]

print(f"\n{'='*100}")
print(f"PIPELINE INFORMATION - LAST 4 WEEKS (Since {four_weeks_ago})")
print(f"{'='*100}\n")

all_results = []
keyword_counts = defaultdict(int)

# Search for each keyword
for keyword in pipeline_keywords:
    rows = cur.execute(f"""
        SELECT created_at, source, raw_text
        FROM documents
        WHERE created_at >= '{four_weeks_ago}'
        AND LOWER(raw_text) LIKE '%{keyword.lower()}%'
        ORDER BY created_at DESC
    """).fetchall()

    if rows:
        keyword_counts[keyword] = len(rows)
        for row in rows:
            if row not in all_results:
                all_results.append(row)

# Sort by date descending
all_results.sort(key=lambda x: x[0], reverse=True)

print(f"KEYWORD SUMMARY:")
print(f"{'-'*100}")
for keyword, count in sorted(keyword_counts.items(), key=lambda x: x[1], reverse=True):
    if count > 0:
        print(f"  {keyword:20s}: {count:4d} mentions")
print(f"\nTOTAL DOCUMENTS FOUND: {len(all_results)}")
print(f"{'='*100}\n")

# Categorize and display results
categories = {
    'Candidates & Interviews': ['candidate', 'interview', 'applicant', 'shortlist', 'cv', 'resume'],
    'Hiring & Offers': ['offer', 'hiring', 'onboard', 'start date', 'reference check'],
    'Positions & Roles': ['position', 'vacancy', 'role', 'job', 'headcount', 'backfill'],
    'Resignations & Attrition': ['resign', 'attrition', 'notice period'],
    'General Pipeline': ['pipeline', 'recruitment', 'talent', 'acquisition', 'probation']
}

for category, keywords in categories.items():
    category_docs = []
    for date, source, text in all_results:
        text_lower = text.lower()
        if any(kw in text_lower for kw in keywords):
            if (date, source, text) not in category_docs:
                category_docs.append((date, source, text))

    if category_docs:
        print(f"\n{'*'*100}")
        print(f"{category.upper()} ({len(category_docs)} items)")
        print(f"{'*'*100}\n")

        for i, (date, source, text) in enumerate(category_docs[:20], 1):  # Limit to 20 per category
            # Extract subject if email
            subject = ""
            for line in text.split('\n'):
                if line.startswith('Subject:'):
                    subject = line.replace('Subject:', '').strip()[:100]
                    break

            print(f"[{i}] {date[:10]} | Source: {source[:30]}")
            if subject:
                print(f"    Subject: {subject}")

            # Show relevant excerpt (first 500 chars)
            preview = text[:500].replace('\n', ' ').strip()
            # Handle unicode encoding issues
            try:
                print(f"    Preview: {preview[:300]}...")
            except UnicodeEncodeError:
                # Fallback to ASCII-safe output
                safe_preview = preview[:300].encode('ascii', 'ignore').decode('ascii')
                print(f"    Preview: {safe_preview}...")
            print()

        if len(category_docs) > 20:
            print(f"    ... and {len(category_docs) - 20} more items in this category\n")

print(f"\n{'='*100}")
print(f"END OF PIPELINE SUMMARY")
print(f"{'='*100}\n")

conn.close()
