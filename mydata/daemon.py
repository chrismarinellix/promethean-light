"""Unified daemon orchestrator - file watcher + email + ML"""

import threading
import time
import signal
import sys
from pathlib import Path
from typing import Optional, List, Dict
from .crypto import CryptoManager
from .database import Database
from .storage import EncryptedStorage
from .embedder import Embedder
from .vectordb import VectorDB
from .ml_organizer import MLOrganizer
from .ingestion import IngestionPipeline
from .file_watcher import FileWatcher
from .email_watcher import EmailWatcher
from .models import EmailCredential
from sqlmodel import select

# Try to import Outlook watcher (Windows only)
try:
    from .outlook_watcher import OutlookWatcher
    OUTLOOK_AVAILABLE = True
except ImportError:
    OUTLOOK_AVAILABLE = False


class Daemon:
    """Main daemon that orchestrates all background services"""

    def __init__(self, crypto: CryptoManager):
        self.crypto = crypto
        self.db = Database()
        self.storage = EncryptedStorage(crypto)
        self.embedder = Embedder()
        self.vectordb = VectorDB()
        self.vectordb.initialize(dimension=self.embedder.dimension)

        # Create pipeline
        session = self.db.session()
        self.ml_organizer = MLOrganizer(self.embedder, session)
        self.pipeline = IngestionPipeline(
            session, self.storage, self.embedder, self.vectordb, self.ml_organizer
        )

        self.file_watcher: Optional[FileWatcher] = None
        self.email_watchers: List[EmailWatcher] = []
        self._running = False
        self._threads: List[threading.Thread] = []

    def start(self) -> None:
        """Start all daemon services"""
        self._running = True

        # Setup signal handlers
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)

        # Start API server in background
        self._start_api_server()

        # Start file watcher
        self._start_file_watcher()

        # Start email watchers
        self._start_email_watchers()

        # Start ML organizer (periodic)
        ml_thread = threading.Thread(target=self._ml_loop, daemon=True)
        ml_thread.start()
        self._threads.append(ml_thread)

        print("\n" + "=" * 60)
        print("PROMETHEAN LIGHT - GOD MODE: ACTIVE")
        print("=" * 60)
        print("Services running:")
        print("  ✓ API Server (http://localhost:8000)")
        if self.file_watcher and self.file_watcher.is_running():
            print("  ✓ File Watcher")
        if self.email_watchers:
            print(f"  ✓ Email Watchers ({len(self.email_watchers)})")
        print("  ✓ ML Organizer")
        print("\nPress Ctrl+C to stop\n")
        print("You can now use 'mydata ask' and 'mydata search' in another terminal!")
        print()

        # Keep main thread alive
        try:
            while self._running:
                time.sleep(1)
        except KeyboardInterrupt:
            self.stop()

    def _start_api_server(self) -> None:
        """Start FastAPI server in background thread"""
        def run_server():
            import uvicorn
            from .api import app, init_services

            # Initialize API with our existing services
            init_services(self.crypto, self.db, self.storage, self.embedder, self.vectordb, self.pipeline)

            uvicorn.run(app, host="127.0.0.1", port=8000, log_level="error")

        api_thread = threading.Thread(target=run_server, daemon=True)
        api_thread.start()
        self._threads.append(api_thread)
        time.sleep(2)  # Give server time to start

    def stop(self) -> None:
        """Stop all services"""
        print("\n\nShutting down...")
        self._running = False

        if self.file_watcher:
            self.file_watcher.stop()

        for email_watcher in self.email_watchers:
            email_watcher.stop()

        print("✓ All services stopped")
        sys.exit(0)

    def _signal_handler(self, signum, frame):
        """Handle termination signals"""
        self.stop()

    def _start_file_watcher(self) -> None:
        """Start file watcher service"""
        # Get watch directories from config or use defaults
        watch_dirs = [
            Path.home() / "Documents",
            Path.home() / "Downloads",
        ]

        # Filter to existing directories
        existing_dirs = [d for d in watch_dirs if d.exists()]

        if not existing_dirs:
            print("⚠ No valid watch directories found")
            return

        def on_file_created(file_path: Path):
            """Callback for new files"""
            self.pipeline.ingest_file(file_path)

        self.file_watcher = FileWatcher(existing_dirs, on_file_created)

        # Start in separate thread
        watcher_thread = threading.Thread(target=self.file_watcher.start, daemon=True)
        watcher_thread.start()
        self._threads.append(watcher_thread)

    def _start_email_watchers(self) -> None:
        """Start email watcher services"""

        # Try Outlook watcher first (Windows only, no password needed!)
        if OUTLOOK_AVAILABLE:
            try:
                def on_email_received(email_data: Dict):
                    """Callback for new emails"""
                    self.pipeline.ingest_email(email_data)

                # Configure: 60 days (2 months) of history, watch both inbox and sent
                outlook_watcher = OutlookWatcher(
                    on_email_received,
                    history_hours=1440,  # Load last 60 days (2 months) on startup
                    watch_sent=True,     # Also watch sent emails
                )

                # Start in separate thread
                outlook_thread = threading.Thread(target=outlook_watcher.start, daemon=True)
                outlook_thread.start()
                self._threads.append(outlook_thread)
                self.email_watchers.append(outlook_watcher)

                print("✓ Using local Outlook (win32com)")
                return

            except Exception as e:
                print(f"⚠ Outlook watcher failed: {e}")
                print("  Falling back to IMAP...")

        # Fallback to IMAP if Outlook not available
        session = self.db.session()
        credentials = session.exec(select(EmailCredential).where(EmailCredential.enabled == True)).all()

        if not credentials:
            print("ℹ No email accounts configured")
            return

        for cred in credentials:
            # Decrypt password
            password = self.crypto.decrypt_str(cred.encrypted_password)

            def on_email_received(email_data: Dict):
                """Callback for new emails"""
                self.pipeline.ingest_email(email_data)

            email_watcher = EmailWatcher(
                email_address=cred.email_address,
                password=password,
                on_email_received=on_email_received,
                imap_server=cred.imap_server,
                imap_port=cred.imap_port,
            )

            # Start in separate thread
            email_thread = threading.Thread(target=email_watcher.start, daemon=True)
            email_thread.start()
            self._threads.append(email_thread)
            self.email_watchers.append(email_watcher)

    def _ml_loop(self) -> None:
        """Periodic ML organization"""
        from datetime import datetime

        iteration = 0

        while self._running:
            time.sleep(300)  # Run every 5 minutes
            iteration += 1

            try:
                current_time = datetime.now().strftime("%H:%M:%S")
                print(f"\n[HEARTBEAT] [{current_time}] System active - Iteration #{iteration}")
                print(f"[HEARTBEAT] Services: API ✓ | File Watcher ✓ | Email ✓ | ML ✓")
                print()

                print(f"[ML] Running periodic organization (cycle #{iteration})...")
                result = self.ml_organizer.run_clustering()

                if result.get("status") == "ok":
                    print(f"[ML] ✓ Organization cycle #{iteration} complete")
                else:
                    print(f"[ML] ⚠ Cycle #{iteration} skipped: {result.get('reason', 'unknown')}")

                print(f"[ML] Next organization in 5 minutes ({datetime.now().strftime('%H:%M:%S')})")
                print()

            except Exception as e:
                print(f"[ML] Error in cycle #{iteration}: {e}")
                import traceback
                print(f"[ML] Traceback: {traceback.format_exc()}")
