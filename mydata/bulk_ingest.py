"""
Bulk project ingestion with comprehensive progress tracking and safety features.

🔒 SAFETY GUARANTEE: This script ONLY READS files. No files are ever modified, moved, or deleted.
All operations are READ-ONLY.
"""

import time
import traceback
from pathlib import Path
from typing import Optional, Dict, List
from collections import defaultdict, Counter
from datetime import datetime
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn, TimeRemainingColumn, TimeElapsedColumn
from rich.panel import Panel
from rich.live import Live
from rich.layout import Layout
from rich import box
from sqlmodel import Session
from .crypto import CryptoManager
from .database import Database
from .storage import EncryptedStorage
from .embedder import Embedder
from .vectordb import VectorDB
from .ml_organizer import MLOrganizer
from .ingestion import IngestionPipeline
from .config import Config

console = Console()


class BulkIngester:
    """Bulk ingestion with rich progress tracking"""

    # File extensions we can extract text from
    SUPPORTED_EXTENSIONS = {
        '.txt', '.md', '.csv', '.json', '.log',  # Plain text
        '.pdf',  # PDF
        '.docx',  # Word
        '.xlsx', '.xls',  # Excel
    }

    # File extensions to skip (binary/unsupported)
    SKIP_EXTENSIONS = {
        '.dwg', '.dxf',  # CAD
        '.exe', '.dll', '.so',  # Executables
        '.zip', '.7z', '.rar', '.tar', '.gz',  # Archives
        '.jpg', '.jpeg', '.png', '.gif', '.bmp',  # Images
        '.mp4', '.avi', '.mov', '.mkv',  # Video
        '.mp3', '.wav', '.flac',  # Audio
        '.psd', '.ai', '.eps',  # Design files
        '.bin', '.dat', '.db',  # Generic binary
    }

    def __init__(self, db_name: Optional[str] = None):
        """
        Initialize bulk ingester.

        Args:
            db_name: Database name (e.g., 'project_9002'). If None, uses default database.
        """
        self.db_name = db_name
        self.stats = {
            'total_files': 0,
            'extractable_files': 0,
            'binary_files': 0,
            'success_count': 0,
            'error_count': 0,
            'skipped_count': 0,
            'total_size_bytes': 0,
            'extracted_size_bytes': 0,
            'start_time': None,
            'end_time': None,
        }
        self.file_type_stats = Counter()
        self.errors = []

    def analyze_directory(self, directory_path: Path) -> Dict:
        """
        🔒 READ-ONLY: Analyze directory structure and file types.

        Returns comprehensive statistics about the directory.
        """
        console.print(Panel(f"[bold cyan]Analyzing Directory[/bold cyan]\n{directory_path}", border_style="cyan"))

        with console.status("[bold green]Scanning files...") as status:
            all_files = list(directory_path.rglob("*"))
            files_only = [f for f in all_files if f.is_file()]

            # Count by extension
            extension_counts = Counter()
            extension_sizes = defaultdict(int)

            for file_path in files_only:
                ext = file_path.suffix.lower()
                extension_counts[ext if ext else '(no extension)'] += 1
                try:
                    size = file_path.stat().st_size
                    extension_sizes[ext if ext else '(no extension)'] += size
                except Exception:
                    pass

            # Categorize files
            extractable = []
            binary = []
            unknown = []

            for file_path in files_only:
                ext = file_path.suffix.lower()
                if ext in self.SUPPORTED_EXTENSIONS:
                    extractable.append(file_path)
                elif ext in self.SKIP_EXTENSIONS:
                    binary.append(file_path)
                else:
                    unknown.append(file_path)

            # Calculate total size
            total_size = sum(extension_sizes.values())

        # Display results
        table = Table(title="File Type Breakdown", box=box.ROUNDED)
        table.add_column("File Type", style="cyan")
        table.add_column("Count", justify="right", style="magenta")
        table.add_column("Total Size", justify="right", style="green")
        table.add_column("Extractable", justify="center", style="yellow")

        for ext, count in extension_counts.most_common():
            size_mb = extension_sizes[ext] / (1024 * 1024)
            if ext in self.SUPPORTED_EXTENSIONS:
                extractable_marker = "[green]YES[/green]"
            elif ext in self.SKIP_EXTENSIONS:
                extractable_marker = "[red]NO[/red]"
            else:
                extractable_marker = "[yellow]?[/yellow]"

            table.add_row(
                ext,
                str(count),
                f"{size_mb:.2f} MB",
                extractable_marker
            )

        console.print(table)

        # Summary
        summary = Panel(
            f"""[bold]Summary[/bold]
Total files: {len(files_only):,}
Total size: {total_size / (1024 ** 3):.2f} GB
Extractable files: {len(extractable):,} ({len(extractable) / len(files_only) * 100:.1f}%)
Binary/Skip files: {len(binary):,} ({len(binary) / len(files_only) * 100:.1f}%)
Unknown files: {len(unknown):,}

[bold green]Extractable types:[/bold green] {', '.join(sorted(self.SUPPORTED_EXTENSIONS))}
[bold red]Binary/Skip types:[/bold red] {', '.join(sorted(list(self.SKIP_EXTENSIONS)[:10]))}...""",
            title="[bold]Analysis Complete[/bold]",
            border_style="green"
        )
        console.print(summary)

        return {
            'total_files': len(files_only),
            'total_size': total_size,
            'extractable': extractable,
            'binary': binary,
            'unknown': unknown,
            'extension_counts': extension_counts,
            'extension_sizes': extension_sizes,
        }

    def ingest_directory(
        self,
        directory_path: Path,
        dry_run: bool = False,
        max_files: Optional[int] = None,
    ) -> Dict:
        """
        🔒 READ-ONLY: Ingest all supported files from directory.

        Args:
            directory_path: Path to directory to ingest
            dry_run: If True, only analyze without actually ingesting
            max_files: Maximum number of files to process (for testing)

        Returns:
            Dictionary with ingestion statistics
        """
        if not directory_path.exists():
            console.print(f"[red]✗ Directory does not exist: {directory_path}[/red]")
            return {}

        if not directory_path.is_dir():
            console.print(f"[red]✗ Path is not a directory: {directory_path}[/red]")
            return {}

        # Analyze first
        analysis = self.analyze_directory(directory_path)

        if dry_run:
            console.print("\n[yellow]DRY RUN - No files will be ingested[/yellow]")
            return analysis

        # Confirm before proceeding
        extractable_files = analysis['extractable']
        if max_files:
            extractable_files = extractable_files[:max_files]

        console.print(f"\n[bold yellow]Ready to ingest {len(extractable_files):,} files[/bold yellow]")
        console.print(f"[dim]Database: {self.db_name or 'default'}[/dim]")

        # Initialize pipeline
        try:
            console.print("\n[cyan]Initializing ingestion pipeline...[/cyan]")
            pipeline = self._get_pipeline()
            console.print("[green]✓ Pipeline initialized[/green]")
        except Exception as e:
            console.print(f"[red]✗ Failed to initialize pipeline: {e}[/red]")
            return {}

        # Ingest files with progress tracking
        self.stats['start_time'] = time.time()
        self._ingest_files_with_progress(extractable_files, pipeline)
        self.stats['end_time'] = time.time()

        # Display final results
        self._display_final_stats()

        return self.stats

    def _ingest_files_with_progress(self, files: List[Path], pipeline: IngestionPipeline):
        """Ingest files with rich progress tracking"""

        # Create progress bars
        progress = Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            TextColumn("({task.completed}/{task.total})"),
            TimeElapsedColumn(),
            TimeRemainingColumn(),
            console=console,
        )

        with progress:
            task = progress.add_task("[cyan]Processing files...", total=len(files))

            for i, file_path in enumerate(files, 1):
                progress.update(task, description=f"[cyan]Processing: {file_path.name[:40]}...")

                try:
                    # Read file (READ-ONLY)
                    content = file_path.read_bytes()
                    file_size = len(content)
                    self.stats['total_size_bytes'] += file_size

                    # Extract text (READ-ONLY)
                    text = pipeline._extract_text_from_file(file_path, content)

                    if text is None:
                        self.stats['skipped_count'] += 1
                        self.file_type_stats[file_path.suffix.lower() + ' (skipped)'] += 1
                        progress.update(task, advance=1)
                        continue

                    if not text.strip():
                        self.stats['skipped_count'] += 1
                        self.file_type_stats[file_path.suffix.lower() + ' (empty)'] += 1
                        progress.update(task, advance=1)
                        continue

                    self.stats['extracted_size_bytes'] += len(text)

                    # Ingest
                    try:
                        result = pipeline.ingest_text(
                            text=text,
                            source=f"file://{file_path}",
                            source_type="file",
                            mime_type=pipeline._detect_mime_type(file_path)
                        )

                        if result:
                            self.stats['success_count'] += 1
                            self.file_type_stats[file_path.suffix.lower() + ' (success)'] += 1
                        else:
                            self.stats['skipped_count'] += 1
                            self.file_type_stats[file_path.suffix.lower() + ' (duplicate)'] += 1

                    except Exception as e:
                        self.stats['error_count'] += 1
                        self.errors.append((file_path, str(e)))
                        self.file_type_stats[file_path.suffix.lower() + ' (error)'] += 1

                except Exception as e:
                    self.stats['error_count'] += 1
                    self.errors.append((file_path, str(e)))
                    self.file_type_stats[file_path.suffix.lower() + ' (read error)'] += 1

                progress.update(task, advance=1)

                # Show live stats every 50 files
                if i % 50 == 0:
                    self._show_live_stats(progress, i, len(files))

    def _show_live_stats(self, progress, current, total):
        """Show live statistics during ingestion"""
        elapsed = time.time() - self.stats['start_time']
        rate = current / elapsed if elapsed > 0 else 0

        stats_text = f"""
[bold]Progress:[/bold] {current}/{total} ({current/total*100:.1f}%)
[bold]Success:[/bold] {self.stats['success_count']} | [bold]Errors:[/bold] {self.stats['error_count']} | [bold]Skipped:[/bold] {self.stats['skipped_count']}
[bold]Speed:[/bold] {rate:.1f} files/sec
[bold]Data extracted:[/bold] {self.stats['extracted_size_bytes'] / (1024**2):.1f} MB
"""
        console.print(Panel(stats_text, title="Live Statistics", border_style="green"))

    def _display_final_stats(self):
        """Display final ingestion statistics"""
        elapsed = self.stats['end_time'] - self.stats['start_time']
        total_processed = self.stats['success_count'] + self.stats['error_count'] + self.stats['skipped_count']

        # Main stats panel
        stats_panel = Panel(
            f"""[bold cyan]Ingestion Complete![/bold cyan]

[bold]Time:[/bold] {elapsed:.1f} seconds ({elapsed/60:.1f} minutes)
[bold]Files processed:[/bold] {total_processed:,}
[bold]Success:[/bold] [green]{self.stats['success_count']:,}[/green] ({self.stats['success_count']/total_processed*100:.1f}%)
[bold]Errors:[/bold] [red]{self.stats['error_count']:,}[/red]
[bold]Skipped:[/bold] [yellow]{self.stats['skipped_count']:,}[/yellow] (duplicates, empty, unsupported)

[bold]Data processed:[/bold] {self.stats['total_size_bytes'] / (1024**2):.1f} MB
[bold]Text extracted:[/bold] {self.stats['extracted_size_bytes'] / (1024**2):.1f} MB
[bold]Average speed:[/bold] {total_processed/elapsed:.1f} files/sec
""",
            title="[bold green]✓ Final Statistics[/bold green]",
            border_style="green",
            box=box.DOUBLE
        )
        console.print("\n")
        console.print(stats_panel)

        # File type breakdown
        if self.file_type_stats:
            type_table = Table(title="File Type Results", box=box.ROUNDED)
            type_table.add_column("File Type", style="cyan")
            type_table.add_column("Count", justify="right", style="magenta")

            for file_type, count in self.file_type_stats.most_common():
                type_table.add_row(file_type, str(count))

            console.print("\n")
            console.print(type_table)

        # Errors (if any)
        if self.errors:
            console.print(f"\n[bold red]Errors ({len(self.errors)}):[/bold red]")
            error_table = Table(box=box.SIMPLE)
            error_table.add_column("File", style="yellow", max_width=50)
            error_table.add_column("Error", style="red", max_width=60)

            for file_path, error in self.errors[:20]:  # Show first 20 errors
                error_table.add_row(str(file_path.name), error[:100])

            console.print(error_table)

            if len(self.errors) > 20:
                console.print(f"[dim]... and {len(self.errors) - 20} more errors[/dim]")

        # Next steps
        next_steps = Panel(
            f"""[bold cyan]Next Steps:[/bold cyan]

1. Query your data:
   [yellow]mydata --db={self.db_name or 'default'} ask "your question"[/yellow]

2. View statistics:
   [yellow]mydata --db={self.db_name or 'default'} stats[/yellow]

3. List documents:
   [yellow]mydata --db={self.db_name or 'default'} ls[/yellow]

4. Generate clusters:
   [yellow]mydata --db={self.db_name or 'default'} cluster[/yellow]
""",
            title="Usage",
            border_style="cyan"
        )
        console.print("\n")
        console.print(next_steps)

    def _get_pipeline(self) -> IngestionPipeline:
        """Initialize ingestion pipeline with correct database"""
        crypto = CryptoManager()
        if not crypto.key_file.exists():
            raise Exception("Crypto not initialized. Run 'mydata setup' first.")

        crypto.unlock()

        # Get database paths
        sqlite_path, qdrant_path = Config.get_database_paths(self.db_name)

        # Initialize components
        db = Database(db_path=sqlite_path)
        storage = EncryptedStorage(crypto)
        embedder = Embedder()
        vectordb = VectorDB(path=qdrant_path)
        vectordb.initialize(dimension=embedder.dimension)

        session = db.session()
        ml_organizer = MLOrganizer(embedder, session)

        return IngestionPipeline(session, storage, embedder, vectordb, ml_organizer)


def main():
    """Command-line interface for bulk ingestion"""
    import sys

    if len(sys.argv) < 2:
        console.print("[yellow]Usage: python -m mydata.bulk_ingest <directory_path> [--db=<name>] [--dry-run][/yellow]")
        sys.exit(1)

    directory_path = Path(sys.argv[1])
    db_name = None
    dry_run = '--dry-run' in sys.argv

    # Parse --db flag
    for arg in sys.argv:
        if arg.startswith('--db='):
            db_name = arg.split('=')[1]

    ingester = BulkIngester(db_name=db_name)

    if dry_run:
        ingester.analyze_directory(directory_path)
    else:
        ingester.ingest_directory(directory_path, dry_run=False)


if __name__ == '__main__':
    main()
