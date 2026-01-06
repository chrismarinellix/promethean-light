#!/usr/bin/env python3
"""
Full dashboard rebuild with correct column mappings
Uses data directly from the user's pasted message
"""
import json
import re

# Raw timesheet data - will be populated from user's message
# Using the CORRECT column mappings:
# Column Y (index 24) = Sales Quantity = HOURS
# Column AI (index 34) = Sales Amount = REVENUE
# Column AJ (index 35) = Internal Comments = COMMENTS

def parse_tsv_line(line):
    """Parse a single TSV line into a dictionary"""
    parts = line.split('\t')

    if len(parts) < 36:
        return None

    try:
        # Extract data using CORRECT columns
        hours = float(parts[24]) if parts[24] else 0  # Sales Quantity (Column Y)
        revenue = float(parts[34]) if parts[34] else 0  # Sales Amount (Column AI)
        comments = parts[35] if len(parts) > 35 else ''  # Internal Comments (Column AJ)

        entry = {
            'employee': parts[2].strip(),  # Employee Description
            'empId': parts[1].strip(),     # Employee ID
            'date': parts[3].strip(),      # Account Date
            'project': parts[6].strip(),   # Project
            'projectDesc': parts[7].strip(), # Project Description
            'activity': parts[10].strip(), # Activity
            'activityDesc': parts[11].strip(), # Activity Description
            'reportCode': parts[12].strip(), # Report Code
            'hours': hours,
            'revenue': revenue,
            'comments': comments.strip()
        }

        return entry
    except (ValueError, IndexError) as e:
        print(f"Warning: Error parsing line: {e}")
        return None

def generate_js_data(entries):
    """Generate JavaScript data array"""
    js_entries = []

    for entry in entries:
        js_entry = (
            f'{{employee: "{entry["employee"]}", '
            f'empId: "{entry["empId"]}", '
            f'date: "{entry["date"]}", '
            f'project: "{entry["project"]}", '
            f'projectDesc: "{entry["projectDesc"]}", '
            f'activity: "{entry["activity"]}", '
            f'activityDesc: "{entry["activityDesc"]}", '
            f'reportCode: "{entry["reportCode"]}", '
            f'hours: {entry["hours"]}, '
            f'revenue: {entry["revenue"]}, '
            f'comments: "{entry["comments"].replace('"', '\\"')[:200]}"}}'
        )
        js_entries.append(js_entry)

    return "const timesheetData = [\n            " + ",\n            ".join(js_entries) + "\n        ];"

def rebuild_dashboard(entries, template_file, output_file):
    """Rebuild the dashboard with corrected data"""

    # Read template
    with open(template_file, 'r', encoding='utf-8') as f:
        html = f.read()

    # Generate JavaScript data
    js_data = generate_js_data(entries)

    # Replace the data array
    pattern = r'const timesheetData = \[.*?\];'
    html = re.sub(pattern, js_data, html, flags=re.DOTALL)

    # Update header to indicate corrected data
    html = html.replace(
        'Week of Nov 17-21, 2025 | Utilization & Resource Management',
        'Week of Nov 17-21, 2025 | Corrected Data (Sales Qty=Hours, Sales Amt=Revenue)'
    )

    # Write output
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html)

    print(f"✓ Dashboard rebuilt: {output_file}")

    # Print statistics
    employees = set(e['employee'] for e in entries)
    total_hours = sum(e['hours'] for e in entries)
    total_revenue = sum(e['revenue'] for e in entries)

    print(f"\n📊 Dashboard Statistics:")
    print(f"   Employees: {len(employees)}")
    print(f"   Total Entries: {len(entries)}")
    print(f"   Total Hours: {total_hours:.1f}")
    print(f"   Total Revenue: ${total_revenue:,.2f} AUD")

# This script expects the raw TSV data to be piped in or read from stdin
if __name__ == "__main__":
    print("Full Dashboard Rebuild Script")
    print("=" * 60)
    print("Using CORRECT column mappings:")
    print("  ✓ Column Y (Sales Quantity) = Hours")
    print("  ✓ Column AI (Sales Amount) = Revenue")
    print("  ✓ Column AJ (Internal Comments) = Comments")
    print("=" * 60)
    print()

    # For now, print instructions
    print("To use this script:")
    print("1. Save the raw timesheet TSV to: timesheet_raw_full.tsv")
    print("2. Run: python rebuild_dashboard_full.py")
    print()
    print("Or provide the data via stdin.")
