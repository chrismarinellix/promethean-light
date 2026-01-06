"""
Backup System for Promethean Light - OPTIMIZED INCREMENTAL VERSION
Backs up SQLite database, Qdrant vector DB, and program files
Implements rotation policy: 7 daily, 4 weekly, 12 monthly backups

EFFICIENCY FEATURES:
- Databases: Always full backup (for consistency)
- Program files: Hard-link unchanged files (70-80% space savings)
- Incremental daily backups (Mon-Sat)
- Full backups weekly (Sunday) and monthly (1st)
"""

import os
import shutil
import sqlite3
import hashlib
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional, Dict, Set
import logging
import sys
import subprocess

# Configuration
BACKUP_ROOT = Path(r"V:\mel_energy_office\Business Dev\Data Base Backup")
SOURCE_DIR = Path(__file__).parent.resolve()
SQLITE_DB = SOURCE_DIR / "mydata" / "mydata.db"
QDRANT_DIR = Path.home() / ".mydata" / "qdrant"
LOG_DIR = BACKUP_ROOT / "logs"

# Retention policy
HOURLY_RETENTION = 24  # Keep last 24 hours (work hours only: 8am-6pm)
DAILY_RETENTION = 7  # Keep last 7 days
WEEKLY_RETENTION = 4  # Keep last 4 weeks
MONTHLY_RETENTION = 12  # Keep last 12 months


