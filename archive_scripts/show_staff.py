from mydata.summaries import get_australia_staff_summary
from rich.console import Console
from rich.table import Table

console = Console()
data = get_australia_staff_summary()

table = Table(title="Australia Staff (13 Total)", show_header=True, header_style="bold cyan")
table.add_column("ID", style="dim", width=8)
table.add_column("Name", style="white", width=25)
table.add_column("Position", style="magenta", width=28)
table.add_column("Base", style="green", justify="right", width=12)
table.add_column("w/Bonus", style="yellow", justify="right", width=12)
table.add_column("Status", style="red", width=10)

for s in data['staff']:
    status = "RESIGNED" if "RESIGNED" in s['position'] else ""
    bonus = s.get('total', s['salary'])
    has_bonus = "+" if bonus != s['salary'] else ""

    table.add_row(
        s['id'],
        s['name'],
        s['position'].replace(" [RESIGNED]", ""),
        s['salary'],
        f"{bonus} {has_bonus}",
        status
    )

console.print(table)
print(f"\nRetention bonuses: {data['with_retention_bonus']} staff")
print(f"Notes: {data['notes']}")
