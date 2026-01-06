"""
Rebuild the vector database from all chunks in SQLite.
This syncs the Qdrant vector DB with the SQLite chunks table.

Run this if vector search isn't finding documents that exist in the database.
"""

import sys
import os

# Fix Windows console encoding for unicode characters
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

sys.path.insert(0, '.')

import time
from mydata.database import Database
from mydata.embedder import Embedder
from mydata.vectordb import VectorDB
from mydata.models import Chunk, Document
from sqlmodel import select


def main():
    print("=" * 60)
    print("Vector Database Rebuild Tool")
    print("=" * 60)

    # Initialize components
    print("\n[1/3] Initializing database...")
    db = Database()
    session = db.session()

    # Count chunks
    chunks = session.exec(select(Chunk)).all()
    total_chunks = len(chunks)
    print(f"  Found {total_chunks} chunks in SQLite")

    if total_chunks == 0:
        print("\n  No chunks to index. Run ingestion first.")
        return

    print("\n[2/3] Initializing embedder (loading ML model)...")
    start = time.time()
    embedder = Embedder()
    print(f"  Embedder ready ({time.time() - start:.1f}s)")

    print("\n[3/3] Initializing vector database...")
    vectordb = VectorDB()

    # Check current state
    try:
        vectordb.initialize(dimension=embedder.dimension)
        current_count = vectordb.count()
        print(f"  Current vector count: {current_count}")
    except Exception as e:
        print(f"  Error initializing: {e}")
        current_count = 0

    print("\n" + "=" * 60)
    print(f"Rebuilding vector index for {total_chunks} chunks...")
    print("=" * 60)

    # Process in batches
    batch_size = 50
    indexed = 0
    errors = 0
    start_time = time.time()

    for i in range(0, total_chunks, batch_size):
        batch = chunks[i:i + batch_size]

        for chunk in batch:
            try:
                # Get the chunk text
                text = chunk.text if hasattr(chunk, 'text') else chunk.content

                if not text or len(text.strip()) < 10:
                    continue

                # Get document source for metadata - use doc_id (correct attribute name)
                doc = session.get(Document, chunk.doc_id)
                source = doc.source if doc else "unknown"

                # Embed the text
                embedding = embedder.embed(text)

                # Upsert to vector DB
                vectordb.upsert(
                    id=str(chunk.id),
                    vector=embedding,
                    payload={
                        "text": text[:2000],  # Limit text size in payload
                        "source": source,
                        "doc_id": str(chunk.doc_id),
                        "start_offset": chunk.start_offset,
                        "end_offset": chunk.end_offset,
                    }
                )
                indexed += 1

            except Exception as e:
                errors += 1
                if errors <= 5:
                    print(f"  Error on chunk {chunk.id}: {e}")

        # Progress update
        elapsed = time.time() - start_time
        rate = indexed / elapsed if elapsed > 0 else 0
        eta = (total_chunks - indexed) / rate if rate > 0 else 0

        print(f"  Progress: {indexed}/{total_chunks} ({indexed*100//total_chunks}%) - {rate:.1f} chunks/sec - ETA: {eta:.0f}s")

    print("\n" + "=" * 60)
    print("Rebuild Complete!")
    print("=" * 60)

    # Final stats
    final_count = vectordb.count()
    elapsed = time.time() - start_time

    print(f"\n  Time: {elapsed:.1f} seconds")
    print(f"  Indexed: {indexed} chunks")
    print(f"  Errors: {errors}")
    print(f"  Vector DB count: {final_count}")

    if final_count < indexed:
        print(f"\n  Warning: Vector count ({final_count}) < indexed ({indexed})")
        print("  Some chunks may have been deduplicated or failed silently")


if __name__ == "__main__":
    main()
