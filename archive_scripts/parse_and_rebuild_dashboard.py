#!/usr/bin/env python3
"""
Parse the raw timesheet TSV and rebuild the dashboard with correct column mappings.

Usage:
    1. Save your raw timesheet data to: timesheet_raw_data.tsv
    2. Run: python parse_and_rebuild_dashboard.py
    3. Open: timesheet_analysis_dashboard_CORRECTED.html
"""
import csv
import json
from pathlib import Path

def parse_timesheet(tsv_file):
    """Parse TSV file using correct column mappings"""

    # Column indexes (0-based)
    COL_EMP_ID = 1  # Column B
    COL_EMP_NAME = 2  # Column C
    COL_DATE = 3  # Column D
    COL_PROJECT = 6  # Column G
    COL_PROJECT_DESC = 7  # Column H
    COL_ACTIVITY = 10  # Column K
    COL_ACTIVITY_DESC = 11  # Column L
    COL_REPORT_CODE = 12  # Column M
    COL_SALES_QTY = 24  # Column Y - HOURS (correct!)
    COL_SALES_AMT = 34  # Column AI - REVENUE (correct!)
    COL_COMMENTS = 35  # Column AJ - COMMENTS (correct!)

    entries = []

    with open(tsv_file, 'r', encoding='utf-8') as f:
        reader = csv.reader(f, delimiter='\t')
        header = next(reader)  # Skip header

        for row in reader:
            if len(row) < 36:  # Skip incomplete rows
                continue

            try:
                entry = {
                    'employee': row[COL_EMP_NAME].strip(),
                    'empId': row[COL_EMP_ID].strip(),
                    'date': row[COL_DATE].strip(),
                    'project': row[COL_PROJECT].strip(),
                    'projectDesc': row[COL_PROJECT_DESC].strip(),
                    'activity': row[COL_ACTIVITY].strip(),
                    'activityDesc': row[COL_ACTIVITY_DESC].strip(),
                    'reportCode': row[COL_REPORT_CODE].strip(),
                    'hours': float(row[COL_SALES_QTY]) if row[COL_SALES_QTY] else 0,
                    'revenue': float(row[COL_SALES_AMT]) if row[COL_SALES_AMT] else 0,
                    'comments': row[COL_COMMENTS].strip() if len(row) > COL_COMMENTS else ''
                }
                entries.append(entry)
            except (ValueError, IndexError) as e:
                print(f"Warning: Skipping row due to error: {e}")
                continue

    return entries

def generate_dashboard_html(entries, output_file):
    """Generate the corrected dashboard HTML"""

    # Read the template (use existing dashboard as base)
    template_file = Path("timesheet_analysis_dashboard.html")

    if not template_file.exists():
        print(f"Error: Template file not found: {template_file}")
        return False

    with open(template_file, 'r', encoding='utf-8') as f:
        html = f.read()

    # Convert entries to JavaScript format
    js_data = "const timesheetData = " + json.dumps(entries, indent=12) + ";"

    # Replace the old data with new data
    # Find the timesheetData array and replace it
    import re
    pattern = r'const timesheetData = \[.*?\];'
    html = re.sub(pattern, js_data, html, flags=re.DOTALL)

    # Write corrected dashboard
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html)

    print(f"✓ Dashboard generated: {output_file}")
    return True

def main():
    tsv_file = "timesheet_raw_data.tsv"
    output_file = "timesheet_analysis_dashboard_CORRECTED.html"

    if not Path(tsv_file).exists():
        print(f"Error: Please save your raw timesheet data to: {tsv_file}")
        print("The file should contain the tab-separated data you pasted earlier.")
        return

    print("Parsing timesheet data...")
    entries = parse_timesheet(tsv_file)

    print(f"✓ Parsed {len(entries)} timesheet entries")

    # Get unique employees
    employees = set(e['employee'] for e in entries)
    print(f"✓ Found {len(employees)} unique employees")

    print("\nGenerating corrected dashboard...")
    if generate_dashboard_html(entries, output_file):
        print(f"\n SUCCESS! Open {output_file} to view the corrected dashboard.")
        print("\nCorrections applied:")
        print("  ✓ Using Sales Quantity for hours (Column Y)")
        print("  ✓ Using Sales Amount for revenue (Column AI)")
        print("  ✓ Using Internal Comments (Column AJ)")
        print(f"  ✓ Showing all {len(employees)} employees")

if __name__ == "__main__":
    main()
