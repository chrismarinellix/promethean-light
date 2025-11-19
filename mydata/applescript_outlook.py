#!/usr/bin/env python3
"""Simple Outlook AppleScript test for Mac"""

import subprocess
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich import box

console = Console()


def test_outlook_access():
    """Test if we can access Outlook"""
    script = '''
    tell application "Microsoft Outlook"
        return name
    end tell
    '''

    try:
        result = subprocess.run(
            ['osascript', '-e', script],
            capture_output=True,
            text=True,
            timeout=5
        )

        if result.returncode == 0:
            console.print(f"[green]✓ Outlook is accessible: {result.stdout.strip()}[/green]")
            return True
        else:
            console.print(f"[red]✗ Cannot access Outlook: {result.stderr}[/red]")
            return False
    except Exception as e:
        console.print(f"[red]✗ Error: {e}[/red]")
        return False


def get_inbox_count():
    """Get count of messages in inbox"""
    # Use a simpler approach - get recent messages only
    script = '''
    tell application "Microsoft Outlook"
        try
            -- Get the default inbox
            set inboxFolder to inbox

            -- Get messages from the last 30 days only (faster)
            set cutoffDate to (current date) - (30 * days)
            set recentMessages to (every message of inboxFolder whose time received > cutoffDate)

            return count of recentMessages
        on error errMsg
            return "ERROR: " & errMsg
        end try
    end tell
    '''

    try:
        console.print("[cyan]Counting recent messages (last 30 days)...[/cyan]")
        result = subprocess.run(
            ['osascript', '-e', script],
            capture_output=True,
            text=True,
            timeout=30
        )

        if result.returncode == 0:
            output = result.stdout.strip()
            if output.startswith("ERROR"):
                console.print(f"[red]{output}[/red]")
                return 0
            try:
                count = int(output)
                console.print(f"[green]✓ Found {count} messages in last 30 days[/green]")
                return count
            except:
                console.print(f"[yellow]Unexpected output: {output}[/yellow]")
                return 0
        else:
            console.print(f"[red]Error: {result.stderr}[/red]")
            return 0
    except subprocess.TimeoutExpired:
        console.print("[red]Timeout - inbox might be very large[/red]")
        return 0
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        return 0


def fetch_sample_emails(limit=5):
    """Fetch a small sample of recent emails"""
    script = f'''
    tell application "Microsoft Outlook"
        try
            set inboxFolder to inbox

            -- Get only the most recent messages
            set cutoffDate to (current date) - (7 * days)
            set recentMessages to (every message of inboxFolder whose time received > cutoffDate)

            set emailList to {{}}
            set fetchCount to {limit}

            if (count of recentMessages) < fetchCount then
                set fetchCount to count of recentMessages
            end if

            repeat with i from 1 to fetchCount
                set msg to item i of recentMessages

                try
                    set msgSubject to subject of msg as string
                    set msgSender to name of sender of msg as string
                    set msgSenderEmail to address of sender of msg as string
                    set msgDate to (time received of msg) as string
                    set msgRead to is read of msg as boolean

                    -- Get plain text content (first 200 chars)
                    set msgBody to plain text content of msg as string
                    if length of msgBody > 200 then
                        set msgBody to text 1 thru 200 of msgBody & "..."
                    end if

                    set emailData to msgSubject & "|||" & msgSender & "|||" & msgSenderEmail & "|||" & msgDate & "|||" & (msgRead as string) & "|||" & msgBody
                    set end of emailList to emailData
                on error
                    -- Skip this message if error
                end try
            end repeat

            return emailList
        on error errMsg
            return "ERROR: " & errMsg
        end try
    end tell
    '''

    try:
        console.print(f"[cyan]Fetching {limit} sample emails...[/cyan]")
        result = subprocess.run(
            ['osascript', '-e', script],
            capture_output=True,
            text=True,
            timeout=60
        )

        if result.returncode != 0:
            console.print(f"[red]AppleScript Error: {result.stderr}[/red]")
            return []

        output = result.stdout.strip()

        if output.startswith("ERROR"):
            console.print(f"[red]{output}[/red]")
            return []

        if not output:
            console.print("[yellow]No emails found[/yellow]")
            return []

        # Parse the comma-separated list
        emails = []
        raw_emails = output.split(", ")

        for raw in raw_emails:
            parts = raw.split("|||")
            if len(parts) >= 6:
                emails.append({
                    "subject": parts[0],
                    "sender_name": parts[1],
                    "sender_email": parts[2],
                    "date": parts[3],
                    "is_read": parts[4] == "true",
                    "body": parts[5]
                })

        return emails

    except subprocess.TimeoutExpired:
        console.print("[red]Timeout fetching emails[/red]")
        return []
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        return []


def display_emails(emails):
    """Display emails in a table"""
    if not emails:
        return

    table = Table(
        title=f"[bold cyan]📧 Sample Outlook Emails ({len(emails)})[/bold cyan]",
        show_header=True,
        header_style="bold magenta",
        border_style="cyan",
        box=box.ROUNDED
    )

    table.add_column("#", style="dim", width=3)
    table.add_column("From", style="green", width=25)
    table.add_column("Subject", style="white", width=35)
    table.add_column("Date", style="cyan", width=20)
    table.add_column("Read", style="yellow", width=5)

    for idx, email in enumerate(emails, 1):
        read_icon = "✓" if email["is_read"] else "✗"
        table.add_row(
            str(idx),
            email["sender_name"][:25],
            email["subject"][:35],
            email["date"][:20],
            read_icon
        )

    console.print(table)

    # Show first email preview
    if emails:
        console.print(f"\n[bold]Sample Email Body (first email):[/bold]")
        console.print(Panel(
            emails[0]["body"],
            border_style="dim",
            title=f"[dim]{emails[0]['subject'][:50]}[/dim]"
        ))


def main():
    console.print(Panel(
        "[bold cyan]Outlook AppleScript Email Fetcher[/bold cyan]\n"
        "[dim]Testing Outlook email access via AppleScript[/dim]",
        border_style="cyan",
        box=box.DOUBLE
    ))

    # Test Outlook access
    console.print("\n[bold]Step 1: Testing Outlook Access[/bold]")
    if not test_outlook_access():
        console.print("\n[red]Cannot access Outlook. Make sure:[/red]")
        console.print("  1. Microsoft Outlook is installed")
        console.print("  2. You have an email account configured in Outlook")
        console.print("  3. Outlook has accessibility permissions")
        return

    # Count messages
    console.print("\n[bold]Step 2: Counting Messages[/bold]")
    count = get_inbox_count()

    if count == 0:
        console.print("\n[yellow]No messages found or Outlook inbox is empty[/yellow]")
        console.print("[dim]Make sure you have email accounts set up in Outlook[/dim]")
        return

    # Fetch sample
    console.print("\n[bold]Step 3: Fetching Sample Emails[/bold]")
    emails = fetch_sample_emails(limit=5)

    # Display
    if emails:
        console.print()
        display_emails(emails)
        console.print(f"\n[bold green]✓ Successfully fetched {len(emails)} sample emails![/bold green]")
        console.print("[dim]This confirms AppleScript can read your Outlook emails[/dim]")
        console.print("[dim]Ready to integrate into Promethean Light![/dim]")
    else:
        console.print("\n[yellow]Could not fetch emails[/yellow]")


if __name__ == "__main__":
    main()
