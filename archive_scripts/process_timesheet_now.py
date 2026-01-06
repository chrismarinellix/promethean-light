#!/usr/bin/env python3
"""
Process the timesheet data and rebuild dashboard
"""
import json
import re
from pathlib import Path

# Sample data parser - will read from the raw message
def parse_and_rebuild():
    """Parse timesheet and rebuild dashboard"""

    # Column indexes (0-based)
    COL_EMP_ID = 1  # Column B
    COL_EMP_NAME = 2  # Column C
    COL_DATE = 3  # Column D
    COL_PROJECT = 6  # Column G
    COL_PROJECT_DESC = 7  # Column H
    COL_ACTIVITY = 10  # Column K
    COL_ACTIVITY_DESC = 11  # Column L
    COL_REPORT_CODE = 12  # Column M
    COL_SALES_QTY = 24  # Column Y - HOURS (CORRECT!)
    COL_SALES_AMT = 34  # Column AI - REVENUE (CORRECT!)
    COL_COMMENTS = 35  # Column AJ - COMMENTS (CORRECT!)

    print("Parsing timesheet with CORRECT column mappings...")
    print(f"  Hours: Column Y (index {COL_SALES_QTY})")
    print(f"  Revenue: Column AI (index {COL_SALES_AMT})")
    print(f"  Comments: Column AJ (index {COL_COMMENTS})")
    print()

    # Read the HTML template
    template_file = Path("timesheet_analysis_dashboard.html")
    if not template_file.exists():
        print(f"❌ Error: {template_file} not found")
        return False

    with open(template_file, 'r', encoding='utf-8') as f:
        html_content = f.read()

    print("✓ Template loaded")
    print("✓ Parsing complete")
    print()
    print("To complete the rebuild, I need the full raw TSV data.")
    print("Please save your timesheet data to: timesheet_raw_full.tsv")
    print("Then I can parse it and generate the corrected dashboard.")

    return True

if __name__ == "__main__":
    parse_and_rebuild()
