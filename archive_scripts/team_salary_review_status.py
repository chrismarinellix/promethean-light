from mydata.summaries import get_australia_staff_summary, get_india_staff_summary
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
import sys
import locale

# Fix Windows encoding issues
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

console = Console(force_terminal=True)

# Get data
aus_data = get_australia_staff_summary()
india_data = get_india_staff_summary()

# Separate Australia staff
aus_with_bonus = []
aus_need_review = []
for staff in aus_data['staff']:
    if staff.get('retention_bonus'):
        aus_with_bonus.append(staff)
    else:
        aus_need_review.append(staff)

# Separate India staff
india_with_bonus = []
india_need_review = []
for staff in india_data['staff']:
    if staff.get('retention_bonus') != "None":
        india_with_bonus.append(staff)
    else:
        india_need_review.append(staff)

# Summary Panel
summary_text = Text()
summary_text.append(f"Total Team Members: {aus_data['total_count'] + india_data['total_count']}\n", style="bold white")
summary_text.append(f"  Australia: {aus_data['total_count']} | India: {india_data['total_count']}\n\n", style="cyan")
summary_text.append(f"Recently Given Pay Rises: {len(aus_with_bonus) + len(india_with_bonus)}\n", style="bold green")
summary_text.append(f"  Australia: {len(aus_with_bonus)} | India: {len(india_with_bonus)}\n\n", style="green")
summary_text.append(f"Need Salary Review: {len(aus_need_review) + len(india_need_review)}\n", style="bold yellow")
summary_text.append(f"  Australia: {len(aus_need_review)} | India: {len(india_need_review)}", style="yellow")

console.print(Panel(summary_text, title="Team Salary Review Status", border_style="bold blue"))

# Table 1: Staff with Recent Pay Rises (Retention Bonuses)
print("\n")
table_bonus = Table(title="Staff with Recent Pay Rises (Retention Bonuses)", show_header=True, header_style="bold green")
table_bonus.add_column("Region", style="cyan", width=10)
table_bonus.add_column("ID", style="dim", width=8)
table_bonus.add_column("Name", style="white", width=25)
table_bonus.add_column("Position", style="magenta", width=28)
table_bonus.add_column("Base Salary", style="green", justify="right", width=12)
table_bonus.add_column("Bonus", style="yellow", justify="center", width=8)
table_bonus.add_column("Total w/Bonus", style="bold green", justify="right", width=14)
table_bonus.add_column("Expires", style="red", justify="center", width=10)
table_bonus.add_column("Status", style="red", width=12)

# Add Australia staff with bonuses
for s in aus_with_bonus:
    status = "RESIGNED" if "RESIGNED" in s['position'] else "Active"
    table_bonus.add_row(
        "AUS",
        s['id'],
        s['name'],
        s['position'].replace(" [RESIGNED]", ""),
        s['salary'],
        s.get('retention_bonus', '-'),
        s.get('total', s['salary']),
        s.get('expires', '-'),
        status
    )

# Add India staff with bonuses
for s in india_with_bonus:
    table_bonus.add_row(
        "INDIA",
        s['id'],
        s['name'],
        s['level'],
        s['ctc_inr'] + " / " + s['ctc_aud'],
        s.get('retention_bonus', '-').split('(')[0].strip(),
        s['total_with_bonus_inr'] + " / " + s['total_with_bonus_aud'],
        s.get('bonus_until', '-'),
        "Active"
    )

console.print(table_bonus)

# Table 2: Staff Needing Salary Review (DETAILED)
print("\n")
table_review = Table(title="Staff Requiring Salary Review - DETAILED ANALYSIS", show_header=True, header_style="bold yellow")
table_review.add_column("Region", style="cyan", width=10)
table_review.add_column("ID", style="dim", width=8)
table_review.add_column("Name", style="white", width=25)
table_review.add_column("Position/Level", style="magenta", width=28)
table_review.add_column("Current Salary", style="yellow", justify="right", width=20)
table_review.add_column("Status", style="red", width=12)
table_review.add_column("Notes & Priority", style="white", width=40)

# Add Australia staff needing review
for s in aus_need_review:
    # Determine priority and notes based on salary level
    salary_num = int(s['salary'].replace('$', '').replace(',', ''))
    position = s['position'].replace(" [RESIGNED]", "")
    status = "RESIGNED" if "RESIGNED" in s['position'] else "Active"

    if status == "RESIGNED":
        priority = "N/A - Resigned"
        notes = "Staff member has resigned"
    elif salary_num >= 160000:
        priority = "HIGH PRIORITY"
        notes = f"Senior staff ({position}) - no bonus. Market retention risk."
    elif salary_num >= 100000:
        priority = "MEDIUM PRIORITY"
        notes = f"Mid-level engineer - consider performance review & market comparison."
    else:
        priority = "REVIEW NEEDED"
        notes = f"Entry/junior level - annual review recommended."

    table_review.add_row(
        "AUS",
        s['id'],
        s['name'],
        position,
        s['salary'],
        status,
        f"[{priority}] {notes}"
    )

# Add India staff needing review
for s in india_need_review:
    level = s['level']
    ctc_display = s['ctc_inr'] + " (" + s['ctc_aud'] + ")"

    if "Senior" in level:
        priority = "HIGH PRIORITY"
        notes = f"Senior engineer - no bonus. Consider retention strategy."
    elif "Mid" in level:
        priority = "MEDIUM PRIORITY"
        notes = f"Mid-level engineer - review against India market rates."
    else:
        priority = "REVIEW NEEDED"
        notes = f"Junior level - standard annual review cycle."

    table_review.add_row(
        "INDIA",
        s['id'],
        s['name'],
        level,
        ctc_display,
        "Active",
        f"[{priority}] {notes}"
    )

console.print(table_review)

# Additional context
print("\n")
context_text = Text()
context_text.append("ADDITIONAL CONTEXT:\n", style="bold underline white")
context_text.append(f"\n{aus_data.get('notes', '')}\n", style="italic cyan")
context_text.append(f"\nRetention Bonus Expiry Dates:\n", style="bold white")
context_text.append(f"  - Feb 2026: {aus_data['retention_bonus_expires_feb_2026']} staff\n", style="yellow")
context_text.append(f"  - Aug 2026: {aus_data['retention_bonus_expires_aug_2026']} AUS staff + 2 India staff\n", style="yellow")
context_text.append(f"\nNext Actions Required:\n", style="bold white")
context_text.append(f"  1. Schedule performance reviews for {len(aus_need_review) + len(india_need_review)} staff without bonuses\n", style="green")
context_text.append(f"  2. Conduct market salary comparisons for HIGH PRIORITY staff\n", style="green")
context_text.append(f"  3. Plan retention strategy for Feb 2026 bonus expirations (3 months away)\n", style="green")

console.print(Panel(context_text, border_style="bold blue"))
