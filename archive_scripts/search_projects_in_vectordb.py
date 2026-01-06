"""Search Qdrant vector DB for project and client information"""

from pathlib import Path
from qdrant_client import QdrantClient
import re
import json

# Client names to search for
clients = [
    "Metlen Energy and Metals",
    "Sirius Energy Australia",
    "ELGIN ENERGY",
    "Origin Energy",
    "SOUTH ENERGY",
    "Shanghai Electric Australia",
    "ib vogt Development Australia",
    "Enerfin Energy Services",
    "BNRG RENEWABLES",
    "Recurrent Energy",
    "LROA",
    "LRQA",
]

# Project keywords
project_keywords = [
    "Emu Park", "Castle Doyle", "Bethungra", "Tabulam", "Uranquinty",
    "Shoalhaven", "Inverell", "Deep Water", "Woolsthorpe", "Flynn",
    "Panorama", "Mt Stuart", "Rifle Butts", "Hydrogen Plant", "BESS",
    "Wind Farm", "Solar Farm", "Connection Studies"
]

def extract_emails(text):
    """Extract email addresses from text"""
    pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    return list(set(re.findall(pattern, text)))

def extract_phones(text):
    """Extract phone numbers (Australian and international)"""
    patterns = [
        r'\+61\s?[2-478](?:\s?\d){8}',  # +61 format
        r'0[2-478](?:\s?\d){8}',  # 04xx format
        r'\+\d{1,3}\s?\d{1,4}\s?\d{1,4}\s?\d{1,4}',  # International
    ]
    phones = []
    for pattern in patterns:
        phones.extend(re.findall(pattern, text))
    return list(set(phones))

def search_vectordb():
    """Search vector database for all documents"""
    qdrant_path = Path.home() / '.mydata' / 'qdrant'
    client = QdrantClient(path=str(qdrant_path))

    # Get all points from the documents collection
    print("Fetching all documents from Qdrant vector database...\n")

    # Scroll through all documents
    records, next_offset = client.scroll(
        collection_name="documents",
        limit=100,
        with_payload=True,
        with_vectors=False
    )

    print(f"Found {len(records)} documents in vector DB\n")
    print("="*120)

    all_matches = {}

    for idx, record in enumerate(records, 1):
        payload = record.payload

        # Get text content
        text = payload.get('text', '') or payload.get('content', '') or payload.get('raw_text', '') or ''
        source = payload.get('source', 'Unknown')
        source_type = payload.get('source_type', payload.get('source', 'Unknown'))

        # Skip if no text
        if not text:
            continue

        print(f"\n[{idx}] Document ID: {record.id}")
        print(f"    Source Type: {source_type}")
        print(f"    Source: {source[:100]}")
        print(f"    Text Length: {len(text)} chars")

        # Search for client mentions
        found_clients = []
        found_projects = []

        for client in clients:
            if client.lower() in text.lower():
                found_clients.append(client)

        for keyword in project_keywords:
            if keyword.lower() in text.lower():
                found_projects.append(keyword)

        if found_clients or found_projects:
            print(f"    MATCH! Clients: {', '.join(found_clients) if found_clients else 'None'}")
            print(f"    Projects: {', '.join(found_projects) if found_projects else 'None'}")

            # Extract contact info
            emails = extract_emails(text)
            phones = extract_phones(text)

            if emails:
                print(f"    Emails found: {', '.join(emails[:5])}")
            if phones:
                print(f"    Phones found: {', '.join(phones[:3])}")

            # Store matches
            for client in found_clients:
                if client not in all_matches:
                    all_matches[client] = {
                        'emails': [],
                        'phones': [],
                        'documents': [],
                        'projects': []
                    }
                all_matches[client]['emails'].extend(emails)
                all_matches[client]['phones'].extend(phones)
                all_matches[client]['documents'].append(source)
                all_matches[client]['projects'].extend(found_projects)

            # Show snippet
            if found_clients or found_projects:
                snippet = text[:300].replace('\n', ' ').strip()
                print(f"    Snippet: {snippet}...")

        print("-" * 120)

    # Summary
    print("\n" + "="*120)
    print("SUMMARY - CLIENT CONTACT INFORMATION")
    print("="*120 + "\n")

    if all_matches:
        for client, data in all_matches.items():
            print(f"\n{client}:")
            unique_emails = list(set(data['emails']))
            unique_phones = list(set(data['phones']))
            unique_projects = list(set(data['projects']))

            if unique_emails:
                print(f"  Emails: {', '.join(unique_emails[:5])}")
            else:
                print(f"  Emails: None found")

            if unique_phones:
                print(f"  Phones: {', '.join(unique_phones[:3])}")
            else:
                print(f"  Phones: None found")

            if unique_projects:
                print(f"  Related Projects: {', '.join(unique_projects[:5])}")

            print(f"  Documents: {len(data['documents'])} related")
    else:
        print("No matches found for any clients in the vector database.")

    print("\n" + "="*120)

if __name__ == '__main__':
    search_vectordb()
