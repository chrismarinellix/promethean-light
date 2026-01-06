"""Generate full pipeline report with email cross-correlation"""

import sqlite3
from pathlib import Path

DB_PATH = Path.home() / '.mydata' / 'mydata.db'

# Project data with contact info from email search
projects = [
    {
        "id": "6744", "name": "Emu Park BESS R1 Connection Studies",
        "client": "Metlen Energy and Metals", "value": 599200, "currency": "AUD",
        "prob": 10, "expected": 29856, "start": "2025-09-15", "target": "2027-02-01",
        "type": "BESS", "contacts": [], "phones": [], "notes": "No email data found"
    },
    {
        "id": "504", "name": "Castle Doyle Wind Farm Connection Studies",
        "client": "Sirius Energy Australia Pty Ltd", "value": 570000, "currency": "AUD",
        "prob": 10, "expected": 28401, "start": "2024-04-13", "target": "2027-01-01",
        "type": "Wind", "contacts": [], "phones": [], "notes": "No email data found"
    },
    {
        "id": "680AU", "name": "Bethungra Wind Farm Connection Studies",
        "client": "Sirius Energy Australia Pty Ltd", "value": 570000, "currency": "AUD",
        "prob": 10, "expected": 28401, "start": "2024-04-13", "target": "2027-01-01",
        "type": "Wind", "contacts": [], "phones": [], "notes": "No email data found"
    },
    {
        "id": "5043", "name": "Tabulam Solar Farm & BESS Connection Study Support",
        "client": "ELGIN ENERGY PTY LTD", "value": 576100, "currency": "AUD",
        "prob": 10, "expected": 28705, "start": "2024-05-07", "target": "2027-01-01",
        "type": "Solar",
        "contacts": ["kieran.kelly@elgin.com", "shane.slattery@elgin-energy.com", "derick.lima@elgin.com"],
        "phones": ["0341232310", "0387780382", "+61 0404 042 094"],
        "names": ["Shane Slattery", "Gururaja Asrolli"],
        "notes": "20 emails found - Active engagement with Elgin team"
    },
    {
        "id": "5147", "name": "Uranquinty AVR Replacement 5.3.9 Studies",
        "client": "Origin Energy Power Limited", "value": 400000, "currency": "AUD",
        "prob": 10, "expected": 19930, "start": "2024-10-12", "target": "2027-01-01",
        "type": "Grid",
        "contacts": ["meg.holding@originenergy.com.au"],
        "phones": ["0283717915", "0420088509", "0437 956 948"],
        "names": ["Meg Holding"],
        "notes": "20+ emails - Origin 5.3.9 studies active"
    },
    {
        "id": "5676", "name": "Shoalhaven Control Scheme Replacement 5.3.9 Studies",
        "client": "Origin Energy Power Limited", "value": 400000, "currency": "AUD",
        "prob": 10, "expected": 19930, "start": "2024-10-12", "target": "2027-01-01",
        "type": "Grid",
        "contacts": ["meg.holding@originenergy.com.au"],
        "phones": ["0283717915", "0420088509"],
        "names": ["Meg Holding"],
        "notes": "Origin Energy - 5.3.9 studies"
    },
    {
        "id": "5677", "name": "Inverell BESS RO Studies",
        "client": "SOUTH ENERGY PTY LTD", "value": 625100, "currency": "AUD",
        "prob": 10, "expected": 31146, "start": "2025-06-16", "target": "2027-01-01",
        "type": "BESS", "contacts": [], "phones": [], "notes": "No email data found"
    },
    {
        "id": "3701", "name": "Deep Water SF - Connection Studies",
        "client": "Origin Energy Power Limited", "value": 529000, "currency": "AUD",
        "prob": 20, "expected": 52716, "start": "2023-04-05", "target": "2027-01-01",
        "type": "Solar",
        "contacts": ["meg.holding@originenergy.com.au"],
        "phones": ["0283717915"],
        "names": ["Meg Holding"],
        "notes": "Longest running - Origin Energy contact"
    },
    {
        "id": "4664", "name": "Woolsthorpe WF Variation - 5.3.9 Due Diligence",
        "client": "Shanghai Electric Australia Pty Ltd", "value": 25800, "currency": "AUD",
        "prob": 20, "expected": 2571, "start": "2024-01-09", "target": "2027-01-01",
        "type": "Wind", "contacts": [], "phones": [], "notes": "No email data found"
    },
    {
        "id": "4855", "name": "Flynn Solar Farm Connection Studies",
        "client": "ib vogt Development Australia Pty", "value": 150000, "currency": "AUD",
        "prob": 20, "expected": 14948, "start": "2024-03-04", "target": "2027-01-01",
        "type": "Solar",
        "contacts": ["invoiceapac@ibvogt.com", "dan.halperin@ibvogt.com"],
        "phones": ["0749254542", "0749274360"],
        "notes": "6 emails - ib vogt invoice/billing related"
    },
    {
        "id": "5656", "name": "Panorama BESS RO Connection Study and Support",
        "client": "Enerfin Energy Services Pty Ltd", "value": 500000, "currency": "AUD",
        "prob": 20, "expected": 49826, "start": "2024-10-05", "target": "2027-01-01",
        "type": "BESS", "contacts": [], "phones": [], "notes": "No email data found"
    },
    {
        "id": "5675", "name": "Mt Stuart 1 & 2 AVR and Governor Replacement 5.3.9 Studies",
        "client": "BNRG RENEWABLES LIMITED", "value": 400000, "currency": "AUD",
        "prob": 20, "expected": 39861, "start": "2024-10-12", "target": "2027-01-01",
        "type": "Grid",
        "contacts": ["Andrew.jones@eneflux.com", "BillionWattsAU@billionwatts.com.tw"],
        "phones": ["0455633220", "0455633350"],
        "names": ["Peter Leeson", "Thomas Aas", "Elaine Chen"],
        "notes": "20 emails - BNRG/Leeson active discussion"
    },
    {
        "id": "6413", "name": "Rifle Butts Wind Farm RO Studies",
        "client": "Recurrent Energy", "value": 500000, "currency": "AUD",
        "prob": 20, "expected": 49826, "start": "2025-06-16", "target": "2027-01-01",
        "type": "Wind", "contacts": [], "phones": [], "notes": "No email data found"
    },
    {
        "id": "5520", "name": "Hydrogen Plant Connection Studies 1",
        "client": "LROA", "value": 275800, "currency": "MYR",
        "prob": 10, "expected": 5012, "start": "2025-06-25", "target": "2027-01-01",
        "type": "Hydrogen", "contacts": [], "phones": [], "notes": "No email data found"
    },
    {
        "id": "6521", "name": "Hydrogen Plant Connection Studies 2",
        "client": "LRQA", "value": 275800, "currency": "MYR",
        "prob": 10, "expected": 5012, "start": "2025-06-25", "target": "2027-01-01",
        "type": "Hydrogen",
        "contacts": ["christopher.spencer@vysusgroup.com", "amani.syafiqah@vysusgroup.com"],
        "phones": ["+6018 205 0225"],
        "names": ["Christopher Spencer"],
        "notes": "8 emails - Malaysia meet-up discussions"
    },
]

