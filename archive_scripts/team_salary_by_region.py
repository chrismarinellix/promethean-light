"""Team Capabilities and Salary Report by Region"""

import sys
import io

# Fix Windows console encoding
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

from mydata.summaries import get_australia_staff_summary, get_india_staff_summary
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text

console = Console()

# Salary Budget Ranges
BUDGET_RANGES = {
    "Australia": {
        "P.S Engineer": "AUD 90K - 150K",
        "Senior P.S Engineer": "AUD 140K - 170K",
        "Lead P.S Engineer": "AUD 170K - 200K",
        "Principal P.S Engineer": "AUD 200K+"
    },
    "India": {
        "P.S Engineer": "INR 10L - 25L",
        "Senior P.S Engineer": "INR 25L - 40L",
        "Lead P.S Engineer": "INR 40L - 50L",
        "Principal P.S Engineer": "INR 50L+"
    },
    "Malaysia": {
        "P.S Engineer": "MYR 95K - 170K",
        "Senior P.S Engineer": "MYR 150K - 220K",
        "Lead P.S Engineer": "MYR 200K - 300K",
        "Principal P.S Engineer": "MYR 300K+"
    }
}

# Header
console.print("\n")
console.print(Panel.fit(
    "[bold cyan]APAC Team Capabilities & Salary Report[/bold cyan]\n"
    "[dim]By Region - Current Staff vs. Budget Guidelines[/dim]",
    border_style="cyan"
))

# ============= AUSTRALIA =============
console.print("\n[bold green]=== AUSTRALIA (13 staff) ===[/bold green]\n")

aus_data = get_australia_staff_summary()
aus_table = Table(show_header=True, header_style="bold cyan", title="Current Australia Team")
aus_table.add_column("Name", style="white", width=28)
aus_table.add_column("Position", style="magenta", width=28)
aus_table.add_column("Base Salary", style="green", justify="right", width=12)
aus_table.add_column("w/Bonus", style="yellow", justify="right", width=12)
aus_table.add_column("Status", style="red", width=12)

for s in aus_data['staff']:
    status = "RESIGNED" if "RESIGNED" in s['position'] else "Active"
    bonus = s.get('total', s['salary'])

    aus_table.add_row(
        s['name'],
        s['position'].replace(" [RESIGNED]", ""),
        s['salary'],
        bonus if bonus != s['salary'] else "-",
        status
    )

console.print(aus_table)

# Australia Budget Guidelines
aus_budget_table = Table(show_header=True, header_style="bold yellow", title="Australia Salary Budget Guidelines")
aus_budget_table.add_column("Level", style="cyan", width=25)
aus_budget_table.add_column("Salary Range", style="green", width=20)

for level, range_val in BUDGET_RANGES["Australia"].items():
    aus_budget_table.add_row(level, range_val)

console.print("\n")
console.print(aus_budget_table)
console.print(f"\n[dim]$ Staff with retention bonuses: {aus_data['with_retention_bonus']}/13[/dim]")
console.print(f"[dim]Note: {aus_data['notes']}[/dim]")

# ============= INDIA =============
console.print("\n\n[bold blue]=== INDIA (7 staff) ===[/bold blue]\n")

india_data = get_india_staff_summary()
india_table = Table(show_header=True, header_style="bold cyan", title="Current India Team")
india_table.add_column("Name", style="white", width=28)
india_table.add_column("Level", style="magenta", width=18)
india_table.add_column("CTC (INR)", style="green", justify="right", width=14)
india_table.add_column("CTC (AUD)", style="blue", justify="right", width=12)
india_table.add_column("Retention", style="yellow", width=15)

for s in india_data['staff']:
    india_table.add_row(
        s['name'],
        s['level'],
        s['ctc_inr'],
        s['ctc_aud'],
        s['retention_bonus']
    )

console.print(india_table)

# India Budget Guidelines
india_budget_table = Table(show_header=True, header_style="bold yellow", title="India Salary Budget Guidelines")
india_budget_table.add_column("Level", style="cyan", width=25)
india_budget_table.add_column("Salary Range", style="green", width=20)

for level, range_val in BUDGET_RANGES["India"].items():
    india_budget_table.add_row(level, range_val)

console.print("\n")
console.print(india_budget_table)
console.print(f"\n[dim]$ Staff with retention bonuses: {india_data['with_retention_bonus']}/7[/dim]")
console.print(f"[dim]Calendar: Retention bonuses expire: {india_data['retention_bonus_expires']}[/dim]")

# ============= MALAYSIA =============
console.print("\n\n[bold magenta]=== MALAYSIA ===[/bold magenta]\n")

malaysia_budget_table = Table(show_header=True, header_style="bold yellow", title="Malaysia Salary Budget Guidelines")
malaysia_budget_table.add_column("Level", style="cyan", width=25)
malaysia_budget_table.add_column("Salary Range", style="green", width=20)

for level, range_val in BUDGET_RANGES["Malaysia"].items():
    malaysia_budget_table.add_row(level, range_val)

console.print(malaysia_budget_table)
console.print("\n[dim]Info: 1 Malaysia staff member (Amani) with 10% retention bonus (26K MYR)[/dim]")

# ============= SUMMARY =============
console.print("\n\n[bold white]=== REGIONAL SUMMARY ===[/bold white]\n")

summary_table = Table(show_header=True, header_style="bold cyan")
summary_table.add_column("Region", style="cyan", width=15)
summary_table.add_column("Total Staff", style="green", justify="center", width=12)
summary_table.add_column("w/Retention Bonus", style="yellow", justify="center", width=18)
summary_table.add_column("Capabilities", style="magenta", width=45)

summary_table.add_row(
    "Australia",
    "13",
    "6 (46%)",
    "Leadership, Principal/Lead Engineers, PS Engineers"
)
summary_table.add_row(
    "India",
    "7",
    "2 (29%)",
    "Senior & Mid-level Engineers"
)
summary_table.add_row(
    "Malaysia",
    "1",
    "1 (100%)",
    "Engineering capability (details TBD)"
)
summary_table.add_row(
    "[bold]TOTAL[/bold]",
    "[bold]21[/bold]",
    "[bold]9 (43%)[/bold]",
    "[bold]-[/bold]"
)

console.print(summary_table)

# Hiring Requirements
console.print("\n")
console.print(Panel(
    "[bold yellow]Hiring Requirements[/bold yellow]\n\n"
    "• Minimum experience for junior role: 2-3 years\n"
    "• Exception: May consider more junior candidates when hiring a batch of seniors\n"
    "• All salaries paid in respective currency based on location of work",
    title="Policy Guidelines",
    border_style="yellow"
))

console.print("\n")
