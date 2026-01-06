"""Quick script to save a note to Promethean Light"""
import sys
from pathlib import Path

# Add mydata to path
sys.path.insert(0, str(Path(__file__).parent))

from mydata.database import Database
from mydata.embedder import Embedder
from mydata.vectordb import VectorDB
from mydata.ingestion import IngestionPipeline
from mydata.config import Config

def main():
    # Initialize components (no encryption needed for read-only text file)
    db = Database(Config.DATABASE_PATH)
    embedder = Embedder()
    vectordb = VectorDB(Config.QDRANT_PATH)

    # Create pipeline (storage not needed for plain text ingestion)
    from mydata.storage import EncryptedStorage
    from mydata.crypto import CryptoManager

    # Create dummy crypto manager
    crypto = CryptoManager(Config.MYDATA_HOME)
    storage = EncryptedStorage(crypto)

    pipeline = IngestionPipeline(
        db_session=db.get_session(),
        storage=storage,
        embedder=embedder,
        vectordb=vectordb
    )

    # Ingest the file
    file_path = Path(r"C:\Code\Promethian  Light\license_resource_allocation_note.txt")
    print(f"Ingesting: {file_path}")

    result = pipeline.ingest_file(file_path)

    if result:
        print(f"\nSUCCESS: Note saved to Promethean Light database!")
        print(f"Document ID: {result}")
    else:
        print("\nFAILED: Could not save note")
        sys.exit(1)

if __name__ == "__main__":
    main()
