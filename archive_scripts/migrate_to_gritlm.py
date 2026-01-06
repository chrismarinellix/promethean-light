"""Migration script to upgrade to GritLM-7B embeddings"""

import shutil
from pathlib import Path
from datetime import datetime
import sys


def migrate_to_gritlm():
    """Migrate from old embedding model to GritLM-7B"""

    print("=" * 80)
    print("  PROMETHEAN LIGHT - EMBEDDING MODEL UPGRADE")
    print("=" * 80)
    print()
    print("  Upgrading to: GritLM-7B (4096-dimensional embeddings)")
    print("  This will provide STATE-OF-THE-ART search quality!")
    print()
    print("=" * 80)
    print()

    mydata_dir = Path.home() / ".mydata"

    if not mydata_dir.exists():
        print("[ERROR] .mydata directory not found!")
        print("        Please run 'python -m mydata setup' first.")
        sys.exit(1)

    # Paths
    qdrant_dir = mydata_dir / "qdrant"
    db_file = mydata_dir / "mydata.db"
    backup_dir = mydata_dir / "backups" / f"pre_gritlm_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

    print("[STEP 1/4] Creating backup...")
    backup_dir.mkdir(parents=True, exist_ok=True)

    # Backup database
    if db_file.exists():
        print(f"  - Backing up database: {db_file.name}")
        shutil.copy2(db_file, backup_dir / "mydata.db")
        print("    [OK] Database backed up")

    # Backup vector DB (optional - can be large)
    if qdrant_dir.exists():
        print(f"  - Vector DB found: {qdrant_dir}")
        print("    (Not backing up - will be rebuilt with new embeddings)")

    print()

    print("[STEP 2/4] Removing old vector database...")
    if qdrant_dir.exists():
        try:
            # Windows: sometimes Qdrant locks files, try to remove lock first
            lock_file = qdrant_dir / ".lock"
            if lock_file.exists():
                try:
                    lock_file.unlink()
                except:
                    pass

            shutil.rmtree(qdrant_dir)
            print("  [OK] Old vector database removed")
        except Exception as e:
            print(f"  [WARNING] Could not remove vector DB: {e}")
            print("  [ACTION REQUIRED] Please:")
            print("    1. Stop any running Promethean Light daemons")
            print("    2. Manually delete: %USERPROFILE%\\.mydata\\qdrant")
            print("    3. Re-run this script")
            sys.exit(1)
    else:
        print("  [INFO] No existing vector database found")

    print()

    print("[STEP 3/4] Downloading GritLM-7B model...")
    print("  NOTE: This is a 7B parameter model (~14GB download)")
    print("        First-time download will take 10-30 minutes depending on connection")
    print()
    print("  Starting download...")

    try:
        from mydata.embedder import Embedder

        # This will trigger model download
        embedder = Embedder()  # Now defaults to GritLM-7B
        dimension = embedder.dimension

        print(f"  [OK] Model loaded successfully ({dimension} dimensions)")

        if dimension != 4096:
            print(f"  [WARNING] Expected 4096 dimensions, got {dimension}")
            print("            Model may not be GritLM-7B")

    except Exception as e:
        print(f"  [ERROR] Failed to load model: {e}")
        print()
        print("  Possible solutions:")
        print("    1. Check internet connection")
        print("    2. Ensure you have 16GB+ free disk space")
        print("    3. Try: pip install --upgrade sentence-transformers torch")
        sys.exit(1)

    print()

    print("[STEP 4/4] Rebuilding vector database...")
    print("  This will re-embed all your documents with GritLM-7B")
    print()

    # Re-initialize vector DB
    from mydata.vectordb import VectorDB
    from mydata.crypto import CryptoManager
    from mydata.database import Database
    from mydata.models import Document, Chunk
    from sqlmodel import select
    import getpass

    # Get passphrase
    passphrase = getpass.getpass("  Enter your master passphrase: ")

    try:
        crypto = CryptoManager(passphrase)
        db = Database()
        vectordb = VectorDB()
        vectordb.initialize(dimension=4096)

        # Get all chunks
        session = db.session()
        chunks = session.exec(select(Chunk)).all()

        if not chunks:
            print("  [INFO] No existing chunks found - database is empty")
            print("  [OK] Migration complete! Start daemon to begin ingesting documents.")
        else:
            print(f"  [INFO] Found {len(chunks)} chunks to re-embed")
            print("  [INFO] This will take a while with GritLM-7B...")
            print()

            # Re-embed in batches
            batch_size = 16  # Smaller batches for large model
            total = len(chunks)

            for i in range(0, total, batch_size):
                batch = chunks[i:i+batch_size]
                batch_num = (i // batch_size) + 1
                total_batches = (total + batch_size - 1) // batch_size

                # Get chunk texts
                texts = [chunk.text for chunk in batch]

                # Generate embeddings
                embeddings = embedder.embed_batch(texts, batch_size=batch_size)

                # Upsert to vector DB
                chunk_ids = [str(chunk.id) for chunk in batch]
                payloads = [
                    {
                        "doc_id": str(chunk.doc_id),
                    }
                    for chunk in batch
                ]

                vectordb.upsert_batch(chunk_ids, embeddings, payloads)

                print(f"  [{batch_num}/{total_batches}] Processed {min(i+batch_size, total)}/{total} chunks")

            print()
            print("  [OK] All chunks re-embedded!")

    except Exception as e:
        print(f"  [ERROR] Migration failed: {e}")
        import traceback
        traceback.print_exc()
        print()
        print("  Your backup is safe at:")
        print(f"    {backup_dir}")
        sys.exit(1)

    print()
    print("=" * 80)
    print("  MIGRATION COMPLETE!")
    print("=" * 80)
    print()
    print("  You are now running GritLM-7B - the best local embedding model!")
    print()
    print("  Next steps:")
    print("    1. Start daemon: python -m mydata daemon")
    print("    2. Try some searches: python -m mydata search 'your query'")
    print("    3. Notice the DRAMATICALLY better results!")
    print()
    print("  Performance notes:")
    print("    - Search will be ~2x slower but WAY more accurate")
    print("    - Uses ~8-12GB RAM (worth it for the quality)")
    print("    - First search after startup takes 10-20 seconds (model loading)")
    print()
    print("  Your backup is saved at:")
    print(f"    {backup_dir}")
    print()
    print("=" * 80)


if __name__ == "__main__":
    try:
        migrate_to_gritlm()
    except KeyboardInterrupt:
        print("\n\n[CANCELLED] Migration cancelled by user")
        sys.exit(1)
