"""Query Qdrant directly for salary review information"""
from pathlib import Path
from qdrant_client import QdrantClient
import sys

# Connect to Qdrant
qdrant_path = Path.home() / ".mydata" / "qdrant"
if not qdrant_path.exists():
    print(f"Qdrant path does not exist: {qdrant_path}")
    sys.exit(1)

try:
    client = QdrantClient(path=str(qdrant_path))

    # Get collection info
    collections = client.get_collections().collections
    print(f"Found {len(collections)} collections:")
    for col in collections:
        print(f"  - {col.name} ({col.vectors_count} vectors)")

    if not collections:
        print("No collections found!")
        sys.exit(1)

    # Use the first collection (should be 'documents')
    collection_name = collections[0].name

    # Scroll through all points to find salary review related content
    print(f"\n{'='*80}")
    print(f"Searching for salary review mentions in '{collection_name}'...")
    print('='*80)

    offset = None
    batch_size = 100
    found_docs = []

    while True:
        results, next_offset = client.scroll(
            collection_name=collection_name,
            limit=batch_size,
            offset=offset,
            with_payload=True,
            with_vectors=False
        )

        if not results:
            break

        for point in results:
            payload = point.payload
            text = payload.get('text', '').lower()

            # Look for salary review keywords
            if any(keyword in text for keyword in [
                'salary review', 'reviewed', 'compensation review',
                'performance review', 'pay review', 'reviewed salary'
            ]):
                found_docs.append({
                    'id': point.id,
                    'text': payload.get('text', ''),
                    'source': payload.get('source', 'Unknown'),
                    'created_at': payload.get('created_at', 'Unknown')
                })

        offset = next_offset
        if offset is None:
            break

    print(f"\nFound {len(found_docs)} documents mentioning salary reviews\n")

    # Group by source type
    emails = [d for d in found_docs if 'email' in d['source'].lower()]
    files = [d for d in found_docs if 'file' in d['source'].lower()]
    other = [d for d in found_docs if d not in emails and d not in files]

    print(f"Emails: {len(emails)}")
    print(f"Files: {len(files)}")
    print(f"Other: {len(other)}")
    print()

    # Display findings
    for i, doc in enumerate(found_docs[:20], 1):  # Show first 20
        print(f"\n{i}. Source: {doc['source']}")
        print(f"   Created: {doc['created_at']}")

        # Extract relevant lines
        lines = doc['text'].split('\n')
        relevant = [
            line.strip() for line in lines
            if any(kw in line.lower() for kw in [
                'salary review', 'reviewed', 'compensation',
                'pay review', 'performance review'
            ])
        ]

        if relevant:
            print("   Relevant excerpts:")
            for line in relevant[:5]:  # Show first 5 relevant lines
                if line:
                    print(f"     • {line[:120]}")
        print("-" * 80)

    if len(found_docs) > 20:
        print(f"\n... and {len(found_docs) - 20} more documents")

except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
