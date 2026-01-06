"""Search for Dimitri's email about dongles"""
import sys
sys.path.insert(0, '.')
from mydata.database import Database
from mydata.config import Config
from sqlmodel import select
from mydata.models import Document

db = Database(Config.DATABASE_PATH)
session = db.get_session()

# Find documents about PSSE dongle licenses mentioning Dimitri
results = session.query(Document).filter(
    Document.raw_text.like('%Dimitri%'),
    Document.raw_text.like('%dongle%')
).all()

for doc in results:
    print('=' * 80)
    print(f'Source: {doc.source}')
    print(f'Date: {doc.created_at}')
    print('=' * 80)
    print(doc.raw_text[:3000])  # First 3000 chars
    print('\n\n')
