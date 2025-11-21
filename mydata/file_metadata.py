"""
File metadata extraction for change tracking.

Extracts file timestamps, ownership, and Windows attributes.
"""

import os
import platform
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict
import stat


def get_file_metadata(file_path: Path) -> Dict:
    """
    Extract comprehensive file metadata for change tracking.

    Returns:
        Dict with:
        - modified_at: Last modification time
        - created_at: File creation time
        - size_bytes: File size
        - owner: File owner (Windows username or Unix UID)
    """
    try:
        stat_info = file_path.stat()

        metadata = {
            'modified_at': datetime.fromtimestamp(stat_info.st_mtime),
            'created_at': datetime.fromtimestamp(stat_info.st_ctime),
            'size_bytes': stat_info.st_size,
            'owner': None,
        }

        # Try to get file owner (Windows-specific)
        if platform.system() == 'Windows':
            try:
                import win32security
                import win32api

                # Get file owner SID
                sd = win32security.GetFileSecurity(
                    str(file_path),
                    win32security.OWNER_SECURITY_INFORMATION
                )
                owner_sid = sd.GetSecurityDescriptorOwner()

                # Convert SID to account name
                name, domain, type = win32security.LookupAccountSid(None, owner_sid)
                metadata['owner'] = f"{domain}\\{name}" if domain else name

            except Exception:
                # Fallback: just get the username
                try:
                    metadata['owner'] = win32api.GetUserName()
                except Exception:
                    pass

        else:
            # Unix/Linux: Get owner UID/username
            try:
                import pwd
                metadata['owner'] = pwd.getpwuid(stat_info.st_uid).pw_name
            except Exception:
                metadata['owner'] = str(stat_info.st_uid)

        return metadata

    except Exception as e:
        # Return minimal metadata if extraction fails
        return {
            'modified_at': None,
            'created_at': None,
            'size_bytes': 0,
            'owner': None,
            'error': str(e)
        }


def get_recent_changes(directory: Path, days: int = 30) -> list:
    """
    Find files modified in the last N days.

    Args:
        directory: Directory to scan
        days: Number of days to look back

    Returns:
        List of (file_path, metadata) tuples
    """
    from datetime import timedelta

    cutoff_date = datetime.now() - timedelta(days=days)
    recent_files = []

    for file_path in directory.rglob("*"):
        if file_path.is_file():
            metadata = get_file_metadata(file_path)
            if metadata['modified_at'] and metadata['modified_at'] > cutoff_date:
                recent_files.append((file_path, metadata))

    # Sort by modification time (newest first)
    recent_files.sort(key=lambda x: x[1]['modified_at'], reverse=True)

    return recent_files


def compare_directories(dir1: Path, dir2: Path) -> Dict:
    """
    Compare two directory snapshots to find changes.

    Args:
        dir1: First directory (e.g., current state)
        dir2: Second directory (e.g., backup/snapshot)

    Returns:
        Dict with:
        - added: Files in dir1 but not dir2
        - deleted: Files in dir2 but not dir1
        - modified: Files with different modification times or sizes
    """
    def get_file_map(directory):
        file_map = {}
        for file_path in directory.rglob("*"):
            if file_path.is_file():
                rel_path = file_path.relative_to(directory)
                metadata = get_file_metadata(file_path)
                file_map[str(rel_path)] = metadata
        return file_map

    files1 = get_file_map(dir1)
    files2 = get_file_map(dir2)

    added = {f: files1[f] for f in files1 if f not in files2}
    deleted = {f: files2[f] for f in files2 if f not in files1}

    modified = {}
    for file in set(files1.keys()) & set(files2.keys()):
        if (files1[file]['modified_at'] != files2[file]['modified_at'] or
            files1[file]['size_bytes'] != files2[file]['size_bytes']):
            modified[file] = {
                'before': files2[file],
                'after': files1[file]
            }

    return {
        'added': added,
        'deleted': deleted,
        'modified': modified
    }


def get_files_by_author(directory: Path, author: str = None) -> Dict:
    """
    Group files by owner/author.

    Args:
        directory: Directory to scan
        author: Specific author to filter (optional)

    Returns:
        Dict mapping author -> list of files
    """
    by_author = {}

    for file_path in directory.rglob("*"):
        if file_path.is_file():
            metadata = get_file_metadata(file_path)
            owner = metadata.get('owner', 'Unknown')

            if author and owner != author:
                continue

            if owner not in by_author:
                by_author[owner] = []

            by_author[owner].append({
                'path': file_path,
                'metadata': metadata
            })

    return by_author


def create_change_timeline(directory: Path, limit: int = 100) -> list:
    """
    Create a timeline of file changes sorted by modification date.

    Args:
        directory: Directory to scan
        limit: Maximum number of files to return

    Returns:
        List of (file_path, metadata) sorted by modification time
    """
    all_files = []

    for file_path in directory.rglob("*"):
        if file_path.is_file():
            metadata = get_file_metadata(file_path)
            if metadata['modified_at']:
                all_files.append((file_path, metadata))

    # Sort by modification time (newest first)
    all_files.sort(key=lambda x: x[1]['modified_at'], reverse=True)

    return all_files[:limit]


if __name__ == '__main__':
    # Example usage
    import sys
    from rich.console import Console
    from rich.table import Table

    console = Console()

    if len(sys.argv) < 2:
        console.print("[yellow]Usage: python -m mydata.file_metadata <directory> [--recent-days=30][/yellow]")
        sys.exit(1)

    directory = Path(sys.argv[1])
    days = 30

    # Parse --recent-days flag
    for arg in sys.argv:
        if arg.startswith('--recent-days='):
            days = int(arg.split('=')[1])

    if not directory.exists():
        console.print(f"[red]Directory not found: {directory}[/red]")
        sys.exit(1)

    console.print(f"\n[bold]Recent Changes (Last {days} days)[/bold]\n")

    recent = get_recent_changes(directory, days=days)

    if not recent:
        console.print(f"[yellow]No files modified in the last {days} days[/yellow]")
    else:
        table = Table(title=f"Files Modified in Last {days} Days")
        table.add_column("File", style="cyan", max_width=50)
        table.add_column("Modified", style="magenta")
        table.add_column("Size", style="green", justify="right")
        table.add_column("Owner", style="yellow")

        for file_path, metadata in recent[:50]:  # Show first 50
            rel_path = str(file_path.relative_to(directory))
            modified = metadata['modified_at'].strftime("%Y-%m-%d %H:%M")
            size_mb = metadata['size_bytes'] / (1024 * 1024)
            owner = metadata.get('owner', 'Unknown')

            table.add_row(rel_path, modified, f"{size_mb:.2f} MB", owner)

        console.print(table)
        console.print(f"\n[dim]Showing {min(50, len(recent))} of {len(recent)} files[/dim]")
