"""Quick Reports Menu - Access all your important reports in one place"""
import sys

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

print("\n" + "="*80)
print(" PROMETHEAN LIGHT - QUICK REPORTS MENU ".center(80, "="))
print("="*80)
print("\nAvailable Reports:")
print("-"*80)
print("  1. Salary Review Status (All Staff + Pay Rises)")
print("  2. Australia Staff Summary")
print("  3. India Staff Summary")
print("  4. Retention Bonus Summary")
print("  5. Staff Details (Full List)")
print("  6. Email Summary (Recent)")
print("  7. Project Pipeline")
print("  8. Weekly Checklists Status")
print("\n  0. Exit")
print("-"*80)

choice = input("\nSelect report (0-8): ").strip()

if choice == "1":
    import subprocess
    subprocess.run(["python", "salary_review_compact.py"])
elif choice == "2":
    import subprocess
    subprocess.run(["python", "show_staff.py"])
elif choice == "3":
    from mydata.summaries import get_india_staff_summary
    from rich.console import Console
    from rich.table import Table

    console = Console()
    data = get_india_staff_summary()

    table = Table(title="India Staff (7 Total)", show_header=True, header_style="bold cyan")
    table.add_column("ID", style="dim", width=8)
    table.add_column("Name", style="white", width=25)
    table.add_column("Level", style="magenta", width=20)
    table.add_column("CTC (INR)", style="green", justify="right", width=15)
    table.add_column("CTC (AUD)", style="yellow", justify="right", width=12)
    table.add_column("Bonus", style="red", width=12)

    for s in data['staff']:
        bonus = s.get('retention_bonus', 'None')
        table.add_row(
            s['id'],
            s['name'],
            s['level'],
            s['ctc_inr'],
            s['ctc_aud'],
            bonus
        )

    console.print(table)
    print(f"\nWith retention bonuses: {data['with_retention_bonus']} staff")

elif choice == "4":
    from mydata.summaries import get_retention_bonus_summary
    from rich.console import Console
    from rich.table import Table

    console = Console()
    data = get_retention_bonus_summary()

    print("\n" + "="*60)
    print(f" RETENTION BONUS SUMMARY ".center(60, "="))
    print("="*60)
    print(f"\nTotal Staff with Bonuses: {data['total_staff_with_bonuses']}")
    print(f"Total Annual Cost: {data['total_annual_cost_aud']}")

    table1 = Table(title="Expires Feb 2026", show_header=True, header_style="bold red")
    table1.add_column("Name", style="white", width=30)
    table1.add_column("Bonus", style="yellow", width=10)
    table1.add_column("Amount", style="green", width=15)

    for s in data['expires_feb_2026']:
        table1.add_row(s['name'], s['bonus'], s['amount_aud'])

    console.print(table1)

    table2 = Table(title="Expires Aug 2026", show_header=True, header_style="bold yellow")
    table2.add_column("Name", style="white", width=30)
    table2.add_column("Bonus", style="yellow", width=10)
    table2.add_column("Amount", style="green", width=15)

    for s in data['expires_aug_2026']:
        amount = s.get('amount_aud') or s.get('amount_myr') or s.get('amount_inr', 'N/A')
        table2.add_row(s['name'], s['bonus'], amount)

    console.print(table2)

elif choice == "5":
    import subprocess
    subprocess.run(["python", "show_staff.py"])

elif choice == "6":
    print("\nFetching recent emails...")
    import subprocess
    subprocess.run(["python", "recent_email_summary.py"])

elif choice == "7":
    print("\nFetching pipeline summary...")
    import subprocess
    subprocess.run(["python", "get_pipeline_summary.py"])

elif choice == "8":
    print("\nChecking weekly checklists...")
    import sqlite3
    conn = sqlite3.connect('mydata/mydata.db')
    cursor = conn.cursor()

    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='weekly_checklists'")
    if cursor.fetchone():
        cursor.execute("SELECT COUNT(*) FROM weekly_checklists")
        count = cursor.fetchone()[0]
        print(f"\nTotal checklists: {count}")

        cursor.execute("SELECT * FROM weekly_checklists ORDER BY created_at DESC LIMIT 5")
        rows = cursor.fetchall()
        if rows:
            print("\nRecent checklists:")
            for row in rows:
                print(f"  - {row}")
    else:
        print("\nNo checklists table found")

    conn.close()

elif choice == "0":
    print("\nExiting...\n")
else:
    print("\nInvalid choice!\n")

print()
