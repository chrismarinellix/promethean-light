"""File system watcher for automatic ingestion"""

import time
from pathlib import Path
from typing import Callable, List, Union
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileSystemEvent


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

    def start(self) -> None:
        """Start watching directories"""
        for watch_dir in self.watch_dirs:
            if not watch_dir.exists():
                print(f"⚠ Watch directory does not exist: {watch_dir}")
                continue

            self.observer.schedule(self.handler, str(watch_dir), recursive=self.recursive)
            print(f"👁 Watching: {watch_dir}")

        self.observer.start()
        self._running = True
        print("✓ File watcher started")

    def stop(self) -> None:
        """Stop watching"""
        if self._running:
            self.observer.stop()
            self.observer.join()
            self._running = False
            print("✓ File watcher stopped")

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

        print(f"📄 New file detected: {file_path.name}")
        self.processed_files.add(str(file_path))

        try:
            self.on_file_created(file_path)
        except Exception as e:
            print(f"Error processing {file_path}: {e}")

    def on_modified(self, event: FileSystemEvent) -> None:
        """Called when a file is modified"""
        # Optionally handle modifications
        pass
