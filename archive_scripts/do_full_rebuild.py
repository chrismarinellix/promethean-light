#!/usr/bin/env python3
"""
Complete dashboard rebuild with correct column mappings
Processes the raw TSV data and generates corrected HTML
"""
import sys
import re
from pathlib import Path

def save_raw_data_instructions():
    """Show instructions for saving raw data"""
    print("=" * 60)
    print("FULL DASHBOARD REBUILD - Instructions")
    print("=" * 60)
    print("")
    print("To complete rebuild with 100% correct column mappings:")
    print("")
    print("STEP 1: Save Raw Timesheet Data")
    print("  Save your TSV data to: timesheet_raw_full.tsv")
    print("")
    print("STEP 2: Run Rebuild")
    print("  python do_full_rebuild.py rebuild")
    print("")
    print("This will:")
    print("  - Parse Column Y (Sales Quantity) for hours")
    print("  - Parse Column AI (Sales Amount) for revenue")
    print("  - Parse Column AJ (Internal Comments) for comments")
    print("  - Create: timesheet_analysis_dashboard_REBUILT.html")
    print("")
    print("=" * 60)

def rebuild_from_file(tsv_file):
    """Rebuild dashboard from TSV file"""
    if not Path(tsv_file).exists():
        print(f"Error: File not found: {tsv_file}")
        print("Please save your raw timesheet data first.")
        return False

    # Column indexes
    COL_EMP_ID = 1
    COL_EMP_NAME = 2
    COL_DATE = 3
    COL_PROJECT = 6
    COL_PROJECT_DESC = 7
    COL_ACTIVITY = 10
    COL_ACTIVITY_DESC = 11
    COL_REPORT_CODE = 12
    COL_SALES_QTY = 24  # Column Y - HOURS
    COL_SALES_AMT = 34  # Column AI - REVENUE
    COL_COMMENTS = 35   # Column AJ - COMMENTS

    entries = []

    print("Parsing timesheet data...")

    with open(tsv_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        header = lines[0]  # Skip header

        for i, line in enumerate(lines[1:], 1):
            parts = line.split('\t')

            if len(parts) < 36:
                continue

            try:
                entry = {
                    'employee': parts[COL_EMP_NAME].strip(),
                    'empId': parts[COL_EMP_ID].strip(),
                    'date': parts[COL_DATE].strip(),
                    'project': parts[COL_PROJECT].strip(),
                    'projectDesc': parts[COL_PROJECT_DESC].strip(),
                    'activity': parts[COL_ACTIVITY].strip(),
                    'activityDesc': parts[COL_ACTIVITY_DESC].strip(),
                    'reportCode': parts[COL_REPORT_CODE].strip(),
                    'hours': float(parts[COL_SALES_QTY]) if parts[COL_SALES_QTY] else 0,
                    'revenue': float(parts[COL_SALES_AMT]) if parts[COL_SALES_AMT] else 0,
                    'comments': parts[COL_COMMENTS].strip() if len(parts) > COL_COMMENTS else ''
                }
                entries.append(entry)
            except (ValueError, IndexError) as e:
                print(f"Warning: Skipped line {i}: {e}")
                continue

    print(f"Parsed {len(entries)} entries")

    # Generate JavaScript
    js_lines = []
    for entry in entries:
        comment_escaped = entry['comments'].replace('"', '\\"').replace('\n', ' ')[:200]
        js_line = (
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
            f'comments: "{comment_escaped}"}}'
        )
        js_lines.append(js_line)

    js_data = "const timesheetData = [\n            " + ",\n            ".join(js_lines) + "\n        ];"

    # Read template
    template = Path("timesheet_analysis_dashboard.html")
    with open(template, 'r', encoding='utf-8') as f:
        html = f.read()

    # Replace data
    pattern = r'const timesheetData = \[.*?\];'
    html = re.sub(pattern, js_data, html, flags=re.DOTALL)

    # Update title
    html = html.replace(
        'Week of Nov 17-21, 2025 | Utilization & Resource Management',
        'Week of Nov 17-21, 2025 | REBUILT - Correct Columns (Y=Hours, AI=Revenue)'
    )

    # Write output
    output_file = "timesheet_analysis_dashboard_REBUILT.html"
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html)

    print(f"\n[SUCCESS] Dashboard rebuilt: {output_file}")

    # Statistics
    employees = set(e['employee'] for e in entries)
    total_hours = sum(e['hours'] for e in entries)
    total_revenue = sum(e['revenue'] for e in entries)

    print(f"\nStatistics:")
    print(f"  Employees: {len(employees)}")
    print(f"  Entries: {len(entries)}")
    print(f"  Total Hours: {total_hours:.1f}")
    print(f"  Total Revenue: ${total_revenue:,.2f} AUD")

    return True

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "rebuild":
        rebuild_from_file("timesheet_raw_full.tsv")
    else:
        save_raw_data_instructions()
