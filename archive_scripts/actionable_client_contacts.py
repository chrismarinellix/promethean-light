"""Generate actionable client contact table for sales follow-up"""

import sqlite3
from pathlib import Path
from datetime import datetime, timedelta

DB_PATH = Path.home() / '.mydata' / 'mydata.db'

# Enhanced project data with all contact info
projects = [
    {
        "id": "3701", "name": "Deep Water SF - Connection Studies",
        "client": "Origin Energy Power Limited", "value": 529000, "currency": "AUD",
        "prob": 20, "expected": 52716, "start": "2023-04-05", "target": "2027-01-01",
        "type": "Solar", "priority": "HIGH - 20%",
        "contacts": ["meg.holding@originenergy.com.au"],
        "phones": ["0283717915", "0420088509", "0437 956 948"],
        "names": ["Meg Holding"],
        "email_activity": "20+ emails | Last: Recent",
        "action": "Follow up on Deep Water SF progress - longest running project since Apr 2023"
    },
    {
        "id": "5656", "name": "Panorama BESS RO Connection Study",
        "client": "Enerfin Energy Services Pty Ltd", "value": 500000, "currency": "AUD",
        "prob": 20, "expected": 49826, "start": "2024-10-05", "target": "2027-01-01",
        "type": "BESS", "priority": "HIGH - 20%",
        "contacts": [], "phones": [], "names": [],
        "email_activity": "NO EMAILS FOUND",
        "action": "URGENT: Find contact - high value project with no email trail"
    },
    {
        "id": "6413", "name": "Rifle Butts Wind Farm RO Studies",
        "client": "Recurrent Energy", "value": 500000, "currency": "AUD",
        "prob": 20, "expected": 49826, "start": "2025-06-16", "target": "2027-01-01",
        "type": "Wind", "priority": "HIGH - 20%",
        "contacts": [], "phones": [], "names": [],
        "email_activity": "NO EMAILS FOUND",
        "action": "URGENT: New project (Jun 2025) - need to establish contact"
    },
    {
        "id": "5675", "name": "Mt Stuart 1 & 2 AVR/Governor Replacement",
        "client": "BNRG RENEWABLES LIMITED", "value": 400000, "currency": "AUD",
        "prob": 20, "expected": 39861, "start": "2024-10-12", "target": "2027-01-01",
        "type": "Grid", "priority": "HIGH - 20%",
        "contacts": ["Andrew.jones@eneflux.com", "BillionWattsAU@billionwatts.com.tw"],
        "phones": ["0455633220", "0455633350", "0455633440"],
        "names": ["Peter Leeson", "Thomas Aas", "Elaine Chen"],
        "email_activity": "20 emails | Active discussions",
        "action": "Contact Peter Leeson/Andrew Jones - BNRG project active since Oct 2024"
    },
    {
        "id": "4855", "name": "Flynn Solar Farm Connection Studies",
        "client": "ib vogt Development Australia Pty", "value": 150000, "currency": "AUD",
        "prob": 20, "expected": 14948, "start": "2024-03-04", "target": "2027-01-01",
        "type": "Solar", "priority": "HIGH - 20%",
        "contacts": ["invoiceapac@ibvogt.com", "dan.halperin@ibvogt.com"],
        "phones": ["0749254542", "0749274360", "0749223613"],
        "names": ["Dan Halperin"],
        "email_activity": "6 emails | Invoice/billing",
        "action": "Contact Dan Halperin - billing emails only, need project update"
    },
    {
        "id": "4664", "name": "Woolsthorpe WF Variation - 5.3.9 Due Diligence",
        "client": "Shanghai Electric Australia Pty Ltd", "value": 25800, "currency": "AUD",
        "prob": 20, "expected": 2571, "start": "2024-01-09", "target": "2027-01-01",
        "type": "Wind", "priority": "HIGH - 20%",
        "contacts": [], "phones": [], "names": [],
        "email_activity": "NO EMAILS FOUND",
        "action": "Find contact - small value but 20% probability"
    },
    {
        "id": "5677", "name": "Inverell BESS RO Studies",
        "client": "SOUTH ENERGY PTY LTD", "value": 625100, "currency": "AUD",
        "prob": 10, "expected": 31146, "start": "2025-06-16", "target": "2027-01-01",
        "type": "BESS", "priority": "MEDIUM - 10%",
        "contacts": [], "phones": [], "names": [],
        "email_activity": "NO EMAILS FOUND",
        "action": "HIGHEST VALUE 10% project - need contact urgently (starts Jun 2025)"
    },
    {
        "id": "6744", "name": "Emu Park BESS R1 Connection Studies",
        "client": "Metlen Energy and Metals", "value": 599200, "currency": "AUD",
        "prob": 10, "expected": 29856, "start": "2025-09-15", "target": "2027-02-01",
        "type": "BESS", "priority": "MEDIUM - 10%",
        "contacts": [], "phones": [], "names": [],
        "email_activity": "NO EMAILS FOUND",
        "action": "2nd highest value - starts Sep 2025, need contact"
    },
    {
        "id": "5043", "name": "Tabulam Solar Farm & BESS",
        "client": "ELGIN ENERGY PTY LTD", "value": 576100, "currency": "AUD",
        "prob": 10, "expected": 28705, "start": "2024-05-07", "target": "2027-01-01",
        "type": "Solar", "priority": "MEDIUM - 10%",
        "contacts": ["kieran.kelly@elgin.com", "shane.slattery@elgin-energy.com", "derick.lima@elgin.com"],
        "phones": ["0341232310", "0387780382", "+61 0404 042 094"],
        "names": ["Shane Slattery", "Gururaja Asrolli", "Kieran Kelly"],
        "email_activity": "20 emails | Very active",
        "action": "Contact Shane Slattery/Kieran Kelly - active Tabulam project"
    },
    {
        "id": "504", "name": "Castle Doyle Wind Farm",
        "client": "Sirius Energy Australia Pty Ltd", "value": 570000, "currency": "AUD",
        "prob": 10, "expected": 28401, "start": "2024-04-13", "target": "2027-01-01",
        "type": "Wind", "priority": "MEDIUM - 10%",
        "contacts": [], "phones": [], "names": [],
        "email_activity": "NO EMAILS FOUND",
        "action": "Find Sirius contact - 2 projects worth $1.14M total"
    },
    {
        "id": "680AU", "name": "Bethungra Wind Farm",
        "client": "Sirius Energy Australia Pty Ltd", "value": 570000, "currency": "AUD",
        "prob": 10, "expected": 28401, "start": "2024-04-13", "target": "2027-01-01",
        "type": "Wind", "priority": "MEDIUM - 10%",
        "contacts": [], "phones": [], "names": [],
        "email_activity": "NO EMAILS FOUND",
        "action": "Same as Castle Doyle - Sirius has 2 wind farms"
    },
    {
        "id": "5147", "name": "Uranquinty AVR Replacement",
        "client": "Origin Energy Power Limited", "value": 400000, "currency": "AUD",
        "prob": 10, "expected": 19930, "start": "2024-10-12", "target": "2027-01-01",
        "type": "Grid", "priority": "MEDIUM - 10%",
        "contacts": ["meg.holding@originenergy.com.au"],
        "phones": ["0283717915", "0420088509", "0437 956 948"],
        "names": ["Meg Holding"],
        "email_activity": "20+ emails | 5.3.9 studies",
        "action": "Contact Meg Holding - Origin has 3 projects ($1.33M total)"
    },
    {
        "id": "5676", "name": "Shoalhaven Control Scheme Replacement",
        "client": "Origin Energy Power Limited", "value": 400000, "currency": "AUD",
        "prob": 10, "expected": 19930, "start": "2024-10-12", "target": "2027-01-01",
        "type": "Grid", "priority": "MEDIUM - 10%",
        "contacts": ["meg.holding@originenergy.com.au"],
        "phones": ["0283717915", "0420088509"],
        "names": ["Meg Holding"],
        "email_activity": "Active | 5.3.9 studies",
        "action": "Same contact as Uranquinty - Meg Holding"
    },
    {
        "id": "5520", "name": "Hydrogen Plant Connection Studies 1",
        "client": "LROA", "value": 275800, "currency": "MYR",
        "prob": 10, "expected": 5012, "start": "2025-06-25", "target": "2027-01-01",
        "type": "Hydrogen", "priority": "MEDIUM - 10% Malaysia",
        "contacts": [], "phones": [], "names": [],
        "email_activity": "NO EMAILS FOUND",
        "action": "Malaysia project - check LRQA contacts for LROA connection"
    },
    {
        "id": "6521", "name": "Hydrogen Plant Connection Studies 2",
        "client": "LRQA", "value": 275800, "currency": "MYR",
        "prob": 10, "expected": 5012, "start": "2025-06-25", "target": "2027-01-01",
        "type": "Hydrogen", "priority": "MEDIUM - 10% Malaysia",
        "contacts": ["christopher.spencer@vysusgroup.com", "amani.syafiqah@vysusgroup.com"],
        "phones": ["+6018 205 0225"],
        "names": ["Christopher Spencer"],
        "email_activity": "8 emails | KL meet-up",
        "action": "Contact Christopher Spencer - Malaysia hydrogen projects"
    },
]

