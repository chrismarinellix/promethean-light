import csv
from io import StringIO

# Paste the timesheet data here
timesheet_raw = """Invoiced	Employee	Employee Description	Account Date	Activity Seq	Activity Short Name	Project	Project Description	Sub Project	Sub Project Description	Activity	Activity Description	Report Code	Report Code Description	Report Code Type	Price Adjustment	Price Adjustment Description	Internal Quantity	Internal Price	Non Deductible Tax for Contractors	Overhead Price	Total Internal Price	Alternative Cost	Internal Amount	Sales Quantity	Currency Code	Currency Type	Sales Price Basis	Markup Price	Sales Price	Sales Price In Accounting Currency	Sales Amount Basis	Markup Amount	Sales Amount	Sales Amount In Accounting Currency	Internal Comments	Invoice Comments	Transaction Source	Invoicability	Invoice Status	Invoice Id	Invoice No	Organization Code	Create Cost Accounting	Approved	Cost Accounting Voucher Created	Correction Status	Report Code Group	Report Code Group Description	Day Confirmed	Billing Category	Billing Category Description	Customer	Customer Name	Registered By	Registered By Description	Jinsui Enabled	Imported to Payroll	Delivery Type ID	Delivery Type	Resource	Resource Description	Program	Program Description	Position	Position Description	Employee Category	Work Location	Work Location Description	Revenue Accounting Voucher Created	Customer Transaction Approved	Multi-Company Transaction Type	Multi-Company Reporting Company ID	Multi-Company Project Invoice No	Project Transaction Seq	Purchase Order No	PO Line Ref	PO Line No	PO Release No	Invoiced Quantity	Purchase Order Invoice Status	Internal Price in PO Currency	PO Currency Code	Invoicing Advice	Origin Key1	Origin Key2
No	470162	Naveenkumar Rajagopal	11/21/2025	100031422	GRD0500061.BILLABLE.TASK 2.15	GRD0500061	Birdwood Energy Reserve	BILLABLE	Birdwood Energy Reserve-Grid connection support 	TASK 2.15	Technical & Regulatory Connection Support (T&E) 	HOURLY	Hourly Charge Rate	Time			1	133.35	0	24.55	157.9	0	157.9	1	AUD	1	325	0	325	325	325	0	325	325	Internal discussion on Pending comments and PSCAD model issues		Project	Invoiceable	Not invoiced			GRD	Yes	No	No				Yes			605	Birdwood Energy Reserve Trust 	N.RAJAGOPAL	Naveenkumar Rajagopal	No	No			GRD-AU-PRINCIPAL ENGINEER	Principal Engineer			POS_1218	Principal Power Systems Engineer	Fixed Term Contract	MO	Main Office	No	No				836174													"""

# Parse TSV data
reader = csv.DictReader(StringIO(timesheet_raw), delimiter='\t')
data = list(reader)

# Get all unique employees from timesheet
employees_in_timesheet = set()
for row in data:
    emp_name = row.get('Employee Description', '').strip()
    emp_id = row.get('Employee', '').strip()
    if emp_name and emp_id:
        employees_in_timesheet.add(f"{emp_name} ({emp_id})")

print(f"Total unique employees in timesheet: {len(employees_in_timesheet)}")
print("\nEmployees in timesheet:")
for emp in sorted(employees_in_timesheet):
    print(f"  - {emp}")

# Known Australia staff from database
australia_staff = [
    "Chris Marinelli (470408)",
    "Anthony Morton (435865)",
    "Robby Palackal (470117)",
    "Naveenkumar Rajagopal (470162)",
    "Eduardo Jr Laygo (450639)",
    "Ajith Tennakoon (470???)",  # Need to find ID
    "Md Rahman (470305)",
    "Zabir Uddin Hussainy Syed (470479)",
    "Komal Gaikwad (470443)",
    "Dominic Moncada (470433)",
    "Khadija Kobra (470428)",
    "Hayden Brunjes (470434)",
    "Parthena Savvidis (470116)",
]

print("\n\nExpected Australia Staff:")
for emp in australia_staff:
    print(f"  - {emp}")
