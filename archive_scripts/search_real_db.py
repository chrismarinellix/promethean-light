"""Search the REAL mydata database for project and client information"""

import sqlite3
import re
from pathlib import Path

DB_PATH = Path.home() / '.mydata' / 'mydata.db'

# Client names to search for
clients = [
    ("Metlen Energy", "Metlen"),
    ("Sirius Energy", "Sirius"),
    ("ELGIN ENERGY", "Elgin"),
    ("Origin Energy", "Origin"),
    ("SOUTH ENERGY", "South Energy"),
    ("Shanghai Electric", "Shanghai"),
    ("ib vogt", "vogt"),
    ("Enerfin Energy", "Enerfin"),
    ("BNRG RENEWABLES", "BNRG"),
    ("Recurrent Energy", "Recurrent"),
    ("LROA", "LROA"),
    ("LRQA", "LRQA"),
]

# Project keywords
project_keywords = [
    "Emu Park", "Castle Doyle", "Bethungra", "Tabulam", "Uranquinty",
    "Shoalhaven", "Inverell", "Deep Water", "Woolsthorpe", "Flynn",
    "Panorama", "Mt Stuart", "Rifle Butts", "Hydrogen", "BESS",
    "Wind Farm", "Solar Farm", "Connection Studies", "5.3.9"
]

def extract_emails(text):
    """Extract email addresses from text"""
    pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    return list(set(re.findall(pattern, text)))

def extract_phones(text):
    """Extract phone numbers"""
    patterns = [
        r'\+61\s?[2-478](?:\s?\d){8}',
        r'0[2-478](?:[ -]?\d){8}',
        r'\+\d{1,3}[ -]?\d{2,4}[ -]?\d{3,4}[ -]?\d{3,4}',
    ]
    phones = []
    for pattern in patterns:
        phones.extend(re.findall(pattern, text))
    return list(set(phones))

def extract_names(text, client_name):
    """Try to extract contact names near client mention"""
    names = []
    # Look for patterns like "From: Name" or "name@company"
    from_pattern = r'From:\s*([A-Z][a-z]+ [A-Z][a-z]+)'
    names.extend(re.findall(from_pattern, text))
    return list(set(names))[:3]

def search_database():
    """Search database for client information"""
    conn = sqlite3.connect(str(DB_PATH))
    cursor = conn.cursor()

    print(f"Database: {DB_PATH}")
    cursor.execute("SELECT COUNT(*) FROM documents WHERE source_type = 'email'")
    email_count = cursor.fetchone()[0]
    print(f"Total emails in database: {email_count}")
    print("="*120 + "\n")

    results = {}

    for client_full, client_short in clients:
        # Search for emails mentioning this client
        cursor.execute("""
            SELECT raw_text, source, created_at
            FROM documents
            WHERE source_type = 'email'
            AND (LOWER(raw_text) LIKE LOWER(?) OR LOWER(raw_text) LIKE LOWER(?))
            ORDER BY created_at DESC
            LIMIT 20
        """, (f'%{client_full}%', f'%{client_short}%'))

        emails = cursor.fetchall()

        if emails:
            all_contacts = []
            all_phones = []
            all_names = []
            snippets = []
            project_mentions = []

            for raw_text, source, created_at in emails:
                all_contacts.extend(extract_emails(raw_text))
                all_phones.extend(extract_phones(raw_text))
                all_names.extend(extract_names(raw_text, client_full))

                # Find project mentions
                for kw in project_keywords:
                    if kw.lower() in raw_text.lower():
                        project_mentions.append(kw)

                # Extract relevant snippet
                lines = raw_text.split('\n')
                for line in lines:
                    if client_short.lower() in line.lower() and len(line) > 20:
                        snippets.append(line.strip()[:200])
                        break

            results[client_full] = {
                'email_count': len(emails),
                'contacts': list(set(all_contacts))[:8],
                'phones': list(set(all_phones))[:5],
                'names': list(set(all_names))[:5],
                'projects': list(set(project_mentions)),
                'snippet': snippets[0] if snippets else 'N/A'
            }

    conn.close()

    # Print results
    print("CLIENT CONTACT INFORMATION FROM EMAIL DATABASE")
    print("="*120 + "\n")

    for client, data in results.items():
        print(f"[{client}]")
        print(f"  Emails found: {data['email_count']}")
        if data['contacts']:
            print(f"  Contact emails: {', '.join(data['contacts'][:5])}")
        if data['phones']:
            print(f"  Phone numbers: {', '.join(data['phones'][:3])}")
        if data['names']:
            print(f"  Contact names: {', '.join(data['names'])}")
        if data['projects']:
            print(f"  Project mentions: {', '.join(data['projects'][:5])}")
        print(f"  Latest: {data['snippet'][:100]}...")
        print()

    # Clients not found
    searched = set(c[0] for c in clients)
    found = set(results.keys())
    not_found = searched - found
    if not_found:
        print("\n" + "-"*120)
        print("Clients NOT found in email database:")
        for c in not_found:
            print(f"  - {c}")

    print("\n" + "="*120)

if __name__ == '__main__':
    search_database()
