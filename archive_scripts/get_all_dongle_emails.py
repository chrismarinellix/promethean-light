"""Get all dongle-related email content"""
import sys
sys.path.insert(0, '.')
from mydata.database import Database
from mydata.config import Config
from mydata.models import Document

db = Database(Config.DATABASE_PATH)
session = db.get_session()

# Query for emails containing 'dongle'
docs = session.query(Document).filter(
    Document.source_type == 'email',
    Document.raw_text.ilike('%dongle%')
).order_by(Document.created_at.desc()).all()

print(f"Found {len(docs)} dongle-related emails\n")
print("=" * 100)

for i, doc in enumerate(docs, 1):
    print(f"\n[EMAIL #{i}]")
    print(f"Date: {doc.created_at}")
    print(f"Source: {doc.source}")
    print("=" * 100)

    # Extract subject and key content
    lines = doc.raw_text.split('\n')

    # Print first 200 lines to capture the full email
    for line in lines[:200]:
        print(line)

    print("\n" + "=" * 100)
    print("\n")
