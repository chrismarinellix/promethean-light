"""File system watcher for automatic ingestion"""

import time
from datetime import datetime, date
from pathlib import Path
from typing import Callable, List, Optional, Set, Union
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileSystemEvent


# Supported file extensions for ingestion
SUPPORTED_EXTENSIONS = {
    '.txt', '.md', '.csv', '.json', '.log',  # Plain text
    '.pdf',  # PDF
    '.docx',  # Word
    '.xlsx', '.xls',  # Excel
}


class FileWatcher:
    """Watches directories for new files and triggers ingestion"""

    def __init__(
        self, watch_dirs: List[Union[str, Path]], on_file_created: Callable[[Path], None], recursive: bool = True
    ):
        self.watch_dirs = [Path(d).expanduser() for d in watch_dirs]
        self.on_file_created = on_file_created
        self.recursive = recursive
        self.observer = Observer()
        self._running = False

        # Create handler
        self.handler = FileCreatedHandler(self.on_file_created)

    def start(self, scan_today: bool = True) -> None:
        """Start watching directories

        Args:
            scan_today: If True, scan for files created/modified today and ingest them
        """
        for watch_dir in self.watch_dirs:
            if not watch_dir.exists():
                print(f"[WARN] Watch directory does not exist: {watch_dir}")
                continue

            self.observer.schedule(self.handler, str(watch_dir), recursive=self.recursive)
            print(f"[WATCH] Watching: {watch_dir}")

        self.observer.start()
        self._running = True
        print("[OK] File watcher started")

        # Scan for today's files on startup
        if scan_today:
            self._ingest_todays_files()

    def _ingest_todays_files(self) -> None:
        """Scan watched directories for files created/modified today and ingest them.

        This runs once on startup to catch any files that were added before
        the watcher started. Already-ingested files are skipped via file_hash
        deduplication in the ingestion layer.
        """
        today = date.today()
        files_found = 0
        files_queued = 0

        print(f"[SCAN] Scanning for today's files ({today.strftime('%Y-%m-%d')})...")

        for watch_dir in self.watch_dirs:
            if not watch_dir.exists():
                continue

            # Scan directory (recursively if configured)
            pattern = "**/*" if self.recursive else "*"
            for file_path in watch_dir.glob(pattern):
                # Skip directories
                if file_path.is_dir():
                    continue

                # Skip unsupported extensions
                if file_path.suffix.lower() not in SUPPORTED_EXTENSIONS:
                    continue

                # Skip hidden/temp files
                if file_path.name.startswith(".") or file_path.name.startswith("~"):
                    continue

                # Check if file was created/modified today
                try:
                    mtime = datetime.fromtimestamp(file_path.stat().st_mtime).date()
                    if mtime == today:
                        files_found += 1

                        # Skip if already processed this session
                        if str(file_path) in self.handler.processed_files:
                            continue

                        # Mark as processed
                        self.handler.processed_files.add(str(file_path))
                        files_queued += 1

                        # Trigger ingestion
                        try:
                            print(f"[SCAN] Found today's file: {file_path.name}")
                            self.on_file_created(file_path)
                        except Exception as e:
                            print(f"[SCAN] Error ingesting {file_path.name}: {e}")

                except Exception:
                    # Skip files we can't stat
                    continue

        if files_found > 0:
            print(f"[SCAN] Complete: {files_queued} new files queued for ingestion (of {files_found} found today)")
        else:
            print(f"[SCAN] No new files from today found in watched directories")

    def stop(self) -> None:
        """Stop watching"""
        if self._running:
            self.observer.stop()
            self.observer.join()
            self._running = False
            print("[OK] File watcher stopped")

    def is_running(self) -> bool:
        """Check if watcher is running"""
        return self._running


class FileCreatedHandler(FileSystemEventHandler):
    """Handles file creation events"""

    def __init__(self, on_file_created: Callable[[Path], None]):
        self.on_file_created = on_file_created
        self.processed_files = set()

    def on_created(self, event: FileSystemEvent) -> None:
        """Called when a file is created"""
        if event.is_directory:
            return

        file_path = Path(event.src_path)

        # Skip temporary files and hidden files
        if file_path.name.startswith(".") or file_path.name.startswith("~"):
            return

        # Skip already processed files
        if str(file_path) in self.processed_files:
            return

        # Wait a bit to ensure file is fully written
        time.sleep(0.5)

        # Skip if file was deleted in the meantime
        if not file_path.exists():
            return

        print(f"[FILE] New file detected: {file_path.name}")
        self.processed_files.add(str(file_path))

        try:
            self.on_file_created(file_path)
        except Exception as e:
            print(f"Error processing {file_path}: {e}")

    def on_modified(self, event: FileSystemEvent) -> None:
        """Called when a file is modified"""
        # Optionally handle modifications
        pass