class BackupManager:
    """Manages automated backups with incremental optimization"""

    def __init__(self):
        self.backup_root = BACKUP_ROOT
        self.setup_logging()
        self.ensure_backup_structure()
        self.stats = {
            'files_linked': 0,
            'files_copied': 0,
            'space_saved': 0
        }

    def setup_logging(self):
        """Configure logging to file and console"""
        LOG_DIR.mkdir(parents=True, exist_ok=True)
        log_file = LOG_DIR / f"backup_{datetime.now().strftime('%Y%m')}.log"

        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file, encoding='utf-8'),
                logging.StreamHandler(sys.stdout)
            ]
        )
        self.logger = logging.getLogger(__name__)

    def ensure_backup_structure(self):
        """Create backup directory structure"""
        dirs = [
            self.backup_root / "hourly",
            self.backup_root / "daily",
            self.backup_root / "weekly",
            self.backup_root / "monthly",
            LOG_DIR
        ]
        for d in dirs:
            d.mkdir(parents=True, exist_ok=True)

    def backup_sqlite(self, dest_dir: Path) -> bool:
        """Backup SQLite database using safe copy (always full backup)"""
        try:
            if not SQLITE_DB.exists():
                self.logger.warning(f"SQLite database not found: {SQLITE_DB}")
                return False

            dest_file = dest_dir / "mydata.db"

            # Use SQLite backup API for safe hot-copy
            source_conn = sqlite3.connect(str(SQLITE_DB))
            dest_conn = sqlite3.connect(str(dest_file))

            source_conn.backup(dest_conn)

            source_conn.close()
            dest_conn.close()

            size_mb = dest_file.stat().st_size / (1024 * 1024)
            self.logger.info(f"[OK] SQLite backup: {dest_file.name} ({size_mb:.2f} MB)")
            return True

        except Exception as e:
            self.logger.error(f"[ERROR] SQLite backup failed: {e}")
            return False

    def backup_qdrant(self, dest_dir: Path) -> bool:
        """Backup Qdrant vector database (always full backup for consistency)"""
        try:
            if not QDRANT_DIR.exists():
                self.logger.warning(f"Qdrant directory not found: {QDRANT_DIR}")
                return False

            dest_qdrant = dest_dir / "qdrant"

            # Remove existing backup if present
            if dest_qdrant.exists():
                shutil.rmtree(dest_qdrant)

            # Copy entire Qdrant directory (excluding lock files)
            shutil.copytree(
                QDRANT_DIR,
                dest_qdrant,
                ignore=shutil.ignore_patterns('*.lock')
            )

            size_mb = sum(f.stat().st_size for f in dest_qdrant.rglob('*') if f.is_file()) / (1024 * 1024)
            self.logger.info(f"[OK] Qdrant backup: {dest_qdrant.name} ({size_mb:.2f} MB)")
            return True

        except Exception as e:
            self.logger.error(f"[ERROR] Qdrant backup failed: {e}")
            return False

    def get_previous_backup(self, backup_type: str, exclude_name: Optional[str] = None) -> Optional[Path]:
        """Get the most recent backup directory for incremental comparison

        Args:
            backup_type: Type of backup (daily, weekly, monthly, hourly)
            exclude_name: Backup name to exclude (usually the current backup being created)
        """
        backup_dir = self.backup_root / backup_type
        if not backup_dir.exists():
            return None

        backups = sorted(
            [d for d in backup_dir.iterdir()
             if d.is_dir() and (exclude_name is None or d.name != exclude_name)],
            key=lambda x: x.stat().st_mtime,
            reverse=True
        )

        return backups[0] if backups else None

    def file_changed(self, source_file: Path, dest_file: Path) -> bool:
        """Check if file has changed (using size + mtime for speed)"""
        if not dest_file.exists():
            return True

        source_stat = source_file.stat()
        dest_stat = dest_file.stat()

        # Compare size first (exact match required)
        if source_stat.st_size != dest_stat.st_size:
            return True

        # Compare modification time with 3-second tolerance
        # (filesystem precision and copy operations can cause small differences)
        mtime_diff = abs(source_stat.st_mtime - dest_stat.st_mtime)
        if mtime_diff > 3:
            return True

        return False

    def create_hardlink(self, source: Path, dest: Path) -> bool:
        """Create hard link on Windows using os.link()"""
        try:
            dest.parent.mkdir(parents=True, exist_ok=True)
            # Remove destination if it already exists
            if dest.exists():
                dest.unlink()
            # Create hard link (works on NTFS)
            os.link(str(source), str(dest))
            return True
        except (OSError, PermissionError) as e:
            # Hard link failed - will fall back to copy
            # This can happen if:
            # - Source and dest on different drives
            # - File system doesn't support hard links (FAT32)
            # - Insufficient permissions
            return False

    def backup_program_incremental(self, dest_dir: Path, previous_backup: Optional[Path], is_full: bool = False) -> bool:
        """Backup program files with incremental optimization

        EFFICIENCY STRATEGY:
        - Full backup: Copy all files
        - Incremental: Try hard links first (same drive), fallback to skip-if-unchanged copy
        - Cross-drive: Hard links don't work, but we skip copying unchanged files (saves TIME)
        """
        try:
            dest_program = dest_dir / "promethean_light"
            dest_program.mkdir(parents=True, exist_ok=True)

            # Define ignore patterns
            device_names = {'CON', 'PRN', 'AUX', 'NUL', 'COM1', 'COM2', 'COM3', 'COM4',
                           'COM5', 'COM6', 'COM7', 'COM8', 'COM9', 'LPT1', 'LPT2', 'LPT3',
                           'LPT4', 'LPT5', 'LPT6', 'LPT7', 'LPT8', 'LPT9'}
            ignore_patterns = {'__pycache__', '.pyc', '.pyo', '.pyd', '.git', '.venv',
                              'venv', '.mydata', '.log', '.tmp', '.DS_Store'}

            def should_ignore(path: Path) -> bool:
                """Check if file should be ignored"""
                if path.name.upper() in device_names:
                    return True
                for pattern in ignore_patterns:
                    if pattern.startswith('.'):
                        if path.suffix == pattern or path.name == pattern:
                            return True
                    else:
                        if pattern in str(path):
                            return True
                return False

            files_copied = 0
            files_linked = 0
            files_skipped = 0
            space_saved = 0
            time_saved_files = 0
            hardlink_failures = 0

            # Log previous backup info for debugging
            if previous_backup:
                self.logger.info(f"     Using previous backup for comparison: {previous_backup.name}")

            # Walk through source directory
            for source_file in SOURCE_DIR.rglob('*'):
                if source_file.is_file() and not should_ignore(source_file):
                    # Calculate relative path
                    rel_path = source_file.relative_to(SOURCE_DIR)
                    dest_file = dest_program / rel_path

                    # Check if we should use incremental optimization
                    if not is_full and previous_backup:
                        prev_file = previous_backup / "promethean_light" / rel_path

                        if prev_file.exists():
                            file_is_changed = self.file_changed(source_file, prev_file)
                            if not file_is_changed:
                                # File unchanged - try hard link first
                                if self.create_hardlink(prev_file, dest_file):
                                    files_linked += 1
                                    space_saved += source_file.stat().st_size
                                    time_saved_files += 1
                                    continue
                                else:
                                    # Hard link failed (likely cross-drive) - copy from previous backup
                                    hardlink_failures += 1
                                    dest_file.parent.mkdir(parents=True, exist_ok=True)
                                    shutil.copy2(prev_file, dest_file)
                                    files_skipped += 1
                                    time_saved_files += 1  # Still saved time by not reading from source
                                    continue

                    # File is new or changed - copy from source
                    dest_file.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(source_file, dest_file)
                    files_copied += 1

            size_mb = sum(f.stat().st_size for f in dest_program.rglob('*') if f.is_file()) / (1024 * 1024)
            space_saved_mb = space_saved / (1024 * 1024)

            if is_full:
                self.logger.info(f"[OK] Program backup (FULL): {dest_program.name} ({size_mb:.2f} MB)")
                self.logger.info(f"     Files: {files_copied} copied")
            else:
                total_files = files_copied + files_linked + files_skipped
                efficiency_pct = (time_saved_files / total_files * 100) if total_files > 0 else 0

                self.logger.info(f"[OK] Program backup (INCREMENTAL): {dest_program.name} ({size_mb:.2f} MB)")
                self.logger.info(f"     Files: {files_copied} new/changed, {files_linked} linked, {files_skipped} reused")

                if hardlink_failures > 0 and files_linked == 0:
                    self.logger.info(f"     [INFO] Cross-drive backup detected (C: -> V:) - using copy optimization")
                    self.logger.info(f"     Time efficiency: {efficiency_pct:.1f}% of files reused (no re-read from source)")

                if space_saved_mb > 0:
                    self.logger.info(f"     Space saved via hard links: {space_saved_mb:.2f} MB ({(space_saved_mb/size_mb*100):.1f}%)")

            self.stats['files_copied'] += files_copied
            self.stats['files_linked'] += files_linked
            self.stats['space_saved'] += space_saved

            return True

        except Exception as e:
            self.logger.error(f"[ERROR] Program backup failed: {e}")
            return False

    def create_backup(self, backup_type: str, is_full: bool = False) -> Optional[Path]:
        """Create a backup (full or incremental)"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_name = f"backup_{timestamp}"
        backup_dir = self.backup_root / backup_type / backup_name

        mode = "FULL" if is_full else "INCREMENTAL"
        self.logger.info("=" * 60)
        self.logger.info(f"Starting {backup_type} backup ({mode}): {backup_name}")
        self.logger.info("=" * 60)

        try:
            # Get previous backup BEFORE creating the new directory
            previous_backup = None if is_full else self.get_previous_backup(backup_type, exclude_name=backup_name)

            # Now create the backup directory
            backup_dir.mkdir(parents=True, exist_ok=True)

            # Databases always get full backup for consistency
            sqlite_ok = self.backup_sqlite(backup_dir)
            qdrant_ok = self.backup_qdrant(backup_dir)

            # Program files can be incremental
            program_ok = self.backup_program_incremental(backup_dir, previous_backup, is_full)

            if sqlite_ok and qdrant_ok and program_ok:
                # Write backup manifest
                manifest = backup_dir / "BACKUP_INFO.txt"
                with open(manifest, 'w') as f:
                    f.write(f"Backup Type: {backup_type} ({mode})\n")
                    f.write(f"Created: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                    f.write(f"Source: {SOURCE_DIR}\n")
                    f.write(f"SQLite: {SQLITE_DB}\n")
                    f.write(f"Qdrant: {QDRANT_DIR}\n")
                    if previous_backup and not is_full:
                        f.write(f"Based on: {previous_backup.name}\n")
                    f.write(f"\nContents:\n")
                    f.write(f"  - mydata.db (SQLite database - FULL)\n")
                    f.write(f"  - qdrant/ (Vector database - FULL)\n")
                    f.write(f"  - promethean_light/ (Program files - {mode})\n")

                total_size = sum(f.stat().st_size for f in backup_dir.rglob('*') if f.is_file()) / (1024 * 1024)
                self.logger.info(f"[OK] Backup completed successfully: {total_size:.2f} MB total")
                self.logger.info(f"[OK] Location: {backup_dir}")
                return backup_dir
            else:
                self.logger.error("[ERROR] Backup incomplete - some components failed")
                return None

        except Exception as e:
            self.logger.error(f"Backup failed: {e}")
            return None

    def cleanup_old_backups(self):
        """Remove old backups according to retention policy"""
        self.logger.info("Checking retention policy...")

        # Hourly backups: keep last 24 hours
        self._cleanup_directory(
            self.backup_root / "hourly",
            HOURLY_RETENTION,
            "hourly"
        )

        # Daily backups: keep last 7 days
        self._cleanup_directory(
            self.backup_root / "daily",
            DAILY_RETENTION,
            "daily"
        )

        # Weekly backups: keep last 4 weeks
        self._cleanup_directory(
            self.backup_root / "weekly",
            WEEKLY_RETENTION,
            "weekly"
        )

        # Monthly backups: keep last 12 months
        self._cleanup_directory(
            self.backup_root / "monthly",
            MONTHLY_RETENTION,
            "monthly"
        )

    def _cleanup_directory(self, directory: Path, keep_count: int, backup_type: str):
        """Clean up old backups in a directory"""
        if not directory.exists():
            return

        # Get all backup directories sorted by modification time (newest first)
        backups = sorted(
            [d for d in directory.iterdir() if d.is_dir()],
            key=lambda x: x.stat().st_mtime,
            reverse=True
        )

        if len(backups) > keep_count:
            to_delete = backups[keep_count:]
            for backup in to_delete:
                try:
                    shutil.rmtree(backup)
                    self.logger.info(f"[OK] Removed old {backup_type} backup: {backup.name}")
                except Exception as e:
                    self.logger.error(f"[ERROR] Failed to remove {backup}: {e}")

    def should_create_weekly(self) -> bool:
        """Check if we should create a weekly backup (Sunday)"""
        return datetime.now().weekday() == 6  # Sunday

    def should_create_monthly(self) -> bool:
        """Check if we should create a monthly backup (1st of month)"""
        return datetime.now().day == 1

    def run_scheduled_backup(self):
        """Run backup according to schedule with incremental optimization"""
        self.logger.info("=" * 60)
        self.logger.info("  PROMETHEAN LIGHT - AUTOMATED BACKUP (OPTIMIZED)")
        self.logger.info("=" * 60)

        try:
            is_sunday = self.should_create_weekly()
            is_first = self.should_create_monthly()

            # Determine if today's daily backup should be full
            # Full backup on Sunday (will also create weekly) or 1st (will also create monthly)
            daily_is_full = is_sunday or is_first

            # Create daily backup (full on Sunday/1st, incremental otherwise)
            if daily_is_full:
                self.logger.info("\n[INFO] Today is Sunday or 1st - creating FULL daily backup")
            daily_backup = self.create_backup("daily", is_full=daily_is_full)

            # Create weekly backup if it's Sunday (always full)
            if is_sunday:
                self.logger.info("\n>> Creating weekly backup (Sunday - FULL)...")
                self.create_backup("weekly", is_full=True)

            # Create monthly backup if it's the 1st (always full)
            if is_first:
                self.logger.info("\n>> Creating monthly backup (1st of month - FULL)...")
                self.create_backup("monthly", is_full=True)

            # Clean up old backups
            self.logger.info("")
            self.cleanup_old_backups()

            # Print efficiency stats
            if self.stats['files_linked'] > 0:
                total_files = self.stats['files_copied'] + self.stats['files_linked']
                space_saved_mb = self.stats['space_saved'] / (1024 * 1024)
                efficiency = (self.stats['files_linked'] / total_files * 100) if total_files > 0 else 0

                self.logger.info("\n" + "=" * 60)
                self.logger.info("EFFICIENCY STATS:")
                self.logger.info(f"  Files processed: {total_files}")
                self.logger.info(f"  Files linked (unchanged): {self.stats['files_linked']} ({efficiency:.1f}%)")
                self.logger.info(f"  Files copied (new/changed): {self.stats['files_copied']}")
                self.logger.info(f"  Space saved: {space_saved_mb:.2f} MB")
                self.logger.info("=" * 60)

            self.logger.info("\n" + "=" * 60)
            self.logger.info("Backup process completed successfully")
            self.logger.info("=" * 60)

            return True

        except Exception as e:
            self.logger.error(f"Backup process failed: {e}", exc_info=True)
            return False

    def run_hourly_backup(self):
        """Run hourly backup (incremental, work hours only: 8am-6pm)"""
        current_hour = datetime.now().hour

        # Only run during work hours (8am-6pm)
        if current_hour < 8 or current_hour > 18:
            self.logger.info(f"[INFO] Skipping hourly backup - outside work hours (current: {current_hour}:00)")
            return True

        self.logger.info("=" * 60)
        self.logger.info(f"  HOURLY BACKUP - {datetime.now().strftime('%Y-%m-%d %I:%M %p')}")
        self.logger.info("=" * 60)

        try:
            # Create incremental hourly backup
            hourly_backup = self.create_backup("hourly", is_full=False)

            if not hourly_backup:
                self.logger.error("[ERROR] Hourly backup failed")
                return False

            # Clean up old hourly backups (keep last 24)
            self._cleanup_directory(
                self.backup_root / "hourly",
                HOURLY_RETENTION,
                "hourly"
            )

            # Print efficiency stats
            if self.stats['files_linked'] > 0:
                total_files = self.stats['files_copied'] + self.stats['files_linked']
                space_saved_mb = self.stats['space_saved'] / (1024 * 1024)
                efficiency = (self.stats['files_linked'] / total_files * 100) if total_files > 0 else 0

                self.logger.info("\n" + "=" * 60)
                self.logger.info("EFFICIENCY STATS:")
                self.logger.info(f"  Files linked (unchanged): {self.stats['files_linked']} ({efficiency:.1f}%)")
                self.logger.info(f"  Files copied (new/changed): {self.stats['files_copied']}")
                self.logger.info(f"  Space saved: {space_saved_mb:.2f} MB")
                self.logger.info("=" * 60)

            self.logger.info("\n" + "=" * 60)
            self.logger.info("Hourly backup completed successfully")
            self.logger.info("=" * 60)

            return True

        except Exception as e:
            self.logger.error(f"Hourly backup failed: {e}", exc_info=True)
            return False


def main():
    """Main entry point for daily/weekly/monthly backups"""
    try:
        manager = BackupManager()
        success = manager.run_scheduled_backup()
        sys.exit(0 if success else 1)
    except Exception as e:
        logging.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)


def main_hourly():
    """Main entry point for hourly backups"""
    try:
        manager = BackupManager()
        success = manager.run_hourly_backup()
        sys.exit(0 if success else 1)
    except Exception as e:
        logging.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    # Check command-line argument for backup type
    if len(sys.argv) > 1 and sys.argv[1] == "--hourly":
        main_hourly()
    else:
        main()
