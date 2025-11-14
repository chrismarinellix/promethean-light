"""Email watcher for IMAP email ingestion"""

import imaplib
import email
import time
import hashlib
from email.policy import default
from typing import Callable, Optional, List, Dict
from pathlib import Path


class EmailWatcher:
    """Watches an email inbox via IMAP and triggers ingestion"""

    def __init__(
        self,
        email_address: str,
        password: str,
        on_email_received: Callable[[Dict], None],
        imap_server: str = "imap.gmail.com",
        imap_port: int = 993,
        poll_interval: int = 60,
    ):
        self.email_address = email_address
        self.password = password
        self.imap_server = imap_server
        self.imap_port = imap_port
        self.poll_interval = poll_interval
        self.on_email_received = on_email_received
        self._running = False
        self._seen_uids = set()
        self._mail = None

    def connect(self) -> bool:
        """Connect to IMAP server"""
        try:
            self._mail = imaplib.IMAP4_SSL(self.imap_server, self.imap_port)
            self._mail.login(self.email_address, self.password)
            self._mail.select("inbox")
            print(f"✓ Connected to {self.email_address}")
            return True
        except Exception as e:
            print(f"✗ Failed to connect to {self.email_address}: {e}")
            return False

    def disconnect(self) -> None:
        """Disconnect from IMAP server"""
        if self._mail:
            try:
                self._mail.logout()
            except Exception:
                pass
            self._mail = None

    def start(self) -> None:
        """Start watching inbox"""
        if not self.connect():
            return

        self._running = True
        print(f"👁 Watching inbox: {self.email_address}")

        while self._running:
            try:
                self._check_new_emails()
                time.sleep(self.poll_interval)
            except Exception as e:
                print(f"Error checking emails: {e}")
                # Try to reconnect
                self.disconnect()
                time.sleep(10)
                if not self.connect():
                    break

    def stop(self) -> None:
        """Stop watching"""
        self._running = False
        self.disconnect()
        print(f"✓ Email watcher stopped: {self.email_address}")

    def _check_new_emails(self) -> None:
        """Check for new emails"""
        if not self._mail:
            return

        # Search for unseen emails
        status, data = self._mail.uid("search", None, "UNSEEN")
        if status != "OK":
            return

        uids = data[0].split()
        new_count = 0

        for uid in uids:
            uid_str = uid.decode()
            if uid_str in self._seen_uids:
                continue

            self._seen_uids.add(uid_str)
            email_data = self._fetch_email(uid)

            if email_data:
                new_count += 1
                try:
                    self.on_email_received(email_data)
                except Exception as e:
                    print(f"Error processing email {uid_str}: {e}")

        if new_count > 0:
            print(f"📧 Processed {new_count} new email(s)")

    def _fetch_email(self, uid: bytes) -> Optional[Dict]:
        """Fetch and parse email"""
        try:
            status, data = self._mail.uid("fetch", uid, "(RFC822)")
            if status != "OK":
                return None

            raw_email = data[0][1]
            msg = email.message_from_bytes(raw_email, policy=default)

            # Extract basic info
            subject = msg["subject"] or "(no subject)"
            sender = msg["from"] or "(unknown)"
            date = msg["date"] or ""

            # Extract body
            body = self._get_body(msg)

            # Extract attachments info
            attachments = []
            for part in msg.walk():
                if part.get_content_disposition() == "attachment":
                    filename = part.get_filename()
                    if filename:
                        attachments.append(filename)

            # Create unique ID
            email_id = hashlib.sha256(
                f"{sender}{subject}{date}".encode()
            ).hexdigest()[:16]

            return {
                "id": email_id,
                "uid": uid.decode(),
                "subject": subject,
                "sender": sender,
                "date": date,
                "body": body,
                "attachments": attachments,
                "full_text": f"From: {sender}\nSubject: {subject}\nDate: {date}\n\n{body}",
            }

        except Exception as e:
            print(f"Error fetching email: {e}")
            return None

    def _get_body(self, msg: email.message.Message) -> str:
        """Extract email body text"""
        body = ""

        if msg.is_multipart():
            for part in msg.walk():
                content_type = part.get_content_type()
                if content_type == "text/plain":
                    try:
                        body = part.get_payload(decode=True).decode()
                        break
                    except Exception:
                        pass
        else:
            try:
                body = msg.get_payload(decode=True).decode()
            except Exception:
                body = str(msg.get_payload())

        return body.strip()

    def is_running(self) -> bool:
        """Check if watcher is running"""
        return self._running
