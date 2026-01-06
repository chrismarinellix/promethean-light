import sqlite3
from pathlib import Path
from collections import Counter

db_path = Path.home() / ".mydata" / "mydata.db"
conn = sqlite3.connect(str(db_path))
cur = conn.cursor()

# Get emails from last 30 days
rows = cur.execute("""
    SELECT id, source, created_at, raw_text
    FROM documents
    WHERE source_type='email'
    AND datetime(created_at) > datetime('now', '-30 days')
""").fetchall()

print(f"\nTotal emails in last 30 days: {len(rows)}\n")

# Count keyword matches
urgent_keywords = ["deadline", "due", "asap", "urgent", "eod", "eow", "immediately", "priority"]
keyword_counts = Counter()
keyword_examples = {kw: [] for kw in urgent_keywords}

for row in rows:
    email_id, source, created_at, raw_text = row
    text_lower = raw_text.lower()

    for keyword in urgent_keywords:
        if keyword in text_lower:
            keyword_counts[keyword] += 1

            # Get context around keyword (first occurrence only)
            if len(keyword_examples[keyword]) < 3:  # Keep 3 examples per keyword
                idx = text_lower.find(keyword)
                start = max(0, idx - 60)
                end = min(len(raw_text), idx + 80)
                context = raw_text[start:end].replace('\n', ' ')

                # Extract subject
                subject = ""
                for line in raw_text.split('\n'):
                    if line.startswith('Subject:'):
                        subject = line.replace('Subject:', '').strip()[:50]
                        break

                keyword_examples[keyword].append({
                    'subject': subject,
                    'context': context
                })

# Show results
print("="*100)
print("KEYWORD MATCH ANALYSIS")
print("="*100)

for keyword, count in keyword_counts.most_common():
    print(f"\n'{keyword}': {count} matches")
    print("-" * 100)

    for i, example in enumerate(keyword_examples[keyword][:3], 1):
        print(f"  Example {i}: {example['subject']}")
        print(f"  Context: ...{example['context']}...")
        print()

# Check for false positives
print("\n" + "="*100)
print("CHECKING FOR FALSE POSITIVES")
print("="*100)

false_positive_patterns = [
    "not urgent",
    "no urgent",
    "isn't urgent",
    "is not urgent",
    "no deadline",
    "please reach out only for urgent matters",  # Auto-reply pattern
]

false_positives = 0
for row in rows:
    text_lower = row[3].lower()
    for pattern in false_positive_patterns:
        if pattern in text_lower:
            false_positives += 1
            break

print(f"\nEmails containing false positive patterns: {false_positives}")
print(f"Likely TRUE urgent emails: ~{len([r for r in rows if any(kw in r[3].lower() for kw in urgent_keywords)]) - false_positives}")

conn.close()
