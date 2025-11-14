"""Outlook watcher using win32com - direct local Outlook access"""

import time
import threading
from typing import Callable, Dict, Optional
from datetime import datetime, timedelta


class OutlookWatcher:
    """Watches Outlook inbox using win32com (no IMAP needed!)"""

    def __init__(
        self,
        on_email_received: Callable[[Dict], None],
        poll_interval: int = 60,
        history_hours: int = 24,  # How far back to load on first run
        watch_sent: bool = True,  # Also watch sent items
    ):
        self.on_email_received = on_email_received
        self.poll_interval = poll_interval
        self.history_hours = history_hours
        self.watch_sent = watch_sent
        self._running = False
        self._outlook = None
        self._inbox = None
        self._sent_items = None
        self._seen_ids = set()

    def connect(self) -> bool:
        """Connect to local Outlook"""
        try:
            import win32com.client

            self._outlook = win32com.client.Dispatch("Outlook.Application")
            mapi = self._outlook.GetNamespace("MAPI")
            self._inbox = mapi.GetDefaultFolder(6)  # 6 = Inbox

            if self.watch_sent:
                self._sent_items = mapi.GetDefaultFolder(5)  # 5 = Sent Items
                print(f"✓ Connected to Outlook inbox + sent items")
            else:
                print(f"✓ Connected to Outlook inbox")

            print(f"  Loading last {self.history_hours} hours of emails...")
            return True
        except Exception as e:
            print(f"✗ Failed to connect to Outlook: {e}")
            return False

    def start(self) -> None:
        """Start watching inbox"""
        if not self.connect():
            return

        self._running = True
        print(f"👁 Watching Outlook inbox")

        while self._running:
            try:
                self._check_new_emails()
                time.sleep(self.poll_interval)
            except Exception as e:
                print(f"Error checking Outlook: {e}")
                time.sleep(10)

    def stop(self) -> None:
        """Stop watching"""
        self._running = False
        print(f"✓ Outlook watcher stopped")

    def _check_new_emails(self) -> None:
        """Check for new emails in inbox and sent items"""
        new_count = 0

        # Process inbox
        if self._inbox:
            new_count += self._process_folder(self._inbox, "inbox")

        # Process sent items
        if self.watch_sent and self._sent_items:
            new_count += self._process_folder(self._sent_items, "sent")

        if new_count > 0:
            print(f"📧 Processed {new_count} new email(s) from Outlook")

    def _process_folder(self, folder, folder_name: str) -> int:
        """Process emails from a specific folder"""
        try:
            messages = folder.Items
            messages.Sort("[ReceivedTime]", True)  # Descending

            # Check more messages based on history hours
            # For 2 months, check up to 500 messages
            if self.history_hours >= 720:  # 30+ days
                max_check = min(500, messages.Count)
            elif self.history_hours >= 168:  # 7+ days
                max_check = min(200, messages.Count)
            else:
                max_check = min(100, messages.Count)
            new_count = 0

            for i in range(1, max_check + 1):
                try:
                    msg = messages.Item(i)

                    # Skip if already seen
                    entry_id = msg.EntryID
                    if entry_id in self._seen_ids:
                        continue

                    # Check if recent (last hour)
                    received_time = msg.ReceivedTime
                    if isinstance(received_time, str):
                        # Parse if string
                        continue

                    # Only process recent emails (configurable history)
                    # Make datetime timezone-naive for comparison
                    now = datetime.now()
                    if hasattr(received_time, 'replace'):
                        received_time_naive = received_time.replace(tzinfo=None)
                        time_diff = now - received_time_naive
                        if time_diff > timedelta(hours=self.history_hours):
                            continue

                    self._seen_ids.add(entry_id)

                    # Extract email data
                    email_data = self._extract_email_data(msg)

                    if email_data:
                        new_count += 1
                        self.on_email_received(email_data)

                except Exception as e:
                    print(f"Error processing {folder_name} email {i}: {e}")
                    continue

            return new_count

        except Exception as e:
            print(f"Error accessing Outlook {folder_name}: {e}")
            return 0

    def _extract_email_data(self, msg) -> Optional[Dict]:
        """Extract data from Outlook message"""
        try:
            subject = msg.Subject or "(no subject)"
            sender = msg.SenderEmailAddress or msg.SenderName or "(unknown)"
            received = msg.ReceivedTime
            body = msg.Body or ""

            # Create unique ID
            email_id = msg.EntryID[:16] if msg.EntryID else str(hash(subject + sender))

            return {
                "id": email_id,
                "uid": msg.EntryID,
                "subject": subject,
                "sender": sender,
                "date": str(received),
                "body": body,
                "attachments": [],
                "full_text": f"From: {sender}\nSubject: {subject}\nDate: {received}\n\n{body}",
            }

        except Exception as e:
            print(f"Error extracting email data: {e}")
            return None

    def is_running(self) -> bool:
        """Check if watcher is running"""
        return self._running
