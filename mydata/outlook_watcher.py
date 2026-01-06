"""Outlook watcher using win32com - direct local Outlook access"""

import time
import threading
import json
from pathlib import Path
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
        state_file: Optional[Path] = None,  # Where to persist state
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
        self._last_processed_time = None

        # State file for persistence
        if state_file is None:
            state_file = Path.home() / ".mydata" / "outlook_state.json"
        self.state_file = state_file
        self.state_file.parent.mkdir(parents=True, exist_ok=True)

        # Load previous state
        self._load_state()

    def connect(self) -> bool:
        """Connect to local Outlook"""
        try:
            import win32com.client

            self._outlook = win32com.client.Dispatch("Outlook.Application")
            mapi = self._outlook.GetNamespace("MAPI")
            self._inbox = mapi.GetDefaultFolder(6)  # 6 = Inbox

            if self.watch_sent:
                self._sent_items = mapi.GetDefaultFolder(5)  # 5 = Sent Items
                print(f"[OK] Connected to Outlook inbox + sent items")
            else:
                print(f"[OK] Connected to Outlook inbox")

            print(f"  Loading last {self.history_hours} hours of emails...")
            return True
        except Exception as e:
            print(f"[ERROR] Failed to connect to Outlook: {e}")
            return False

    def start(self) -> None:
        """Start watching inbox"""
        # Initialize COM for this thread (required for win32com in threads)
        try:
            import pythoncom
            pythoncom.CoInitialize()
        except Exception as e:
            print(f"[WARN] COM initialization: {e}")

        if not self.connect():
            return

        self._running = True
        print(f"[WATCH] Watching Outlook inbox")

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
        print(f"[OK] Outlook watcher stopped")

    def _check_new_emails(self) -> None:
        """Check for new emails in inbox and sent items"""
        from datetime import datetime

        check_time = datetime.now().strftime("%H:%M:%S")
        new_count = 0
        inbox_count = 0
        sent_count = 0

        # Debug: show what we're looking for
        if self._last_processed_time:
            print(f"[EMAIL-DEBUG] [{check_time}] Checking for emails after: {self._last_processed_time.strftime('%Y-%m-%d %H:%M:%S')}")
        else:
            print(f"[EMAIL-DEBUG] [{check_time}] First run - looking back {self.history_hours} hours")

        # Process inbox
        if self._inbox:
            inbox_count = self._process_folder(self._inbox, "inbox")
            new_count += inbox_count

        # Process sent items
        if self.watch_sent and self._sent_items:
            sent_count = self._process_folder(self._sent_items, "sent")
            new_count += sent_count

        if new_count > 0:
            print(f"[EMAIL] [{check_time}] Processed {new_count} new email(s) from Outlook")
            if inbox_count > 0:
                print(f"   - Inbox: {inbox_count} new")
            if sent_count > 0:
                print(f"   - Sent: {sent_count} new")
            if self._last_processed_time:
                print(f"   - Last sync: {self._last_processed_time.strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"   - Total tracked: {len(self._seen_ids)} emails")
            # Save state after processing new emails
            self._save_state()
        else:
            print(f"[EMAIL-DEBUG] [{check_time}] No new emails found (seen: {len(self._seen_ids)}, cutoff: {self._last_processed_time})")

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
                    # Some items (calendar invites, etc.) may not have ReceivedTime
                    try:
                        received_time = msg.ReceivedTime
                    except Exception:
                        # Mark as seen to avoid repeated errors
                        self._seen_ids.add(entry_id)
                        continue
                    if isinstance(received_time, str):
                        # Parse if string
                        continue

                    # Only process recent emails
                    # Make datetime timezone-naive for comparison
                    now = datetime.now()
                    if hasattr(received_time, 'replace'):
                        received_time_naive = received_time.replace(tzinfo=None)

                        # If we have a last processed time, only process emails after it
                        if self._last_processed_time is not None:
                            if received_time_naive <= self._last_processed_time:
                                continue  # Skip already processed emails
                        else:
                            # First run - use history_hours
                            time_diff = now - received_time_naive
                            if time_diff > timedelta(hours=self.history_hours):
                                continue

                    self._seen_ids.add(entry_id)

                    # Extract email data
                    email_data = self._extract_email_data(msg)

                    if email_data:
                        new_count += 1
                        self.on_email_received(email_data)

                        # Update last processed time
                        if hasattr(received_time, 'replace'):
                            received_time_naive = received_time.replace(tzinfo=None)
                            if self._last_processed_time is None or received_time_naive > self._last_processed_time:
                                self._last_processed_time = received_time_naive

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

    def sync_now(self) -> dict:
        """Trigger an immediate email sync (called from API)"""
        if not self._running:
            return {"status": "error", "message": "Watcher not running"}

        try:
            print("[EMAIL] Manual sync triggered...")
            self._check_new_emails()
            return {
                "status": "ok",
                "message": "Sync completed",
                "emails_tracked": len(self._seen_ids),
                "last_sync": self._last_processed_time.isoformat() if self._last_processed_time else None
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def _load_state(self) -> None:
        """Load previous state from disk"""
        if not self.state_file.exists():
            print("  No previous state found - will load initial history")
            return

        try:
            with open(self.state_file, 'r') as f:
                state = json.load(f)

            # Load last processed timestamp
            if 'last_processed_time' in state:
                self._last_processed_time = datetime.fromisoformat(state['last_processed_time'])
                print(f"  Resuming from: {self._last_processed_time.strftime('%Y-%m-%d %H:%M:%S')}")

        except Exception as e:
            print(f"  Warning: Could not load state: {e}")

    def _save_state(self) -> None:
        """Save current state to disk"""
        try:
            state = {
                'last_processed_time': self._last_processed_time.isoformat() if self._last_processed_time else None,
            }

            with open(self.state_file, 'w') as f:
                json.dump(state, f, indent=2)

        except Exception as e:
            print(f"  Warning: Could not save state: {e}")
