"""Reset Qdrant collection to fix dimension mismatch"""

import sys
from mydata.vectordb import VectorDB
from mydata.embedder import Embedder

# Fix encoding for Windows console
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')


def reset_collection():
    """Delete and recreate Qdrant collection with correct dimensions"""

    print("Loading embedding model...")
    embedder = Embedder()
    print(f"✓ Model loaded: {embedder.dimension} dimensions\n")

    vectordb = VectorDB()

    print("Checking Qdrant collection status...")
    try:
        count = vectordb.count()
        print(f"Current collection has {count} vectors\n")
    except Exception as e:
        print(f"Error checking collection: {e}\n")

    # Ask for confirmation
    response = input("⚠ This will DELETE all vectors and reinitialize the collection.\nContinue? (yes/no): ")

    if response.lower() != "yes":
        print("Aborted.")
        return

    print("\nDeleting collection...")
    try:
        vectordb.client.delete_collection("documents")
        print("✓ Collection deleted")
    except Exception as e:
        print(f"Note: {e}")

    print(f"\nReinitializing collection with {embedder.dimension} dimensions...")
    vectordb.initialize(dimension=embedder.dimension)
    print("✓ Collection reinitialized")

    count = vectordb.count()
    print(f"✓ New collection ready (0 vectors)")

    print("\n" + "="*60)
    print("NEXT STEPS:")
    print("="*60)
    print("1. Restart the daemon to re-ingest emails from Outlook")
    print("2. The daemon will automatically re-embed all new content")
    print("3. Old documents in SQLite are still accessible")
    print("4. Only the vector embeddings have been cleared")
    print("="*60)


if __name__ == "__main__":
    reset_collection()
