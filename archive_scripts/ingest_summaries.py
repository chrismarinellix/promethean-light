"""
Ingest hardcoded summaries into the database so they're searchable via RAG.
This makes staff data, project data, etc. available to the chat interface.
"""

import sys
sys.path.insert(0, '.')

from mydata.database import Database
from mydata.embedder import Embedder
from mydata.vectordb import VectorDB
from mydata.ingestion import IngestionPipeline
from mydata.ml_organizer import MLOrganizer
from mydata.storage import EncryptedStorage
from mydata.crypto import CryptoManager
from mydata import summaries


def format_australia_staff():
    """Format Australia staff as searchable text"""
    data = summaries.get_australia_staff_summary()
    if not data or not data.get("staff"):
        return None

    lines = ["# Australia Staff Summary", ""]
    lines.append(f"Total staff: {len(data['staff'])}")
    lines.append("")

    for s in data["staff"]:
        lines.append(f"## {s.get('name', 'Unknown')}")
        lines.append(f"- Employee ID: {s.get('id', 'N/A')}")
        lines.append(f"- Position: {s.get('position', 'N/A')}")
        lines.append(f"- Base Salary: {s.get('base_salary', 'N/A')}")
        if s.get('with_bonus'):
            lines.append(f"- With Bonus: {s.get('with_bonus')}")
        if s.get('status'):
            lines.append(f"- Status: {s.get('status')}")
        lines.append("")

    return "\n".join(lines)


def format_india_staff():
    """Format India staff as searchable text"""
    data = summaries.get_india_staff_summary()
    if not data or not data.get("staff"):
        return None

    lines = ["# India Staff Summary", ""]
    lines.append(f"Total staff: {len(data['staff'])}")
    lines.append("")

    for s in data["staff"]:
        lines.append(f"## {s.get('name', 'Unknown')}")
        lines.append(f"- Employee ID: {s.get('id', 'N/A')}")
        lines.append(f"- Level: {s.get('level', 'N/A')}")
        lines.append(f"- CTC (INR): {s.get('ctc_inr', 'N/A')}")
        lines.append(f"- CTC (AUD): {s.get('ctc_aud', 'N/A')}")
        lines.append(f"- Retention Bonus: {s.get('retention_bonus', 'None')}")
        if s.get('bonus_until') and s.get('bonus_until') != '-':
            lines.append(f"- Bonus Until: {s.get('bonus_until')}")
        lines.append("")

    return "\n".join(lines)


def format_malaysia_staff():
    """Format Malaysia staff as searchable text"""
    try:
        data = summaries.get_malaysia_staff_summary()
        if not data or not data.get("staff"):
            return None

        lines = ["# Malaysia Staff Summary", ""]
        lines.append(f"Total staff: {len(data['staff'])}")
        lines.append("")

        for s in data["staff"]:
            lines.append(f"## {s.get('name', 'Unknown')}")
            lines.append(f"- Retention Bonus: {s.get('retention_bonus', 'None')}")
            lines.append("")

        return "\n".join(lines)
    except AttributeError:
        return None


def main():
    print("=" * 50)
    print("Ingesting Summaries into Database")
    print("=" * 50)

    # Initialize components
    print("\n[1/4] Initializing database...")
    db = Database()
    session = db.session()

    print("[2/4] Initializing crypto...")
    crypto = CryptoManager()
    try:
        crypto.unlock()
        print("  Crypto unlocked")
    except Exception as e:
        print(f"  Warning: Crypto not unlocked: {e}")
        print("  Set MYDATA_PASSPHRASE environment variable")
        return

    print("[3/4] Initializing embedder (this may take a moment)...")
    embedder = Embedder()

    print("[4/4] Initializing vector database...")
    vectordb = VectorDB()
    vectordb.initialize(dimension=embedder.dimension)

    # Create pipeline
    storage = EncryptedStorage(crypto)
    ml_organizer = MLOrganizer(embedder, session)
    pipeline = IngestionPipeline(session, storage, embedder, vectordb, ml_organizer)

    # Ingest summaries
    summaries_to_ingest = [
        ("Australia Staff", format_australia_staff()),
        ("India Staff", format_india_staff()),
        ("Malaysia Staff", format_malaysia_staff()),
    ]

    print("\n" + "=" * 50)
    print("Ingesting summaries...")
    print("=" * 50)

    ingested = 0
    for name, content in summaries_to_ingest:
        if content:
            print(f"\n  Ingesting: {name}")
            doc_id = pipeline.ingest_text(content, source=f"summary:{name.lower().replace(' ', '-')}")
            if doc_id:
                print(f"    Document ID: {doc_id}")
                ingested += 1
            else:
                print(f"    Failed to ingest")
        else:
            print(f"\n  Skipping: {name} (no data)")

    print("\n" + "=" * 50)
    print(f"Done! Ingested {ingested} summaries.")
    print("=" * 50)

    # Show updated stats
    from mydata.models import Document, Chunk
    from sqlmodel import select

    docs = session.exec(select(Document)).all()
    chunks = session.exec(select(Chunk)).all()
    vector_count = vectordb.count()

    print(f"\nDatabase stats:")
    print(f"  Documents: {len(docs)}")
    print(f"  Chunks (SQLite): {len(chunks)}")
    print(f"  Chunks (Vector DB): {vector_count}")


if __name__ == "__main__":
    main()
