#!/usr/bin/env python3
"""
Parse the correct timesheet data and identify missing employees
"""

# Column indexes (0-based)
COL_EMPLOYEE_ID = 1  # Column B: Employee
COL_EMPLOYEE_NAME = 2  # Column C: Employee Description
COL_DATE = 3  # Column D: Account Date
COL_PROJECT = 6  # Column G: Project
COL_PROJECT_DESC = 7  # Column H: Project Description
COL_ACTIVITY = 10  # Column K: Activity
COL_ACTIVITY_DESC = 11  # Column L: Activity Description
COL_REPORT_CODE = 12  # Column M: Report Code
COL_SALES_QUANTITY = 24  # Column Y: Sales Quantity (TOTAL HOURS)
COL_SALES_AMOUNT = 34  # Column AI: Sales Amount (REVENUE)
COL_INTERNAL_AMOUNT = 23  # Column X: Internal Amount
COL_INTERNAL_COMMENTS = 35  # Column AJ: Internal Comments (COMMENTS)

# Known Australia staff from database
australia_staff = {
    "470408": "Chris Marinelli",
    "435865": "Anthony Morton",
    "470117": "Robby Palackal",
    "470162": "Naveenkumar Rajagopal",
    "450639": "Eduardo Jr Laygo",
    "470305": "Md Momtazur Rahman",  # Md Rahman
    "470479": "Zabir Uddin Hussainy Syed",
    "470443": "Komal Gaikwad",
    "470433": "Dominic Joey Moncada",  # Dominic Moncada
    "470428": "Khadija Tul Kobra",  # Khadija Kobra
    "470434": "Hayden Brunjes",
    "470116": "Parthena Savvidis",
}

# Parse data from user's message - we'll extract employee IDs
employees_in_timesheet = set()

# Simplified check - just list unique employee IDs found
timesheet_employees = {
    "470162": "Naveenkumar Rajagopal",
    "480IN-61": "Mohammed Arif Kandanari Nathar",
    "470434": "Hayden Brunjes",
    "450639": "Eduardo Jr Laygo",
    "470443": "Komal Gaikwad",
    "622MY-63": "Muhammad Syafiq Ishamuddin",
    "435865": "Anthony Morton",
    "470433": "Dominic Joey Moncada",
    "470479": "Zabir Uddin Hussainy Syed",
    "470428": "Khadija Tul Kobra",
    "470408": "Chris Marinelli",
    "470116": "Parthena Savvidis",
    "470305": "Md Momtazur Rahman",
    "622MY-44": "Shahrul Azri Mohammad Faudzi",
    "622MY-52": "Amani Syafiqah binti Mohd Razif",
}

print("=== TIMESHEET ANALYSIS ===\n")
print(f"Total employees in timesheet: {len(timesheet_employees)}")
print("\nEmployees found in timesheet:")
for emp_id, name in sorted(timesheet_employees.items()):
    region = ""
    if emp_id.startswith("480IN"):
        region = " [INDIA]"
    elif emp_id.startswith("622MY"):
        region = " [MALAYSIA]"
    elif emp_id.startswith("4"):
        region = " [AUSTRALIA]"
    print(f"  {emp_id}: {name}{region}")

print("\n\n=== MISSING EMPLOYEES ===\n")
print("Australia staff expected but MISSING from timesheet:")
missing = []
for emp_id, name in australia_staff.items():
    if emp_id not in timesheet_employees:
        missing.append(f"  {emp_id}: {name}")

if missing:
    for m in missing:
        print(m)
else:
    print("  (None - all Australia staff have timesheets)")

# Check for Ajith
print("\n\nNOTE: Ajith Tennakoon was not found in timesheet or employee ID list.")
print("      Need to verify if Ajith worked this week.")
