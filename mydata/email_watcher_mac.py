"""Mac-specific email watcher using AppleScript for Mail.app and Outlook"""

import subprocess
import time
import hashlib
from typing import Callable, Optional, List, Dict
from datetime import datetime, timedelta


class MacEmailWatcher:
    """Watches email on Mac using AppleScript (Mail.app or Outlook)"""

    def __init__(
        self,
        email_type: str,  # "mail" or "outlook"
        on_email_received: Callable[[Dict], None],
        poll_interval: int = 60,
        days_back: int = 30,  # Only fetch emails from last N days
    ):
        self.email_type = email_type.lower()
        self.on_email_received = on_email_received
        self.poll_interval = poll_interval
        self.days_back = days_back
        self._running = False
        self._seen_ids = set()

    def start(self) -> None:
        """Start watching inbox"""
        if not self._check_app_available():
            return

        self._running = True
        app_name = "Mail.app" if self.email_type == "mail" else "Microsoft Outlook"
        print(f"👁 Watching {app_name} inbox...")

        # Do initial fetch
        self._check_new_emails()

        # Then poll for new emails
        while self._running:
            try:
                time.sleep(self.poll_interval)
                self._check_new_emails()
            except Exception as e:
                print(f"Error checking emails: {e}")
                time.sleep(10)

    def stop(self) -> None:
        """Stop watching"""
        self._running = False
        print(f"✓ Email watcher stopped")

    def _check_app_available(self) -> bool:
        """Check if the email app is available"""
        if self.email_type == "mail":
            script = '''
            tell application "System Events"
                return (name of processes) contains "Mail"
            end tell
            '''
            app_name = "Mail.app"
        else:  # outlook
            script = '''
            tell application "Microsoft Outlook"
                return name
            end tell
            '''
            app_name = "Microsoft Outlook"

        try:
            result = subprocess.run(
                ['osascript', '-e', script],
                capture_output=True,
                text=True,
                timeout=5
            )

            if result.returncode == 0:
                if self.email_type == "mail":
                    is_running = result.stdout.strip() == "true"
                    if not is_running:
                        print(f"Starting {app_name}...")
                        subprocess.run(['open', '-a', 'Mail'])
                        time.sleep(2)
                return True
            else:
                print(f"✗ Cannot access {app_name}: {result.stderr}")
                print(f"Please install {app_name} and configure your email account.")
                return False
        except Exception as e:
            print(f"✗ Error checking {app_name}: {e}")
            return False

    def _check_new_emails(self) -> None:
        """Check for new emails"""
        emails = self._fetch_recent_emails(limit=20)
        new_count = 0

        for email_data in emails:
            email_id = email_data["id"]

            if email_id in self._seen_ids:
                continue

            self._seen_ids.add(email_id)
            new_count += 1

            try:
                self.on_email_received(email_data)
            except Exception as e:
                print(f"Error processing email {email_id}: {e}")

        if new_count > 0:
            print(f"📧 Processed {new_count} new email(s)")

    def _fetch_recent_emails(self, limit: int = 20) -> List[Dict]:
        """Fetch recent emails from Mail.app or Outlook"""
        if self.email_type == "mail":
            return self._fetch_from_mail_app(limit)
        else:
            return self._fetch_from_outlook(limit)

    def _fetch_from_mail_app(self, limit: int) -> List[Dict]:
        """Fetch emails from Mac Mail.app"""
        script = f'''
        tell application "Mail"
            set allMessages to messages of inbox
            set msgCount to count of allMessages

            if msgCount = 0 then
                return ""
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

                    -- Truncate content
                    if length of msgContent > 2000 then
                        set msgContent to text 1 thru 2000 of msgContent & "..."
                    end if

                    set emailData to msgSubject & "|||" & msgSender & "|||" & (msgDate as string) & "|||" & (msgRead as string) & "|||" & msgContent
                    set end of emailList to emailData
                on error
                    -- Skip emails that error
                end try
            end repeat

            return emailList
        end tell
        '''

        try:
            result = subprocess.run(
                ['osascript', '-e', script],
                capture_output=True,
                text=True,
                timeout=30
            )

            if result.returncode != 0 or not result.stdout.strip():
                return []

            emails = []
            raw_emails = result.stdout.strip().split(", ")

            for raw in raw_emails:
                parts = raw.split("|||")
                if len(parts) >= 5:
                    # Create unique ID
                    email_id = hashlib.sha256(
                        f"{parts[1]}{parts[0]}{parts[2]}".encode()
                    ).hexdigest()[:16]

                    emails.append({
                        "id": email_id,
                        "subject": parts[0],
                        "sender": parts[1],
                        "date": parts[2],
                        "body": parts[4],
                        "full_text": f"From: {parts[1]}\nSubject: {parts[0]}\nDate: {parts[2]}\n\n{parts[4]}",
                    })

            return emails

        except Exception as e:
            print(f"Error fetching from Mail.app: {e}")
            return []

    def _fetch_from_outlook(self, limit: int) -> List[Dict]:
        """Fetch emails from Microsoft Outlook - optimized version"""
        # Optimized: Get recent messages from all folders
        script = f'''
        tell application "Microsoft Outlook"
            try
                -- Get all email accounts
                set allMessages to {{}}

                -- Iterate through all accounts
                repeat with acct in exchange accounts
                    try
                        -- Get inbox for this account
                        set inboxFolder to inbox of acct

                        -- Get recent messages from this inbox
                        set cutoffDate to (current date) - (7 * days)
                        set accountMessages to (every message of inboxFolder whose time received > cutoffDate)

                        -- Add to collection
                        set allMessages to allMessages & accountMessages
                    on error
                        -- Skip this account if error
                    end try
                end repeat

                -- Also check IMAP/POP accounts
                repeat with acct in imap accounts
                    try
                        set inboxFolder to inbox of acct
                        set cutoffDate to (current date) - (7 * days)
                        set accountMessages to (every message of inboxFolder whose time received > cutoffDate)
                        set allMessages to allMessages & accountMessages
                    on error
                        -- Skip this account if error
                    end try
                end repeat

                repeat with acct in pop accounts
                    try
                        set inboxFolder to inbox of acct
                        set cutoffDate to (current date) - (7 * days)
                        set accountMessages to (every message of inboxFolder whose time received > cutoffDate)
                        set allMessages to allMessages & accountMessages
                    on error
                        -- Skip this account if error
                    end try
                end repeat

                set emailList to {{}}
                set msgCount to count of allMessages

                if msgCount is 0 then
                    return ""
                end if

                -- Limit to prevent timeouts
                set fetchCount to {limit}
                if msgCount < fetchCount then
                    set fetchCount to msgCount
                end if

                repeat with i from 1 to fetchCount
                    set msg to item i of allMessages

                    try
                        set msgSubject to subject of msg as string
                        set msgSender to name of sender of msg as string
                        set msgSenderEmail to address of sender of msg as string
                        set msgDate to (time received of msg) as string
                        set msgRead to is read of msg as boolean

                        -- Get plain text content (smaller chunk)
                        set msgBody to plain text content of msg as string
                        if length of msgBody > 1000 then
                            set msgBody to text 1 thru 1000 of msgBody & "..."
                        end if

                        set emailData to msgSubject & "|||" & msgSender & "|||" & msgSenderEmail & "|||" & msgDate & "|||" & (msgRead as string) & "|||" & msgBody
                        set end of emailList to emailData
                    on error
                        -- Skip this message if error
                    end try
                end repeat

                return emailList
            on error errMsg
                return ""
            end try
        end tell
        '''

        try:
            result = subprocess.run(
                ['osascript', '-e', script],
                capture_output=True,
                text=True,
                timeout=90  # Increased timeout
            )

            if result.returncode != 0 or not result.stdout.strip():
                return []

            emails = []
            raw_emails = result.stdout.strip().split(", ")

            for raw in raw_emails:
                parts = raw.split("|||")
                if len(parts) >= 6:
                    # Create unique ID
                    email_id = hashlib.sha256(
                        f"{parts[2]}{parts[0]}{parts[3]}".encode()
                    ).hexdigest()[:16]

                    sender_full = f"{parts[1]} <{parts[2]}>"

                    emails.append({
                        "id": email_id,
                        "subject": parts[0],
                        "sender": sender_full,
                        "date": parts[3],
                        "body": parts[5],
                        "full_text": f"From: {sender_full}\nSubject: {parts[0]}\nDate: {parts[3]}\n\n{parts[5]}",
                    })

            return emails

        except Exception as e:
            print(f"Error fetching from Outlook: {e}")
            return []

    def is_running(self) -> bool:
        """Check if watcher is running"""
        return self._running
