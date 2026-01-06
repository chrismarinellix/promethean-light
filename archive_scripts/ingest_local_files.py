#!/usr/bin/env python3
"""
Ingest all local text files, markdown files, and relevant data files into Promethean Light database.
This will make the data searchable via the UI and chatbot.

Uses the running daemon's API to ingest files.
"""

from __future__ import annotations
import os
import sys
import requests
from pathlib import Path
from typing import List

# Files/folders to skip
SKIP_PATTERNS = [
    'node_modules',
    '.git',
    '__pycache__',
    '.venv',
    'venv',
    'mydata.egg-info',
    'promethean-light-ui',  # Skip UI folder (just code)
    'test_project',
    '.claude',
]

# File extensions to ingest (just txt - md files are mostly documentation)
INCLUDE_EXTENSIONS = {'.txt'}

# Skip these specific files
SKIP_FILES = {
    'requirements.txt',
    'tray_requirements.txt',
    'pyproject.toml',
    'setup.py',
    'setup.cfg',
    '.gitignore',
    'LICENSE',
}

API_BASE = "http://127.0.0.1:8000"


def should_skip(path: Path) -> bool:
    """Check if path should be skipped"""
    path_str = str(path)

    # Skip if in excluded folder
    for pattern in SKIP_PATTERNS:
        if pattern in path_str:
            return True

    # Skip if file is in skip list
    if path.name in SKIP_FILES:
        return True

    return False


def get_files_to_ingest(base_path: Path) -> List[Path]:
    """Get all files to ingest"""
    files = []

    for ext in INCLUDE_EXTENSIONS:
        for f in base_path.rglob(f'*{ext}'):
            if not should_skip(f) and f.is_file():
                files.append(f)

    return files


def check_daemon() -> bool:
    """Check if daemon is running"""
    try:
        resp = requests.get(f"{API_BASE}/stats", timeout=5)
        return resp.status_code == 200
    except:
        return False


def ingest_text(text: str, source: str) -> bool:
    """Ingest text via API"""
    try:
        resp = requests.post(
            f"{API_BASE}/add",
            json={"text": text, "source": source},
            timeout=60
        )
        return resp.status_code == 200
    except Exception as e:
        print(f"    Error: {e}")
        return False


def main():
    base_path = Path(__file__).parent

    print("=" * 80)
    print("PROMETHEAN LIGHT - LOCAL FILE INGESTION")
    print("=" * 80)

    # Check daemon
    print("\nChecking daemon connection...")
    if not check_daemon():
        print("ERROR: Daemon not running!")
        print("Start the daemon first with: python -m mydata daemon")
        sys.exit(1)
    print("Daemon connected.")

    # Get files to ingest
    files = get_files_to_ingest(base_path)

    print(f"\nFound {len(files)} files to ingest:")
    for f in files:
        rel_path = f.relative_to(base_path)
        size = f.stat().st_size
        print(f"  - {rel_path} ({size:,} bytes)")

    if not files:
        print("No files to ingest!")
        return

    # Confirm
    response = input(f"\nIngest {len(files)} files? [y/N]: ").strip().lower()
    if response != 'y':
        print("Aborted.")
        return

    print("\nIngesting files...\n")

    # Ingest files
    success = 0
    failed = 0
    skipped = 0

    for i, file_path in enumerate(files, 1):
        rel_path = file_path.relative_to(base_path)
        print(f"[{i}/{len(files)}] {rel_path}")

        try:
            # Read file content
            content = file_path.read_text(encoding='utf-8', errors='replace')

            # Skip empty files
            if not content.strip():
                print(f"    Skipped (empty)")
                skipped += 1
                continue

            # Skip very small files (less than 50 chars)
            if len(content.strip()) < 50:
                print(f"    Skipped (too small: {len(content)} chars)")
                skipped += 1
                continue

            # Create source identifier
            source = f"file:{rel_path}"

            # Ingest via API
            if ingest_text(content, source):
                print(f"    Success")
                success += 1
            else:
                print(f"    Failed")
                failed += 1

        except Exception as e:
            print(f"    Error: {e}")
            failed += 1

    print("\n" + "=" * 80)
    print("INGESTION COMPLETE")
    print("=" * 80)
    print(f"  Success: {success}")
    print(f"  Failed:  {failed}")
    print(f"  Skipped: {skipped}")
    print(f"  Total:   {len(files)}")
    print("=" * 80)


if __name__ == "__main__":
    main()
