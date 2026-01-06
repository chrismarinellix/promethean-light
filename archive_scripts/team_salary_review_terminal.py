from mydata.summaries import get_australia_staff_summary, get_india_staff_summary
from rich.console import Console
from rich.table import Table
import sys

# Fix Windows encoding issues
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

console = Console(force_terminal=True)

# Get data
aus_data = get_australia_staff_summary()
india_data = get_india_staff_summary()

# Separate staff
aus_with_bonus = [s for s in aus_data['staff'] if s.get('retention_bonus')]
aus_need_review = [s for s in aus_data['staff'] if not s.get('retention_bonus')]
india_with_bonus = [s for s in india_data['staff'] if s.get('retention_bonus') != "None"]
india_need_review = [s for s in india_data['staff'] if s.get('retention_bonus') == "None"]

# Summary
print("\n" + "="*100)
print("TEAM SALARY REVIEW STATUS".center(100))
print("="*100)
print(f"\nTotal Team: 20 (AUS: 13 | India: 7)")
print(f"With Recent Pay Rises: 8 (AUS: {len(aus_with_bonus)} | India: {len(india_with_bonus)})")
print(f"Need Review: 12 (AUS: {len(aus_need_review)} | India: {len(india_need_review)})")
print("="*100 + "\n")

# Table 1: Staff with Recent Pay Rises
table1 = Table(title="STAFF WITH RECENT PAY RISES (Retention Bonuses)", show_header=True, header_style="bold green", width=150)
table1.add_column("Reg", width=5)
table1.add_column("ID", width=8)
table1.add_column("Name", width=22)
table1.add_column("Position/Level", width=25)
table1.add_column("Base Salary", justify="right", width=15)
table1.add_column("Bonus", justify="center", width=8)
table1.add_column("Total Package", justify="right", width=15)
table1.add_column("Expires", justify="center", width=9)
table1.add_column("Status", width=10)

for s in aus_with_bonus:
    status = "RESIGNED" if "RESIGNED" in s['position'] else "Active"
    table1.add_row(
        "AUS",
        s['id'],
        s['name'],
        s['position'].replace(" [RESIGNED]", ""),
        s['salary'],
        "10%",
        s.get('total', s['salary']),
        s.get('expires', '-'),
        status
    )

for s in india_with_bonus:
    table1.add_row(
        "IND",
        s['id'],
        s['name'],
        s['level'],
        s['ctc_aud'],
        "10%",
        s['total_with_bonus_aud'],
        s.get('bonus_until', '-'),
        "Active"
    )

console.print(table1)
print("\n")

# Table 2: HIGH PRIORITY Reviews
table2 = Table(title="HIGH PRIORITY - Staff Requiring Immediate Review (6 staff)", show_header=True, header_style="bold red", width=150)
table2.add_column("Reg", width=5)
table2.add_column("ID", width=8)
table2.add_column("Name", width=22)
table2.add_column("Position/Level", width=25)
table2.add_column("Current Salary", justify="right", width=15)
table2.add_column("Key Issue", width=55)

# High priority Australia
high_priority_aus = [
    {"staff": s, "issue": "Senior leadership without retention bonus. Market retention risk."}
    for s in aus_need_review if int(s['salary'].replace('$', '').replace(',', '')) >= 160000
]

for item in high_priority_aus:
    s = item['staff']
    table2.add_row(
        "AUS",
        s['id'],
        s['name'],
        s['position'],
        s['salary'],
        item['issue']
    )

# High priority India
high_priority_india = [
    {"staff": s, "issue": "Internal equity: Other senior/mid-senior staff have 10% bonuses."}
    for s in india_need_review if "Senior" in s['level']
]

for item in high_priority_india:
    s = item['staff']
    table2.add_row(
        "IND",
        s['id'],
        s['name'],
        s['level'],
        s['ctc_aud'],
        item['issue']
    )

