"""Rebuild Qdrant collection for GritLM-7B (4096 dimensions)"""

import sys
import os
from pathlib import Path
from mydata.crypto import CryptoManager
from mydata.database import Database
from mydata.storage import EncryptedStorage
from mydata.embedder import Embedder
from mydata.vectordb import VectorDB
from mydata.models import Document, Chunk
from sqlmodel import select
import getpass

def main():
    print("\n" + "="*60)
    print("REBUILD QDRANT FOR GRITLM-7B (4096 DIMENSIONS)")
    print("="*60)
    print("\nThis will:")
    print("  1. Delete the existing 768-dim Qdrant collection")
    print("  2. Create a new 4096-dim collection for GritLM-7B")
    print("  3. Re-embed all existing documents")
    print("\nWARNING: This will take time depending on document count!")
    print("         GritLM-7B is larger and slower than bge-base-en-v1.5")

    # Check for --yes flag
    if "--yes" not in sys.argv:
        response = input("\nContinue? (yes/no): ").strip().lower()
        if response != "yes":
            print("Aborted.")
            sys.exit(0)
    else:
        print("\n✓ Auto-confirmed with --yes flag")

    # Get passphrase
    print("\n" + "="*60)
    passphrase = os.environ.get("MYDATA_PASSPHRASE")
    if not passphrase:
        passphrase = getpass.getpass("Master passphrase: ")

    try:
        # Initialize services
        print("\n✓ Unlocking crypto...")
        crypto = CryptoManager(passphrase)

        print("✓ Opening database...")
        db = Database()
        storage = EncryptedStorage(crypto)

        print("✓ Loading GritLM-7B model...")
        embedder = Embedder(model_name="GritLM/GritLM-7B")

        # Verify dimension
        dim = embedder.dimension
        print(f"✓ Model dimension: {dim}")

        if dim != 4096:
            print(f"\n⚠ ERROR: Expected 4096 dimensions, got {dim}")
            sys.exit(1)

        # Delete old collection
        print("\n" + "="*60)
        print("STEP 1: Deleting old Qdrant collection...")
        print("="*60)

        vectordb = VectorDB()
        try:
            vectordb.client.delete_collection("documents")
            print("✓ Old collection deleted")
        except Exception as e:
            print(f"ℹ No existing collection (this is OK): {e}")

        # Create new collection
        print("\n" + "="*60)
        print("STEP 2: Creating new 4096-dim collection...")
        print("="*60)

        vectordb.initialize(dimension=4096)
        print("✓ New collection created")

        # Re-embed all documents
        print("\n" + "="*60)
        print("STEP 3: Re-embedding all documents...")
        print("="*60)

        session = db.session()

        # Get all chunks
        chunks = session.exec(select(Chunk)).all()
        total_chunks = len(chunks)

        if total_chunks == 0:
            print("ℹ No chunks to process")
            return

        print(f"\nFound {total_chunks:,} chunks to re-embed")

        # Process in batches
        batch_size = 32
        processed = 0

        for i in range(0, total_chunks, batch_size):
            batch = chunks[i:i+batch_size]

            # Get texts
            texts = [chunk.text for chunk in batch]

            # Generate embeddings
            embeddings = embedder.embed_batch(texts, batch_size=len(texts))

            # Upsert to Qdrant
            chunk_ids = [chunk.id for chunk in batch]
            payloads = [{"doc_id": str(chunk.doc_id)} for chunk in batch]

            vectordb.upsert_batch(chunk_ids, embeddings, payloads)

            processed += len(batch)
            pct = (processed / total_chunks) * 100
            print(f"  Progress: {processed:,}/{total_chunks:,} ({pct:.1f}%)")

        print("\n✓ Re-embedding complete!")

        # Verify
        print("\n" + "="*60)
        print("VERIFICATION")
        print("="*60)

        vector_count = vectordb.count()
        print(f"✓ Vectors in Qdrant: {vector_count:,}")
        print(f"✓ Chunks in database: {total_chunks:,}")

        if vector_count == total_chunks:
            print("\n✅ SUCCESS! Database rebuilt successfully.")
            print("\nYou can now start the daemon with: python -m mydata daemon")
        else:
            print(f"\n⚠ WARNING: Mismatch - {vector_count} vectors vs {total_chunks} chunks")

    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
