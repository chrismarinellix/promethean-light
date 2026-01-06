"""Search vector database for engineer salary bands and compensation information"""

from pathlib import Path
from qdrant_client import QdrantClient
from mydata.embedder import Embedder
import re

def search_salary_info():
    """Search vector database for salary band information"""
    qdrant_path = Path.home() / '.mydata' / 'qdrant'
    client = QdrantClient(path=str(qdrant_path))

    # Initialize embedder
    print("Loading embedding model...")
    embedder = Embedder(model_name="BAAI/bge-large-en-v1.5")

    # Search queries for salary information
    queries = [
        "engineer salary band grade pay scale compensation range",
        "engineering salary ranges by level junior mid senior principal",
        "salary bands for engineers compensation framework",
        "engineer grade levels pay ranges",
        "salary review engineer compensation bands",
        "HR salary guide engineering roles pay scales",
        "engineering role classifications salary ranges",
        "engineer pay grades salary structure",
        "salary band ranges for technical staff engineers",
        "compensation framework engineer levels grades"
    ]

    print(f"\nSearching vector database with {len(queries)} queries...\n")
    print("="*120)

    all_results = {}

    for query in queries:
        print(f"\nQuery: '{query}'")

        # Generate embedding for query
        query_vector = embedder.embed(query)

        # Search in vector database
        results = client.search(
            collection_name="documents",
            query_vector=query_vector.tolist(),
            limit=10,
            score_threshold=0.3  # Lower threshold to catch more results
        )

        print(f"Found {len(results)} results\n")

        for idx, hit in enumerate(results, 1):
            doc_id = hit.id
            score = hit.score
            payload = hit.payload

            # Get text content
            text = payload.get('text', '') or payload.get('content', '') or payload.get('raw_text', '') or ''
            source = payload.get('source', 'Unknown')
            source_type = payload.get('source_type', 'Unknown')

            # Skip if already processed
            if doc_id in all_results:
                continue

            # Check if text contains salary/compensation keywords
            salary_keywords = [
                'salary', 'band', 'grade', 'pay scale', 'compensation',
                'pay range', 'engineer level', 'junior', 'mid', 'senior',
                'principal', 'lead', 'staff engineer', 'grade 1', 'grade 2',
                'AUD', '$', 'annual', 'base pay', 'remuneration'
            ]

            keyword_matches = sum(1 for kw in salary_keywords if kw.lower() in text.lower())

            if keyword_matches >= 2:  # At least 2 salary keywords
                print(f"  [{idx}] Score: {score:.3f} | Keywords: {keyword_matches}")
                print(f"      Source: {source_type} - {source[:80]}")
                print(f"      Text length: {len(text)} chars")

                # Store in results
                all_results[doc_id] = {
                    'score': score,
                    'text': text,
                    'source': source,
                    'source_type': source_type,
                    'keyword_matches': keyword_matches,
                    'query': query
                }

        print("-" * 120)

    # Now analyze and extract salary information from top results
    print("\n" + "="*120)
    print("SALARY BAND INFORMATION FOUND")
    print("="*120 + "\n")

    if not all_results:
        print("No salary band information found in vector database.")
        return

    # Sort by keyword matches and score
    sorted_results = sorted(
        all_results.items(),
        key=lambda x: (x[1]['keyword_matches'], x[1]['score']),
        reverse=True
    )

    for doc_id, data in sorted_results[:20]:  # Top 20 results
        print(f"\n{'='*120}")
        print(f"Document ID: {doc_id}")
        print(f"Source: {data['source_type']} - {data['source'][:100]}")
        print(f"Relevance Score: {data['score']:.3f} | Keyword Matches: {data['keyword_matches']}")
        print(f"Matched Query: '{data['query']}'")
        print(f"\n{'-'*120}")
        print("CONTENT:")
        print(f"{'-'*120}")

        text = data['text']

        # Try to extract salary band information
        # Look for patterns like: Grade/Band X: $XXX,XXX - $XXX,XXX
        # Or: Junior Engineer: $XX,XXX - $XX,XXX

        lines = text.split('\n')
        relevant_lines = []

        for i, line in enumerate(lines):
            line_lower = line.lower()
            # Check if line contains salary information
            if any(kw in line_lower for kw in ['salary', 'band', 'grade', 'pay', 'compensation', '$', 'aud']):
                # Include context (2 lines before and after)
                start = max(0, i-2)
                end = min(len(lines), i+3)
                context = '\n'.join(lines[start:end])
                if context not in relevant_lines:
                    relevant_lines.append(context)

        if relevant_lines:
            print("\nRELEVANT SECTIONS:")
            for section in relevant_lines[:10]:  # Limit to 10 sections
                print(f"\n  {section}")
                print()
        else:
            # If no specific sections, show first 1000 chars
            print(text[:1000])
            if len(text) > 1000:
                print(f"\n... [truncated, {len(text) - 1000} more characters]")

        print("\n" + "="*120)

    # Also check if there's a file specifically about HR or salary
    print("\n\n" + "="*120)
    print("SEARCHING FOR HR/SALARY SPECIFIC DOCUMENTS")
    print("="*120 + "\n")

    # Scroll through all documents looking for HR-related files
    records, _ = client.scroll(
        collection_name="documents",
        limit=1000,
        with_payload=True,
        with_vectors=False
    )

    hr_docs = []
    for record in records:
        payload = record.payload
        source = payload.get('source', '').lower()
        text = (payload.get('text', '') or payload.get('content', '') or payload.get('raw_text', '') or '').lower()

        # Check if filename or content suggests HR/salary information
        if any(term in source for term in ['hr', 'salary', 'compensation', 'pay', 'grade', 'band', 'apac']) or \
           ('salary' in text and 'engineer' in text and len(text) > 500):
            hr_docs.append({
                'id': record.id,
                'source': payload.get('source', 'Unknown'),
                'source_type': payload.get('source_type', 'Unknown'),
                'text': payload.get('text', '') or payload.get('content', '') or payload.get('raw_text', '')
            })

    if hr_docs:
        print(f"Found {len(hr_docs)} HR/Salary related documents:\n")
        for doc in hr_docs:
            print(f"\nDocument: {doc['source']}")
            print(f"Type: {doc['source_type']}")
            print(f"Length: {len(doc['text'])} chars")
            print(f"\nContent preview:")
            print(doc['text'][:2000])
            if len(doc['text']) > 2000:
                print(f"\n... [truncated, {len(doc['text']) - 2000} more characters]")
            print("\n" + "-"*120)
    else:
        print("No specific HR/Salary documents found by filename.")

    print("\n" + "="*120)

if __name__ == '__main__':
    search_salary_info()
