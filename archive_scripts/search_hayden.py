"""Search for all information about Hayden in the Promethean Light database"""

import sqlite3
import sys
from pathlib import Path

# Set UTF-8 encoding for output
sys.stdout.reconfigure(encoding='utf-8') if hasattr(sys.stdout, 'reconfigure') else None

# Add mydata to path
sys.path.insert(0, str(Path(__file__).parent / 'mydata'))

from embedder import Embedder
from vectordb import VectorDB

DB_PATH = Path.home() / '.mydata' / 'mydata.db'
QDRANT_PATH = Path.home() / '.mydata' / 'qdrant'

def search_vector_db(query: str, limit: int = 20):
    """Search vector database using semantic search"""
    print(f"\n{'='*100}")
    print(f"VECTOR SEARCH: {query}")
    print(f"{'='*100}\n")

    try:
        embedder = Embedder()
        vectordb = VectorDB(path=QDRANT_PATH)

        # Generate query embedding
        query_vector = embedder.embed(query)

        # Search vector database
        results = vectordb.search(query_vector, limit=limit, score_threshold=0.3)

        if not results:
            print(f"No results found for: {query}\n")
            return []

        print(f"Found {len(results)} results:\n")

        # Get document details from SQLite
        conn = sqlite3.connect(str(DB_PATH))
        cursor = conn.cursor()

        doc_ids = []
        for i, result in enumerate(results, 1):
            doc_id = result['id']
            score = result['score']

            cursor.execute("""
                SELECT raw_text, source, source_type, created_at
                FROM documents
                WHERE id = ?
            """, (doc_id,))

            row = cursor.fetchone()
            if row:
                raw_text, source, source_type, created_at = row
                print(f"\n[Result {i}] Score: {score:.4f}")
                print(f"Source: {source} ({source_type})")
                print(f"Date: {created_at}")
                print(f"\nContent Preview:")

                # Show relevant content
                text_to_show = raw_text
                if text_to_show:
                    lines = text_to_show.split('\n')
                    # Show first 30 lines or lines containing Hayden
                    hayden_lines = [line for line in lines if 'hayden' in line.lower()]
                    if hayden_lines:
                        print("Lines mentioning Hayden:")
                        for line in hayden_lines[:20]:
                            print(f"  {line.strip()}")
                    else:
                        # Show first 20 lines
                        for line in lines[:20]:
                            if line.strip():
                                print(f"  {line.strip()}")

                print(f"\n{'-'*100}")
                doc_ids.append(doc_id)

        conn.close()
        return doc_ids

    except Exception as e:
        print(f"Error during vector search: {e}")
        import traceback
        traceback.print_exc()
        return []

def search_sqlite_direct(keywords: list):
    """Direct SQL search for keywords"""
    print(f"\n{'='*100}")
    print(f"DIRECT SQL SEARCH FOR: {', '.join(keywords)}")
    print(f"{'='*100}\n")

    conn = sqlite3.connect(str(DB_PATH))
    cursor = conn.cursor()

    # Build WHERE clause for multiple keywords
    conditions = []
    params = []
    for keyword in keywords:
        conditions.append("LOWER(raw_text) LIKE ?")
        params.append(f'%{keyword.lower()}%')

    where_clause = " AND ".join(conditions)

    query = f"""
        SELECT id, raw_text, source, source_type, created_at
        FROM documents
        WHERE {where_clause}
        ORDER BY created_at DESC
    """

    cursor.execute(query, params)
    rows = cursor.fetchall()

    print(f"Found {len(rows)} documents\n")

    for i, row in enumerate(rows, 1):
        doc_id, raw_text, source, source_type, created_at = row

        print(f"\n[Document {i}]")
        print(f"Source: {source} ({source_type})")
        print(f"Date: {created_at}")
        print(f"\nContent:")

        text_to_search = raw_text or ""

        # Extract relevant lines
        lines = text_to_search.split('\n')
        relevant_lines = []
        for line in lines:
            line_lower = line.lower()
            if any(kw.lower() in line_lower for kw in keywords):
                relevant_lines.append(line.strip())

        if relevant_lines:
            for line in relevant_lines[:30]:
                if line:
                    print(f"  {line}")
        else:
            # Show first 20 lines if no keyword matches
            for line in lines[:20]:
                if line.strip():
                    print(f"  {line.strip()}")

        print(f"\n{'-'*100}")

    conn.close()
    return len(rows)

def main():
    """Run comprehensive search for Hayden"""

    print("\n" + "="*100)
    print("COMPREHENSIVE SEARCH FOR HAYDEN IN PROMETHEAN LIGHT DATABASE")
    print("="*100)

    # Check if database exists
    if not DB_PATH.exists():
        print(f"\nERROR: Database not found at {DB_PATH}")
        return

    print(f"\nDatabase: {DB_PATH}")

    # Get total document count
    conn = sqlite3.connect(str(DB_PATH))
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM documents")
    total_docs = cursor.fetchone()[0]
    print(f"Total documents: {total_docs}")
    conn.close()

    # 1. Direct SQL search for Hayden
    print("\n\n" + "="*100)
    print("PHASE 1: DIRECT SQL SEARCH FOR 'HAYDEN'")
    print("="*100)
    search_sqlite_direct(['hayden'])

    # 2. Hayden salary and pay rise
    print("\n\n" + "="*100)
    print("PHASE 2: HAYDEN + SALARY/PAY RISE")
    print("="*100)
    search_sqlite_direct(['hayden', 'salary'])
    search_sqlite_direct(['hayden', 'pay rise'])
    search_sqlite_direct(['hayden', 'increase'])
    search_sqlite_direct(['hayden', 'compensation'])

    # 3. Hayden career progression
    print("\n\n" + "="*100)
    print("PHASE 3: HAYDEN + CAREER PROGRESSION")
    print("="*100)
    search_sqlite_direct(['hayden', 'promotion'])
    search_sqlite_direct(['hayden', 'senior'])
    search_sqlite_direct(['hayden', 'junior'])
    search_sqlite_direct(['hayden', 'progression'])

    # 4. Hayden performance and market rate
    print("\n\n" + "="*100)
    print("PHASE 4: HAYDEN + PERFORMANCE/MARKET RATE")
    print("="*100)
    search_sqlite_direct(['hayden', 'performance'])
    search_sqlite_direct(['hayden', 'review'])
    search_sqlite_direct(['hayden', 'market rate'])
    search_sqlite_direct(['hayden', 'feedback'])

    # 5. Vector search queries
    print("\n\n" + "="*100)
    print("PHASE 5: SEMANTIC VECTOR SEARCH")
    print("="*100)

    search_queries = [
        "Hayden salary increase pay rise",
        "Hayden current salary compensation",
        "Hayden market rate junior engineer",
        "Hayden career progression junior to senior",
        "Hayden performance review feedback",
        "Hayden promotion advancement",
        "Hayden pay increase discussion",
        "Hayden compensation review",
    ]

    for query in search_queries:
        search_vector_db(query, limit=10)

    print("\n\n" + "="*100)
    print("SEARCH COMPLETE")
    print("="*100 + "\n")

if __name__ == '__main__':
    main()
