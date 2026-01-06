#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Extract detailed Mt Challenger project information"""

import sqlite3
import sys
from pathlib import Path
import re

# Fix encoding for Windows console
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')

def main():
    db_path = Path.home() / ".mydata" / "mydata.db"
    conn = sqlite3.connect(str(db_path))
    cur = conn.cursor()

    # Get all Mt Challenger emails
    rows = cur.execute("""
        SELECT id, source, created_at, raw_text
        FROM documents
        WHERE source_type='email'
        AND (
            LOWER(raw_text) LIKE '%mt challenger%'
            OR LOWER(raw_text) LIKE '%mt. challenger%'
            OR LOWER(raw_text) LIKE '%challenger%'
        )
        AND (
            LOWER(raw_text) LIKE '%robby%'
            OR LOWER(source) LIKE '%robby%'
        )
        ORDER BY created_at DESC
    """).fetchall()

    print("SEARCHING FOR TECHNICAL DETAILS...\n")
    print("=" * 100)

    # Search for specific details
    details = {
        'capacity_mw': None,
        'location': None,
        'connection_point': None,
        'voltage': None,
        'scope': [],
        'timeline': [],
        'deliverables': [],
        'technical_studies': []
    }

    for email_id, source, created_at, raw_text in rows:
        text_lower = raw_text.lower()

        # Look for capacity (MW)
        mw_matches = re.findall(r'(\d+)\s*mw', text_lower)
        if mw_matches and not details['capacity_mw']:
            details['capacity_mw'] = mw_matches[0]
            print(f"Found capacity: {mw_matches[0]} MW")

        # Look for location/region
        if 'queensland' in text_lower or 'qld' in text_lower:
            if 'powerlink' in text_lower:
                details['location'] = 'Queensland (Powerlink network)'

        # Look for voltage levels
        voltage_matches = re.findall(r'(\d+)\s*kv', text_lower)
        if voltage_matches:
            for v in voltage_matches:
                if v not in str(details['voltage']):
                    if details['voltage']:
                        details['voltage'] += f", {v}kV"
                    else:
                        details['voltage'] = f"{v}kV"

        # Look for scope items
        if 'capacity assessment' in text_lower:
            if 'capacity assessment' not in str(details['scope']):
                details['scope'].append('Capacity Assessment')

        if 'connection application' in text_lower:
            if 'connection application' not in str(details['scope']):
                details['scope'].append('Connection Application')

        if 'compliance assessment' in text_lower:
            if 'compliance assessment' not in str(details['scope']):
                details['scope'].append('Compliance Assessment')

        if 'harmonics' in text_lower:
            if 'Harmonics Analysis' not in str(details['technical_studies']):
                details['technical_studies'].append('Harmonics Analysis')

        if 'powerfactory' in text_lower or 'power factory' in text_lower:
            if 'PowerFactory Modeling' not in str(details['technical_studies']):
                details['technical_studies'].append('PowerFactory Modeling')

        if 'network loading' in text_lower or 'loading' in text_lower and '66' in text_lower:
            if 'Network Loading Analysis' not in str(details['technical_studies']):
                details['technical_studies'].append('Network Loading Analysis (66kV)')

        # Look for timeline mentions
        if 'before christmas' in text_lower or 'christmas' in text_lower:
            if 'capacity' in text_lower:
                if 'Capacity assessment before Christmas' not in str(details['timeline']):
                    details['timeline'].append('Capacity assessment before Christmas 2025')

        if 'january' in text_lower or 'february' in text_lower:
            if 'connection' in text_lower:
                if 'Connection Application' not in str(details['timeline']):
                    details['timeline'].append('Connection Application: Late Jan/Early Feb 2026')

    print("\n" + "=" * 100)
    print("PROJECT DETAILS EXTRACTED:")
    print("=" * 100)

    print(f"\nProject Number: Q7193")
    print(f"Project Type: Wind Farm + Battery Energy Storage System (BESS)")
    print(f"Network: Powerlink Queensland")

    if details['capacity_mw']:
        print(f"Capacity: {details['capacity_mw']} MW (estimated)")

    if details['location']:
        print(f"Location: {details['location']}")

    if details['voltage']:
        print(f"Voltage Levels: {details['voltage']}")

    if details['scope']:
        print(f"\nScope of Work:")
        for item in details['scope']:
            print(f"  • {item}")

    if details['technical_studies']:
        print(f"\nTechnical Studies:")
        for item in details['technical_studies']:
            print(f"  • {item}")

    if details['timeline']:
        print(f"\nProject Timeline:")
        for item in details['timeline']:
            print(f"  • {item}")

    # Now look for more specific details in email bodies
    print("\n" + "=" * 100)
    print("DETAILED EMAIL EXCERPTS:")
    print("=" * 100)

    for email_id, source, created_at, raw_text in rows[:10]:  # Check first 10 emails
        text_lower = raw_text.lower()

        # Look for scope descriptions
        if 'scope' in text_lower and ('study' in text_lower or 'studies' in text_lower):
            # Find the section with scope
            lines = raw_text.split('\n')
            for i, line in enumerate(lines):
                if 'scope' in line.lower() and i < len(lines) - 5:
                    excerpt = '\n'.join(lines[i:i+10])
                    if len(excerpt) > 100:
                        print(f"\nDate: {created_at[:10]}")
                        print(f"Excerpt:\n{excerpt[:500]}\n")
                        print("-" * 100)
                        break

        # Look for deliverables
        if 'deliverable' in text_lower:
            lines = raw_text.split('\n')
            for i, line in enumerate(lines):
                if 'deliverable' in line.lower() and i < len(lines) - 3:
                    excerpt = '\n'.join(lines[i:i+5])
                    if len(excerpt) > 50:
                        print(f"\nDate: {created_at[:10]}")
                        print(f"Deliverables mentioned:\n{excerpt[:300]}\n")
                        print("-" * 100)
                        break

    # Look for what Cedric specifically said about timing
    print("\n" + "=" * 100)
    print("CEDRIC'S TIMELINE REQUIREMENTS:")
    print("=" * 100)

    for email_id, source, created_at, raw_text in rows:
        if 'cedric' in raw_text.lower() or 'cedric.banda' in raw_text.lower():
            text_lower = raw_text.lower()

            if 'christmas' in text_lower or 'december' in text_lower or 'january' in text_lower:
                lines = raw_text.split('\n')

                # Find Cedric's messages
                for i, line in enumerate(lines):
                    if ('from:' in line.lower() and 'cedric' in line.lower()) or 'cedric' in line.lower():
                        # Get context around this
                        start = max(0, i - 2)
                        end = min(len(lines), i + 15)
                        excerpt = '\n'.join(lines[start:end])

                        if 'christmas' in excerpt.lower() or 'capacity' in excerpt.lower():
                            print(f"\nDate: {created_at[:10]}")
                            print(f"Context:\n{excerpt[:600]}\n")
                            print("-" * 100)
                            break

    conn.close()

if __name__ == "__main__":
    main()
