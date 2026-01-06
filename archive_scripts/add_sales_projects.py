"""Add sales dashboard projects and cross-correlate with emails"""

import sqlite3
from datetime import datetime
import re

# Project data from user input
projects_data = [
    {
        "project_id": "6744",
        "currency": "AUD",
        "business_unit": "Grid and Power Systems Advisory",
        "lead": "Chris Marinelli",
        "client": "Metlen Energy and Metals",
        "project_name": "Emu Park BESS R1 Connection Studies",
        "value": 599200.00,
        "probability": 10,
        "expected_value": 29856,
        "target_date": "2027-02-01",
        "start_date": "2025-09-15"
    },
    {
        "project_id": "504",
        "currency": "AUD",
        "business_unit": "Grid and Power Systems Advisory",
        "lead": "Chris Marinelli",
        "client": "Sirius Energy Australia Pty Ltd",
        "project_name": "Castle Doyle Wind Farm Connection Studies",
        "value": 570000.00,
        "probability": 10,
        "expected_value": 28401,
        "target_date": "2027-01-01",
        "start_date": "2024-04-13"
    },
    {
        "project_id": "680AU",
        "currency": "AUD",
        "business_unit": "Grid and Power Systems Advisory",
        "lead": "Chris Marinelli",
        "client": "Sirius Energy Australia Pty Ltd",
        "project_name": "Bethungra Wind Farm Connection Studies",
        "value": 570000.00,
        "probability": 10,
        "expected_value": 28401,
        "target_date": "2027-01-01",
        "start_date": "2024-04-13"
    },
    {
        "project_id": "5043",
        "currency": "AUD",
        "business_unit": "Grid and Power Systems Advisory",
        "lead": "Chris Marinelli",
        "client": "ELGIN ENERGY PTY LTD",
        "project_name": "Tabulam Solar Farm & BESS Connection Study Support",
        "value": 576100.00,
        "probability": 10,
        "expected_value": 28705,
        "target_date": "2027-01-01",
        "start_date": "2024-05-07"
    },
    {
        "project_id": "5147",
        "currency": "AUD",
        "business_unit": "Grid and Power Systems Advisory",
        "lead": "Chris Marinelli",
        "client": "Origin Energy Power Limited",
        "project_name": "Uranquinty AVR Replacement 5.3.9 Studies",
        "value": 400000.00,
        "probability": 10,
        "expected_value": 19930,
        "target_date": "2027-01-01",
        "start_date": "2024-10-12"
    },
    {
        "project_id": "5676",
        "currency": "AUD",
        "business_unit": "Grid and Power Systems Advisory",
        "lead": "Chris Marinelli",
        "client": "Origin Energy Power Limited",
        "project_name": "Shoalhaven Control Scheme Replacement 5.3.9 Studies",
        "value": 400000.00,
        "probability": 10,
        "expected_value": 19930,
        "target_date": "2027-01-01",
        "start_date": "2024-10-12"
    },
    {
        "project_id": "5677",
        "currency": "AUD",
        "business_unit": "Grid and Power Systems Advisory",
        "lead": "Chris Marinelli",
        "client": "SOUTH ENERGY PTY LTD",
        "project_name": "Inverell BESS RO Studies",
        "value": 625100.00,
        "probability": 10,
        "expected_value": 31146,
        "target_date": "2027-01-01",
        "start_date": "2025-06-16"
    },
    {
        "project_id": "3701",
        "currency": "AUD",
        "business_unit": "Grid and Power Systems Advisory",
        "lead": "Chris Marinelli",
        "client": "Origin Energy Power Limited",
        "project_name": "Deep Water SF - Connection Studies",
        "value": 529000.00,
        "probability": 20,
        "expected_value": 52716,
        "target_date": "2027-01-01",
        "start_date": "2023-04-05"
    },
    {
        "project_id": "4664",
        "currency": "AUD",
        "business_unit": "Grid and Power Systems Advisory",
        "lead": "Chris Marinelli",
        "client": "Shanghai Electric Australia Pty Ltd",
        "project_name": "Woolsthorpe WF Variation - Assistance With 5.3.9 Due Diligence",
        "value": 25800.00,
        "probability": 20,
        "expected_value": 2571,
        "target_date": "2027-01-01",
        "start_date": "2024-01-09"
    },
    {
        "project_id": "4855",
        "currency": "AUD",
        "business_unit": "Grid and Power Systems Advisory",
        "lead": "Chris Marinelli",
        "client": "ib vogt Development Australia Pty",
        "project_name": "Flynn Solar Farm Connection Studies",
        "value": 150000.00,
        "probability": 20,
        "expected_value": 14948,
        "target_date": "2027-01-01",
        "start_date": "2024-03-04"
    },
    {
        "project_id": "5656",
        "currency": "AUD",
        "business_unit": "Grid and Power Systems Advisory",
        "lead": "Chris Marinelli",
        "client": "Enerfin Energy Services Pty Ltd",
        "project_name": "Panorama BESS RO Connection Study and Support",
        "value": 500000.00,
        "probability": 20,
        "expected_value": 49826,
        "target_date": "2027-01-01",
        "start_date": "2024-10-05"
    },
    {
        "project_id": "5675",
        "currency": "AUD",
        "business_unit": "Grid and Power Systems Advisory",
        "lead": "Chris Marinelli",
        "client": "BNRG RENEWABLES LIMITED",
        "project_name": "Mt Stuart 1 & 2 AVR and Governor Replacement 5.3.9 Studies",
        "value": 400000.00,
        "probability": 20,
        "expected_value": 39861,
        "target_date": "2027-01-01",
        "start_date": "2024-10-12"
    },
    {
        "project_id": "6413",
        "currency": "AUD",
        "business_unit": "Grid and Power Systems Advisory",
        "lead": "Chris Marinelli",
        "client": "Recurrent Energy",
        "project_name": "Rifle Butts Wind Farm RO Studies",
        "value": 500000.00,
        "probability": 20,
        "expected_value": 49826,
        "target_date": "2027-01-01",
        "start_date": "2025-06-16"
    },
    {
        "project_id": "5520",
        "currency": "MYR",
        "business_unit": "Grid and Power Systems Advisory",
        "lead": "Chris Marinelli",
        "client": "LROA",
        "project_name": "Hydrogen Plant Connection Studies 1",
        "value": 275800.00,
        "probability": 10,
        "expected_value": 5012,
        "target_date": "2027-01-01",
        "start_date": "2025-06-25"
    },
    {
        "project_id": "6521",
        "currency": "MYR",
        "business_unit": "Grid and Power Systems Advisory",
        "lead": "Chris Marinelli",
        "client": "LRQA",
        "project_name": "Hydrogen Plant Connection Studies 2 (February 2026, Malaysia project)",
        "value": 275800.00,
        "probability": 10,
        "expected_value": 5012,
        "target_date": "2027-01-01",
        "start_date": "2025-06-25"
    }
]

