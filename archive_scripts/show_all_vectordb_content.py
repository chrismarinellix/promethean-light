"""Display all content in vector database"""

from pathlib import Path
from qdrant_client import QdrantClient
import sys

# Set UTF-8 encoding for Windows console
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')

qdrant_path = Path.home() / '.mydata' / 'qdrant'
client = QdrantClient(path=str(qdrant_path))

records, _ = client.scroll(
    collection_name='documents',
    limit=100,
    with_payload=True
)

print(f"Total documents in vector DB: {len(records)}\n")
print("="*100)

for i, r in enumerate(records, 1):
    source = r.payload.get('source', 'unknown')
    text = r.payload.get('text', 'no text')

    print(f"\n[{i}] Source: {source}")
    print(f"Text ({len(text)} chars):")
    print(text)
    print("-"*100)