def print_actionable_table():
    """Print table sorted by urgency/value for client chasing"""

    print("\n" + "="*160)
    print("ACTIONABLE CLIENT CONTACT TABLE - GRID & POWER SYSTEMS ADVISORY")
    print("Chris Marinelli | 15 Projects | AUD $5.85M Total | $396K Expected Value")
    print("="*160 + "\n")

    # Sort by: 1) Has contacts (no=urgent), 2) Probability desc, 3) Value desc
    def sort_key(p):
        has_contact = 1 if p['contacts'] else 0  # No contact = 0 = urgent
        return (has_contact, -p['prob'], -p['value'])

    sorted_projects = sorted(projects, key=sort_key)

    # Group by urgency
    urgent = [p for p in sorted_projects if not p['contacts']]
    has_contacts = [p for p in sorted_projects if p['contacts']]

    print(">>> URGENT: NO CONTACT INFO FOUND (8 clients) <<<")
    print("-"*160)
    print_project_group(urgent)

    print("\n>>> ACTIVE: CONTACTS AVAILABLE (5 clients) <<<")
    print("-"*160)
    print_project_group(has_contacts)

    # Summary by client
    print("\n" + "="*160)
    print("QUICK REFERENCE - BY CLIENT")
    print("="*160 + "\n")

    client_summary = {}
    for p in projects:
        client = p['client']
        if client not in client_summary:
            client_summary[client] = {
                'projects': [],
                'total_value': 0,
                'contacts': p['contacts'],
                'phones': p['phones'],
                'names': p['names']
            }
        client_summary[client]['projects'].append(f"{p['id']}: {p['name'][:40]}")
        if p['currency'] == 'AUD':
            client_summary[client]['total_value'] += p['value']

    for client, data in sorted(client_summary.items(), key=lambda x: -x[1]['total_value']):
        print(f"{client}")
        print(f"  Total Value: ${data['total_value']:,.0f} | Projects: {len(data['projects'])}")
        if data['contacts']:
            print(f"  PRIMARY CONTACT: {data['contacts'][0]}")
            if data['names']:
                print(f"  Name: {data['names'][0]}")
            if data['phones']:
                print(f"  Phone: {data['phones'][0]}")
        else:
            print(f"  *** NO CONTACT FOUND - SEARCH NEEDED ***")
        print(f"  Projects: {'; '.join(data['projects'][:3])}")
        print()

    print("="*160)

def print_project_group(project_list):
    """Print formatted project rows"""
    for p in project_list:
        print(f"\n[{p['id']}] {p['name']}")
        print(f"     Client: {p['client']} | Value: {p['currency']} ${p['value']:,.0f} | Priority: {p['priority']}")
        print(f"     Timeline: {p['start']} to {p['target']} | Type: {p['type']}")

        if p['contacts']:
            print(f"     [+] EMAIL: {', '.join(p['contacts'][:2])}")
            if len(p['contacts']) > 2:
                print(f"            (+{len(p['contacts'])-2} more: {', '.join(p['contacts'][2:4])})")
        else:
            print(f"     [!] NO EMAIL CONTACT")

        if p['phones']:
            print(f"     [+] PHONE: {', '.join(p['phones'][:2])}")
        else:
            print(f"     [!] NO PHONE")

        if p['names']:
            print(f"     [+] NAMES: {', '.join(p['names'][:3])}")

        print(f"     Email Activity: {p['email_activity']}")
        print(f"     >>> ACTION: {p['action']}")
        print("     " + "-"*150)

if __name__ == '__main__':
    print_actionable_table()
