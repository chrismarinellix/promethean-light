"""Unified daemon orchestrator - file watcher + email + ML"""

import threading
import time
import signal
import sys
import platform
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
from .logger import get_logger

logger = get_logger()

# Detect platform
IS_MAC = platform.system() == "Darwin"
IS_WINDOWS = platform.system() == "Windows"

# Try to import Mac email watcher (macOS only)
if IS_MAC:
    try:
        from .email_watcher_mac import MacEmailWatcher
        MAC_EMAIL_AVAILABLE = True
    except ImportError:
        MAC_EMAIL_AVAILABLE = False
else:
    MAC_EMAIL_AVAILABLE = False

# Try to import Outlook watcher (Windows only)
if IS_WINDOWS:
    try:
        from .outlook_watcher import OutlookWatcher
        OUTLOOK_AVAILABLE = True
    except ImportError:
        OUTLOOK_AVAILABLE = False
else:
    OUTLOOK_AVAILABLE = False


from .settings import settings


class Daemon:
    """Main daemon that orchestrates all background services"""

    def __init__(self, crypto: CryptoManager, settings: settings):
        self.crypto = crypto
        self.db = Database()
        self.storage = EncryptedStorage(crypto)
        self.embedder = Embedder()
        self.vectordb = VectorDB()
        self.vectordb.initialize(dimension=self.embedder.dimension)
        self.settings = settings

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
        self._api_startup_event = threading.Event() # For API server readiness

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

        logger.info("PROMETHEAN LIGHT - GOD MODE: ACTIVE")
        logger.info("Services running:")
        logger.info(f"  API Server (http://{self.settings.api_host}:{self.settings.api_port})")
        if self.file_watcher and self.file_watcher.is_running():
            logger.info("  File Watcher")
        if self.email_watchers:
            logger.info(f"  Email Watchers ({len(self.email_watchers)})")
        logger.info("  ML Organizer")
        logger.info("Press Ctrl+C to stop")
        logger.info("You can now use 'mydata ask' and 'mydata search' in another terminal!")

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
            init_services(self.crypto, self.db, self.storage, self.embedder, self.vectordb, self.pipeline, self._api_startup_event)

            uvicorn.run(app, host=self.settings.api_host, port=self.settings.api_port, log_level="error")

        api_thread = threading.Thread(target=run_server, daemon=True)
        api_thread.start()
        self._threads.append(api_thread)
        # Wait for API server to signal its readiness
        if not self._api_startup_event.wait(timeout=10):  # Wait up to 10 seconds
            logger.error("API server did not start in time!")
            self.stop()

    def stop(self) -> None:
        """Stop all services"""
        logger.info("Shutting down...")
        self._running = False

        if self.file_watcher:
            self.file_watcher.stop()

        for email_watcher in self.email_watchers:
            email_watcher.stop()

        # Wait for all threads to finish
        for thread in self._threads:
            if thread.is_alive():
                thread.join(timeout=1)  # Give threads 1 second to shut down

        logger.info("All services stopped")
        sys.exit(0)

    def _signal_handler(self, signum, frame):
        """Handle termination signals"""
        self.stop()

    def _start_file_watcher(self) -> None:
        """Start file watcher service"""
        watch_dirs = [Path(d) for d in self.settings.watch_directories]

        # Filter to existing directories
        existing_dirs = [d for d in watch_dirs if d.exists()]

        if not existing_dirs:
            logger.warning("No valid watch directories found")
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

        def on_email_received(email_data: Dict):
            """Callback for new emails"""
            self.pipeline.ingest_email(email_data)

        # Mac: Use AppleScript to access Outlook ONLY
        if IS_MAC and MAC_EMAIL_AVAILABLE:
            try:
                # Only use Outlook on Mac (no Mail.app)
                outlook_watcher = MacEmailWatcher(
                    email_type="outlook",
                    on_email_received=on_email_received,
                    poll_interval=self.settings.mac_outlook_poll_interval,
                    days_back=self.settings.mac_outlook_days_back,
                )
                outlook_thread = threading.Thread(target=outlook_watcher.start, daemon=True)
                outlook_thread.start()
                self._threads.append(outlook_thread)
                self.email_watchers.append(outlook_watcher)
                logger.info("Using AppleScript for Microsoft Outlook")
                return

            except Exception as e:
                logger.warning(f"Outlook watcher failed: {e}")
                logger.warning("Falling back to IMAP...")

        # Windows: Try Outlook watcher (no password needed!)
        elif IS_WINDOWS and OUTLOOK_AVAILABLE:
            try:
                # Configure: 60 days (2 months) of history, watch both inbox and sent
                outlook_watcher = OutlookWatcher(
                    on_email_received,
                    history_hours=self.settings.win_outlook_history_hours,
                    watch_sent=self.settings.win_outlook_watch_sent,
                )

                # Start in separate thread
                outlook_thread = threading.Thread(target=outlook_watcher.start, daemon=True)
                outlook_thread.start()
                self._threads.append(outlook_thread)
                self.email_watchers.append(outlook_watcher)

                logger.info("Using local Outlook (win32com)")
                return

            except Exception as e:
                logger.warning(f"Outlook watcher failed: {e}")
                logger.warning("Falling back to IMAP...")

        # Fallback to IMAP if platform-specific watchers not available
        session = self.db.session()
        credentials = session.exec(select(EmailCredential).where(EmailCredential.enabled == True)).all()

        if not credentials:
            logger.info("No email accounts configured")
            logger.info("Tip: Configure email with: mydata email-add your@email.com")
            return

        for cred in credentials:
            # Decrypt password
            password = self.crypto.decrypt_str(cred.encrypted_password)

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
            time.sleep(self.settings.ml_loop_interval_seconds)
            iteration += 1

            try:
                current_time = datetime.now().strftime("%H:%M:%S")
                logger.info(f"[HEARTBEAT] [{current_time}] System active - Iteration #{iteration}")
                logger.info(f"[HEARTBEAT] Services: API ✓ | File Watcher ✓ | Email ✓ | ML ✓")

                logger.info(f"[ML] Running periodic organization (cycle #{iteration})...")
                result = self.ml_organizer.run_clustering()

                if result.get("status") == "ok":
                    logger.info(f"[ML] Organization cycle #{iteration} complete")
                else:
                    logger.warning(f"[ML] Cycle #{iteration} skipped: {result.get('reason', 'unknown')}")

                logger.info(f"[ML] Next organization in {self.settings.ml_loop_interval_seconds} seconds ({datetime.now().strftime('%H:%M:%S')})")

            except Exception as e:
                logger.error(f"[ML] Error in cycle #{iteration}: {e}")
                logger.error(f"[ML] Traceback: {traceback.format_exc()}")