def parse_date(date_str):
    """Parse date string to datetime"""
    if not date_str:
        return None
    try:
        return datetime.strptime(date_str, "%Y-%m-%d")
    except:
        return None

def determine_project_type(project_name):
    """Determine project type from name"""
    name_lower = project_name.lower()
    if 'bess' in name_lower or 'battery' in name_lower:
        return 'BESS'
    elif 'solar' in name_lower or 'sf' in name_lower:
        return 'Solar'
    elif 'wind' in name_lower or 'wf' in name_lower:
        return 'Wind'
    elif 'hydrogen' in name_lower:
        return 'Hydrogen'
    else:
        return 'Grid Connection'

def add_projects_to_db():
    """Add projects to database"""
    conn = sqlite3.connect('mydata/mydata.db')
    cursor = conn.cursor()

    print("Adding projects to database...\n")

    for proj in projects_data:
        project_type = determine_project_type(proj['project_name'])
        start_date = parse_date(proj['start_date'])
        target_date = parse_date(proj['target_date'])

        # Check if project already exists
        cursor.execute("""
            SELECT id FROM projects
            WHERE name = ? AND client_name = ?
        """, (proj['project_name'], proj['client']))

        existing = cursor.fetchone()

        if existing:
            print(f"[OK] Project already exists: {proj['project_name']} ({proj['client']})")
        else:
            cursor.execute("""
                INSERT INTO projects
                (name, client_name, project_type, status, start_date, target_completion, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                proj['project_name'],
                proj['client'],
                project_type,
                'Active',
                start_date,
                target_date,
                datetime.now(),
                datetime.now()
            ))
            print(f"[+] Added: {proj['project_name']} ({proj['client']})")

    conn.commit()
    conn.close()
    print(f"\n[OK] Processed {len(projects_data)} projects\n")

def search_emails_for_contacts():
    """Search documents for client contact information"""
    conn = sqlite3.connect('mydata/mydata.db')
    cursor = conn.cursor()

    # Check if there are any emails in the database
    cursor.execute("SELECT COUNT(*) FROM documents WHERE source_type = 'email'")
    email_count = cursor.fetchone()[0]

    if email_count == 0:
        print("No emails found in database. Displaying project data only...\n")
        conn.close()
        return [{
            'project_id': proj['project_id'],
            'project_name': proj['project_name'],
            'client': proj['client'],
            'value': proj['value'],
            'currency': proj['currency'],
            'probability': proj['probability'],
            'expected_value': proj['expected_value'],
            'start_date': proj['start_date'],
            'target_date': proj['target_date'],
            'contacts': [],
            'phones': [],
            'email_count': 0,
            'latest_note': 'No emails in database yet'
        } for proj in projects_data]

    print("Searching emails for contact information...\n")

    results = []

    for proj in projects_data:
        client = proj['client']

        # Search for emails mentioning this client
        cursor.execute("""
            SELECT d.raw_text, d.source, d.created_at
            FROM documents d
            WHERE d.source_type = 'email'
            AND (
                LOWER(d.raw_text) LIKE LOWER(?)
                OR LOWER(d.raw_text) LIKE LOWER(?)
            )
            ORDER BY d.created_at DESC
            LIMIT 5
        """, (f'%{client}%', f'%{proj["project_name"][:30]}%'))

        emails = cursor.fetchall()

        # Extract contact info from emails
        contacts = []
        phones = []
        notes = []

        for email_text, source, created_at in emails:
            # Extract email addresses
            email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
            found_emails = re.findall(email_pattern, email_text)
            contacts.extend(found_emails)

            # Extract phone numbers (Australian format)
            phone_pattern = r'(?:\+61|0)[2-478](?:[ -]?[0-9]){8}'
            found_phones = re.findall(phone_pattern, email_text)
            phones.extend(found_phones)

            # Extract relevant snippets
            lines = email_text.split('\n')
            for line in lines:
                if client.lower() in line.lower() or proj['project_name'][:20].lower() in line.lower():
                    notes.append(line.strip()[:200])

        results.append({
            'project_id': proj['project_id'],
            'project_name': proj['project_name'],
            'client': client,
            'value': proj['value'],
            'currency': proj['currency'],
            'probability': proj['probability'],
            'expected_value': proj['expected_value'],
            'start_date': proj['start_date'],
            'target_date': proj['target_date'],
            'contacts': list(set(contacts))[:5],  # Deduplicate and limit
            'phones': list(set(phones))[:3],
            'email_count': len(emails),
            'latest_note': notes[0] if notes else 'No email activity found'
        })

    conn.close()
    return results

def print_results_table(results):
    """Print comprehensive results table"""
    print("\n" + "="*150)
    print("SALES PIPELINE - PROJECT DETAILS WITH EMAIL CORRELATION")
    print("="*150 + "\n")

    for idx, proj in enumerate(results, 1):
        print(f"[{idx}] PROJECT: {proj['project_name']}")
        print(f"    ID: {proj['project_id']}")
        print(f"    Client: {proj['client']}")
        print(f"    Value: {proj['currency']} ${proj['value']:,.2f}")
        print(f"    Probability: {proj['probability']}% | Expected Value: ${proj['expected_value']:,.2f}")
        print(f"    Start: {proj['start_date']} | Target: {proj['target_date']}")
        print(f"    Email Activity: {proj['email_count']} related emails found")

        if proj['contacts']:
            print(f"    Contacts: {', '.join(proj['contacts'][:3])}")
        else:
            print(f"    Contacts: No email contacts found")

        if proj['phones']:
            print(f"    Phones: {', '.join(proj['phones'])}")
        else:
            print(f"    Phones: No phone numbers found")

        print(f"    Latest Note: {proj['latest_note'][:150]}")
        print()

    # Summary statistics
    total_value = sum(p['value'] for p in results if p['currency'] == 'AUD')
    total_expected = sum(p['expected_value'] for p in results if p['currency'] == 'AUD')

    print("="*150)
    print(f"SUMMARY: {len(results)} projects | Total Value (AUD): ${total_value:,.2f} | Total Expected (AUD): ${total_expected:,.2f}")
    print("="*150 + "\n")

if __name__ == '__main__':
    # Add projects to database
    add_projects_to_db()

    # Search emails and correlate
    results = search_emails_for_contacts()

    # Print comprehensive table
    print_results_table(results)
