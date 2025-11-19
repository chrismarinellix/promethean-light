#!/usr/bin/env python3
"""Test AppleScript to fetch emails from Mac Mail.app"""

import subprocess
import json
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import box

console = Console()


def check_mail_running():
    """Check if Mail.app is running"""
    script = '''
    tell application "System Events"
        return (name of processes) contains "Mail"
    end tell
    '''

    result = subprocess.run(
        ['osascript', '-e', script],
        capture_output=True,
        text=True
    )

    return result.stdout.strip() == "true"


def get_mail_accounts():
    """Get list of email accounts in Mail.app"""
    script = '''
    tell application "Mail"
        set accountList to {}
        repeat with acct in accounts
            set end of accountList to name of acct
        end repeat
        return accountList
    end tell
    '''

    try:
        result = subprocess.run(
            ['osascript', '-e', script],
            capture_output=True,
            text=True,
            timeout=10
        )

        if result.returncode == 0:
            # Parse comma-separated list
            accounts = result.stdout.strip().split(", ")
            return [a for a in accounts if a]
        else:
            console.print(f"[red]Error: {result.stderr}[/red]")
            return []
    except Exception as e:
        console.print(f"[red]Error getting accounts: {e}[/red]")
        return []


def fetch_recent_emails(limit=10):
    """Fetch recent emails from Mail.app inbox"""
    script = f'''
    tell application "Mail"
        -- Get all messages from inbox (no date filter)
        set allMessages to messages of inbox
        set msgCount to count of allMessages

        -- Return count first for debugging
        if msgCount = 0 then
            return "NO_EMAILS"
        end if

        set emailList to {{}}
        set fetchCount to {limit}
        if msgCount < fetchCount then
            set fetchCount to msgCount
        end if

        repeat with i from 1 to fetchCount
            set msg to item i of allMessages

            try
                set msgSubject to subject of msg
                set msgSender to sender of msg
                set msgDate to date received of msg
                set msgRead to read status of msg
                set msgContent to content of msg

                -- Truncate content to first 500 chars
                if length of msgContent > 500 then
                    set msgContent to text 1 thru 500 of msgContent & "..."
                end if

                set emailData to msgSubject & "|||" & msgSender & "|||" & (msgDate as string) & "|||" & (msgRead as string) & "|||" & msgContent
                set end of emailList to emailData
            on error errMsg
                -- Skip emails that error
            end try
        end repeat

        return emailList
    end tell
    '''

    try:
        console.print("[cyan]Fetching emails from Mail.app...[/cyan]")

        result = subprocess.run(
            ['osascript', '-e', script],
            capture_output=True,
            text=True,
            timeout=30
        )

        if result.returncode != 0:
            console.print(f"[red]AppleScript Error: {result.stderr}[/red]")
            return []

        # Parse the output
        output = result.stdout.strip()

        if output == "NO_EMAILS":
            console.print("[yellow]Inbox is empty[/yellow]")
            return []

        if not output or output == "":
            return []

        emails = []
        # Split by comma (AppleScript list separator)
        raw_emails = output.split(", ")

        for raw in raw_emails:
            parts = raw.split("|||")
            if len(parts) >= 5:
                emails.append({
                    "subject": parts[0],
                    "sender": parts[1],
                    "date": parts[2],
                    "read": parts[3] == "true",
                    "content": parts[4]
                })

        return emails

    except subprocess.TimeoutExpired:
        console.print("[red]Timeout waiting for Mail.app response[/red]")
        return []
    except Exception as e:
        console.print(f"[red]Error fetching emails: {e}[/red]")
        return []


def display_emails(emails):
    """Display emails in a table"""
    if not emails:
        console.print("[yellow]No emails found[/yellow]")
        return

    table = Table(
        title=f"[bold cyan]📧 Recent Emails from Mail.app ({len(emails)} shown)[/bold cyan]",
        show_header=True,
        header_style="bold magenta",
        border_style="cyan",
        box=box.ROUNDED
    )

    table.add_column("#", style="dim", width=4)
    table.add_column("From", style="green", width=30, no_wrap=True)
    table.add_column("Subject", style="white", width=40, no_wrap=True)
    table.add_column("Date", style="cyan", width=20)
    table.add_column("Read", style="yellow", width=6)

    for idx, email_data in enumerate(emails, 1):
        read_status = "✓" if email_data["read"] else "✗"

        table.add_row(
            str(idx),
            email_data["sender"][:30],
            email_data["subject"][:40],
            email_data["date"][:20],
            read_status
        )

    console.print(table)

    # Show sample content
    if emails:
        console.print("\n[bold]Sample Email Content (first email):[/bold]")
        console.print(Panel(
            emails[0]["content"][:200] + "...",
            border_style="dim",
            title="[dim]Preview[/dim]"
        ))


def main():
    """Main test function"""
    console.print(Panel(
        "[bold cyan]Mac Mail.app AppleScript Test[/bold cyan]\n"
        "[dim]Testing email fetching via AppleScript[/dim]",
        border_style="cyan",
        box=box.DOUBLE
    ))

    # Check if Mail is running
    console.print("\n[cyan]Checking if Mail.app is running...[/cyan]")
    if not check_mail_running():
        console.print("[yellow]Mail.app is not running. Starting it...[/yellow]")
        subprocess.run(['open', '-a', 'Mail'])
        import time
        time.sleep(2)
    else:
        console.print("[green]✓ Mail.app is running[/green]")

    # Get accounts
    console.print("\n[cyan]Getting email accounts...[/cyan]")
    accounts = get_mail_accounts()

    if accounts:
        console.print(f"[green]✓ Found {len(accounts)} account(s):[/green]")
        for account in accounts:
            console.print(f"  • {account}")
    else:
        console.print("[red]✗ No email accounts found in Mail.app[/red]")
        console.print("\n[yellow]Please add an email account to Mail.app first:[/yellow]")
        console.print("  1. Open Mail.app")
        console.print("  2. Go to Mail → Settings → Accounts")
        console.print("  3. Add your email account")
        return

    # Fetch emails
    console.print("\n[cyan]Fetching recent emails (last 7 days)...[/cyan]")
    emails = fetch_recent_emails(limit=10)

    # Display results
    console.print()
    display_emails(emails)

    if emails:
        console.print(f"\n[bold green]✓ Successfully fetched {len(emails)} emails![/bold green]")
        console.print("[dim]This data is ready to import into Promethean Light[/dim]")
    else:
        console.print("\n[yellow]No recent emails found (or error occurred)[/yellow]")


if __name__ == "__main__":
    main()