def print_report():
    print("="*140)
    print("SALES PIPELINE - GRID AND POWER SYSTEMS ADVISORY - FULL CONTACT REPORT")
    print("="*140)
    print()

    total_aud = sum(p['value'] for p in projects if p['currency'] == 'AUD')
    total_expected = sum(p['expected'] for p in projects if p['currency'] == 'AUD')

    print(f"Lead: Chris Marinelli | Projects: {len(projects)} | Total (AUD): ${total_aud:,.0f} | Expected: ${total_expected:,.0f}")
    print()

    # Sort by probability then value
    sorted_projects = sorted(projects, key=lambda x: (-x['prob'], -x['value']))

    for p in sorted_projects:
        print("-"*140)
        print(f"[{p['id']}] {p['name']}")
        print(f"     Client: {p['client']}")
        print(f"     Value: {p['currency']} ${p['value']:,.0f} | Prob: {p['prob']}% | Expected: ${p['expected']:,.0f}")
        print(f"     Timeline: {p['start']} to {p['target']} | Type: {p['type']}")

        if p.get('contacts'):
            print(f"     CONTACTS: {', '.join(p['contacts'][:3])}")
        else:
            print(f"     CONTACTS: None found in email database")

        if p.get('phones'):
            print(f"     PHONES: {', '.join(p['phones'][:2])}")

        if p.get('names'):
            print(f"     NAMES: {', '.join(p.get('names', []))}")

        print(f"     NOTES: {p['notes']}")
        print()

    print("="*140)
    print("CONTACTS FOUND:")
    for p in sorted_projects:
        if p.get('contacts'):
            print(f"  {p['client']}: {', '.join(p['contacts'][:2])}")
    print()
    print("CLIENTS NEEDING CONTACT LOOKUP:")
    for p in sorted_projects:
        if not p.get('contacts'):
            print(f"  - {p['client']}")
    print("="*140)

if __name__ == '__main__':
    print_report()