console.print(table2)
print("\n")

# Table 3: MEDIUM PRIORITY Reviews
table3 = Table(title="MEDIUM PRIORITY - Staff Requiring Review (4 staff)", show_header=True, header_style="bold yellow", width=150)
table3.add_column("Reg", width=5)
table3.add_column("ID", width=8)
table3.add_column("Name", width=22)
table3.add_column("Position/Level", width=25)
table3.add_column("Current Salary", justify="right", width=15)
table3.add_column("Recommendation", width=55)

# Medium priority Australia
medium_priority_aus = [s for s in aus_need_review if 100000 <= int(s['salary'].replace('$', '').replace(',', '')) < 160000]

for s in medium_priority_aus:
    table3.add_row(
        "AUS",
        s['id'],
        s['name'],
        s['position'],
        s['salary'],
        "Mid-level specialist. Performance review and market comparison."
    )

# Medium priority India
medium_priority_india = [s for s in india_need_review if "Mid" in s['level'] and "Senior" not in s['level']]

for s in medium_priority_india:
    table3.add_row(
        "IND",
        s['id'],
        s['name'],
        s['level'],
        s['ctc_aud'],
        "Review against India market rates for similar experience."
    )

console.print(table3)
print("\n")

# Table 4: STANDARD Reviews
table4 = Table(title="STANDARD REVIEW NEEDED (2 staff)", show_header=True, header_style="bold cyan", width=150)
table4.add_column("Reg", width=5)
table4.add_column("ID", width=8)
table4.add_column("Name", width=22)
table4.add_column("Position/Level", width=25)
table4.add_column("Current Salary", justify="right", width=15)
table4.add_column("Recommendation", width=55)

# Standard reviews
standard_aus = [s for s in aus_need_review if int(s['salary'].replace('$', '').replace(',', '')) < 100000]

for s in standard_aus:
    table4.add_row(
        "AUS",
        s['id'],
        s['name'],
        s['position'],
        s['salary'],
        "Annual review cycle to ensure competitive positioning."
    )

console.print(table4)
print("\n")

# Critical Actions
print("="*100)
print("CRITICAL ACTIONS REQUIRED".center(100))
print("="*100)
print("\nIMMEDIATE (Next 30 Days):")
print("  1. Schedule performance reviews for all 12 staff without retention bonuses")
print("  2. Conduct market salary comparisons for 6 HIGH PRIORITY staff")
print("  3. Address internal equity issues:")
print("     - India: 3 mid-senior engineers without bonuses (vs Owais with bonus)")
print("     - AUS: Komal Gaikwad without bonus (vs other senior/leads with bonuses)")

print("\nSHORT TERM (Feb 2026 - 3 months away):")
print("  1. Plan retention strategy for Feb 2026 bonus expirations:")
print("     - Naveenkumar Rajagopal: $230K + 10% ($23K)")
print("     - Eduardo Jr Laygo: $193K + 10% ($19.3K)")
print("     - Total at risk: $42,300/year")

print("\nMEDIUM TERM (Aug 2026 - 9 months away):")
print("  1. Prepare for Aug 2026 bonus expirations (5 staff):")
print("     - Ajith, Md Rahman, Zabir (AUS): ~$56.5K total")
print("     - Faraz, Owais (India): ~$18.4K AUD equivalent")
print("     - Total at risk: ~$75K/year")

print("\n" + "="*100)
print("FINANCIAL IMPACT".center(100))
print("="*100)
print(f"\nCurrent Annual Retention Bonus Investment: ~$117,221 AUD")
print(f"  - Australia (6 staff): $98,800")
print(f"  - India (2 staff): ~$18,421 AUD equivalent")
print(f"\nBonuses at Risk if Not Renewed:")
print(f"  - Feb 2026: $42,300/year (2 staff)")
print(f"  - Aug 2026: $74,921/year (5 staff)")
print("="*100 + "\n")
