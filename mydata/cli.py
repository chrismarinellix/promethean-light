"""Command-line interface for MyData"""

import sys
import traceback
from pathlib import Path
from typing import Optional, List, Tuple
import typer
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import print as rprint
from .crypto import CryptoManager
from .database import Database
from .storage import EncryptedStorage
from .embedder import Embedder
from .vectordb import VectorDB
from .ml_organizer import MLOrganizer
from .ingestion import IngestionPipeline
from .banner import print_banner
from .logger import get_logger
from .config import Config
from sqlmodel import select
from .models import Document, Tag, Cluster

logger = get_logger()

app = typer.Typer(
    help="Prometheus Light - God Mode: Encrypted Personal Knowledge Base",
    add_completion=False,
)
console = Console()

# Global state for database name (set by callback)
_current_database: Optional[str] = None


def version_callback(value: bool):
    """Show version and banner"""
    if value:
        print_banner()
        raise typer.Exit()


@app.callback()
def main(
    version: bool = typer.Option(
        None,
        "--version",
        "-v",
        callback=version_callback,
        is_eager=True,
        help="Show version and banner",
    ),
    db: Optional[str] = typer.Option(
        None,
        "--db",
        help="Database name (e.g., 'project_9002'). Use 'default' or omit for personal database.",
    )
):
    """Prometheus Light - God Mode"""
    global _current_database
    _current_database = db


def get_crypto() -> CryptoManager:
    """Get initialized crypto manager"""
    crypto = CryptoManager()
    if not crypto.key_file.exists():
        console.print("[red]✗[/red] Not initialized. Run 'mydata setup' first.")
        raise typer.Exit(1)
    return crypto


def get_database_paths() -> Tuple[Path, Path]:
    """Get database paths based on current database selection"""
    return Config.get_database_paths(_current_database)


def get_pipeline() -> IngestionPipeline:
    """Get initialized ingestion pipeline"""
    crypto = get_crypto()
    crypto.unlock()

    # Get database paths for current database
    sqlite_path, qdrant_path = get_database_paths()

    db = Database(db_path=sqlite_path)
    storage = EncryptedStorage(crypto)
    embedder = Embedder()
    vectordb = VectorDB(path=qdrant_path)
    vectordb.initialize(dimension=embedder.dimension)

    session = db.session()
    ml_organizer = MLOrganizer(embedder, session)

    return IngestionPipeline(session, storage, embedder, vectordb, ml_organizer)


@app.command()
def setup(passphrase: Optional[str] = typer.Option(None, help="Master passphrase")):
    """Initialize MyData with encryption"""
    logger.info("=== SETUP STARTED ===")

    try:
        crypto = CryptoManager()
        logger.debug(f"CryptoManager initialized. Data dir: {crypto.data_dir}")

        if crypto.key_file.exists():
            console.print(f"[yellow]⚠[/yellow] Already initialized at {crypto.data_dir}")
            logger.warning("Already initialized")
            if not typer.confirm("Re-initialize? This will destroy all data."):
                raise typer.Exit(0)

            # Delete old data
            import shutil
            logger.info("Deleting old data...")
            shutil.rmtree(crypto.data_dir)
            crypto = CryptoManager()

        logger.info("Setting up encryption...")
        crypto.setup(passphrase)
        console.print("[green]✓[/green] MyData initialized successfully")
        console.print(f"[dim]Data directory: {crypto.data_dir}[/dim]")
        logger.info("Encryption setup complete")

        # Get database paths
        sqlite_path, qdrant_path = get_database_paths()

        # Initialize database
        logger.info("Initializing database...")
        db = Database(db_path=sqlite_path)
        console.print("[green]✓[/green] Database created")
        logger.info("Database created")

        # Initialize vector DB
        logger.info("Initializing embedder and vector DB...")
        embedder = Embedder()
        logger.debug(f"Embedder model: {embedder.model_name}")

        vectordb = VectorDB(path=qdrant_path)
        vectordb.initialize(dimension=embedder.dimension)
        console.print("[green]✓[/green] Vector database initialized")
        logger.info(f"Vector DB initialized with dimension {embedder.dimension}")

        if _current_database:
            console.print(f"[cyan]ℹ[/cyan] Database: {_current_database}")

        logger.info("=== SETUP COMPLETE ===")

    except Exception as e:
        console.print(f"[red]✗[/red] Setup failed: {e}")
        logger.error(f"Setup failed: {e}")
        logger.error(traceback.format_exc())
        raise typer.Exit(1)


@app.command()
def add(
    files: Optional[List[str]] = typer.Argument(None, help="Files to ingest"),
    stdin: bool = typer.Option(False, "--stdin", help="Read from stdin"),
):
    """Add files or text (requires daemon to be running)"""
    from .client import Client

    client = Client()

    if not client.is_alive():
        console.print("[red]✗[/red] Daemon not running. Start it with: START.bat")
        raise typer.Exit(1)

    if stdin:
        # Read from stdin
        text = sys.stdin.read()
        if text.strip():
            try:
                result = client.add_text(text, source="stdin")
                console.print(f"[green]✓[/green] Added from stdin (ID: {result['id'][:8]}...)")
            except Exception as e:
                console.print(f"[red]✗[/red] Add failed: {e}")
                raise typer.Exit(1)
    elif files:
        console.print("[yellow]⚠[/yellow] File upload not yet supported via API. Drop files in Documents folder instead.")
    else:
        console.print("[yellow]⚠[/yellow] No input provided. Use --stdin or drop files in Documents folder.")


@app.command()
def ask(query: str, limit: int = typer.Option(10, help="Number of results")):
    """Search your data (requires daemon to be running)"""
    from .client import Client

    client = Client()

    if not client.is_alive():
        console.print("[red]✗[/red] Daemon not running. Start it with: START.bat")
        raise typer.Exit(1)

    try:
        results = client.search(query, limit=limit)

        if not results:
            console.print("[yellow]No results found[/yellow]")
            return

        # Display results
        table = Table(title=f"Search Results: '{query}'")
        table.add_column("Score", style="cyan", width=8)
        table.add_column("Source", style="magenta", width=30)
        table.add_column("Preview", style="white", width=60)

        for hit in results:
            score = f"{hit['score']:.3f}"
            source = hit.get("source", "unknown")
            text = hit.get("text", "")[:100]

            table.add_row(score, source, text)

        console.print(table)

    except Exception as e:
        console.print(f"[red]✗[/red] Search failed: {e}")
        raise typer.Exit(1)


@app.command()
def ls(
    tag: Optional[str] = typer.Option(None, help="Filter by tag"),
    limit: int = typer.Option(20, help="Number of documents to show"),
):
    """List documents"""
    crypto = get_crypto()
    crypto.unlock()

    sqlite_path, _ = get_database_paths()
    db = Database(db_path=sqlite_path)
    session = db.session()

    # Query documents
    stmt = select(Document).limit(limit)
    docs = session.exec(stmt).all()

    if not docs:
        console.print("[yellow]No documents found[/yellow]")
        return

    # Display table
    table = Table(title="Documents")
    table.add_column("ID", style="cyan", width=12)
    table.add_column("Source", style="magenta", width=30)
    table.add_column("Preview", style="white", width=50)
    table.add_column("Created", style="green", width=20)

    for doc in docs:
        doc_id = str(doc.id)[:8]
        source = doc.source[:28] + "..." if len(doc.source) > 30 else doc.source
        preview = doc.raw_text[:47] + "..." if len(doc.raw_text) > 50 else doc.raw_text
        created = doc.created_at.strftime("%Y-%m-%d %H:%M")

        table.add_row(doc_id, source, preview, created)

    console.print(table)


@app.command()
def stats():
    """Show database statistics (requires daemon to be running)"""
    from .client import Client

    client = Client()

    if not client.is_alive():
        console.print("[red]✗[/red] Daemon not running. Start it with: START.bat")
        raise typer.Exit(1)

    try:
        data = client.stats()

        stats_panel = Panel(
            f"""[cyan]Total Documents:[/cyan] {data['total_documents']}
[cyan]Total Chunks:[/cyan] {data['total_chunks']}
[cyan]Total Tags:[/cyan] {data['total_tags']}
[cyan]Total Clusters:[/cyan] {data['total_clusters']}""",
            title="Promethean Light Statistics",
            border_style="green",
        )

        console.print(stats_panel)

    except Exception as e:
        console.print(f"[red]✗[/red] Stats failed: {e}")
        raise typer.Exit(1)


@app.command()
def tags():
    """List all tags"""
    crypto = get_crypto()
    crypto.unlock()

    sqlite_path, _ = get_database_paths()
    db = Database(db_path=sqlite_path)
    session = db.session()

    all_tags = session.exec(select(Tag)).all()

    if not all_tags:
        console.print("[yellow]No tags found[/yellow]")
        return

    # Count tags
    from collections import Counter

    tag_counts = Counter([t.tag for t in all_tags])

    table = Table(title="Tags")
    table.add_column("Tag", style="cyan")
    table.add_column("Count", style="magenta", justify="right")

    for tag, count in tag_counts.most_common():
        table.add_row(tag, str(count))

    console.print(table)


@app.command()
def clusters():
    """Show document clusters"""
    crypto = get_crypto()
    crypto.unlock()

    sqlite_path, _ = get_database_paths()
    db = Database(db_path=sqlite_path)
    session = db.session()

    all_clusters = session.exec(select(Cluster)).all()

    if not all_clusters:
        console.print("[yellow]No clusters found. Run 'mydata daemon' to generate clusters.[/yellow]")
        return

    table = Table(title="Clusters")
    table.add_column("ID", style="cyan")
    table.add_column("Label", style="magenta")
    table.add_column("Docs", style="green", justify="right")

    for cluster in all_clusters:
        table.add_row(str(cluster.id), cluster.label, str(cluster.document_count))

    console.print(table)


@app.command()
def daemon():
    """Start background daemon (file watcher + email + ML)"""
    logger.info("=== DAEMON STARTING ===")

    try:
        from .daemon import Daemon
        from .settings import settings

        # Show banner
        print_banner(style="simple")

        logger.info("Unlocking crypto...")
        crypto = get_crypto()
        crypto.unlock()
        logger.info("Crypto unlocked")

        logger.info("Initializing daemon...")
        daemon = Daemon(crypto, settings)

        logger.info("Starting daemon services...")
        daemon.start()

    except Exception as e:
        console.print(f"[red]✗[/red] Daemon failed: {e}")
        logger.error(f"Daemon failed: {e}")
        logger.error(traceback.format_exc())
        raise typer.Exit(1)


@app.command()
def email_add(
    email_address: str = typer.Argument(..., help="Email address"),
    password: str = typer.Option(None, "--password", "-p", help="App password"),
    imap_server: str = typer.Option("imap.gmail.com", help="IMAP server"),
    imap_port: int = typer.Option(993, help="IMAP port"),
):
    """Add email account for ingestion"""
    crypto = get_crypto()
    crypto.unlock()

    sqlite_path, _ = get_database_paths()
    db = Database(db_path=sqlite_path)
    session = db.session()

    # Get password if not provided
    if password is None:
        import getpass

        password = getpass.getpass("Email password (or app password): ")

    # Encrypt password
    from .models import EmailCredential

    encrypted_password = crypto.encrypt_str(password)

    # Save credential
    cred = EmailCredential(
        email_address=email_address,
        encrypted_password=encrypted_password,
        imap_server=imap_server,
        imap_port=imap_port,
    )

    session.add(cred)
    session.commit()

    console.print(f"[green]✓[/green] Email account added: {email_address}")
    console.print("[dim]Run 'mydata daemon' to start watching inbox[/dim]")


@app.command()
def quick():
    """Quick access menu for common queries and summaries"""
    from .client import Client
    import requests
    import json

    client = Client()

    # Check if daemon is running
    if not client.is_alive():
        console.print("[red]✗[/red] Daemon not running. Start it with: START.bat")
        raise typer.Exit(1)

    # Define quick access items
    items = [
        {"key": "1", "name": "India Staff", "type": "summary", "query": "india_staff"},
        {"key": "2", "name": "Australia Staff", "type": "summary", "query": "australia_staff"},
        {"key": "3", "name": "Retention Bonuses", "type": "summary", "query": "retention_bonuses"},
        {"key": "4", "name": "Search: Salary Info", "type": "search", "query": "salary information"},
        {"key": "5", "name": "Search: Pipeline", "type": "search", "query": "pipeline"},
        {"key": "6", "name": "Search: Urgent Items", "type": "search", "query": "urgent"},
        {"key": "7", "name": "Recent Documents", "type": "list", "query": None},
    ]

    # Display menu
    console.print("\n[bold cyan]Quick Access Menu[/bold cyan]\n")

    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("#", style="cyan", width=4)
    table.add_column("Query", style="white", width=30)
    table.add_column("Type", style="green", width=12)

    for item in items:
        table.add_row(item["key"], item["name"], item["type"])

    console.print(table)
    console.print("\n[dim]Enter number (or 'q' to quit):[/dim] ", end="")

    choice = input().strip()

    if choice.lower() == 'q':
        return

    # Find selected item
    selected = next((item for item in items if item["key"] == choice), None)

    if not selected:
        console.print("[yellow]Invalid selection[/yellow]")
        return

    console.print(f"\n[cyan]Loading: {selected['name']}...[/cyan]\n")

    try:
        if selected["type"] == "summary":
            # Fetch pre-computed summary
            response = requests.get(f"http://localhost:8000/summary/{selected['query']}")
            response.raise_for_status()
            data = response.json()

            # Format based on summary type
            if "staff" in data and isinstance(data["staff"], list):
                # Staff summary - create beautiful table
                staff_table = Table(title=f"[bold cyan]{selected['name']}[/bold cyan]")
                staff_table.add_column("ID", style="dim", width=8)
                staff_table.add_column("Name", style="bold white", width=25)
                staff_table.add_column("Position", style="cyan", width=25)
                staff_table.add_column("Salary", style="green", width=12, justify="right")
                staff_table.add_column("Bonus", style="yellow", width=10, justify="right")
                staff_table.add_column("Total", style="bold green", width=12, justify="right")
                staff_table.add_column("Expires", style="magenta", width=10)

                for person in data["staff"]:
                    name = person.get("name", "")
                    # Color code resigned staff
                    if "RESIGNED" in person.get("position", ""):
                        name = f"[red]{name}[/red]"

                    staff_table.add_row(
                        person.get("id", "-"),
                        name,
                        person.get("position", "-"),
                        person.get("salary", person.get("ctc_aud", "-")),
                        person.get("retention_bonus", "-"),
                        person.get("total", person.get("total_with_bonus_aud", "-")),
                        person.get("expires", person.get("bonus_until", "-"))
                    )

                console.print(staff_table)

                # Show summary stats
                summary_text = f"\n[bold]Summary:[/bold] {data.get('summary', '')}"
                if "total_count" in data:
                    summary_text += f"\n[bold]Total Staff:[/bold] {data['total_count']}"
                if "with_retention_bonus" in data:
                    summary_text += f"\n[bold]With Retention Bonus:[/bold] {data['with_retention_bonus']}"
                if "notes" in data:
                    summary_text += f"\n[bold]Notes:[/bold] {data['notes']}"

                console.print(Panel(summary_text, border_style="green"))

            elif "expires_feb_2026" in data or "expires_aug_2026" in data:
                # Retention bonus summary
                bonus_table = Table(title=f"[bold cyan]{selected['name']}[/bold cyan]")
                bonus_table.add_column("Name", style="bold white", width=30)
                bonus_table.add_column("Bonus", style="yellow", width=10)
                bonus_table.add_column("Amount", style="green", width=15, justify="right")
                bonus_table.add_column("Expires", style="magenta", width=12)

                # Feb 2026 bonuses
                if "expires_feb_2026" in data:
                    for person in data["expires_feb_2026"]:
                        name = person.get("name", "")
                        if "RESIGNED" in name:
                            name = f"[red]{name}[/red]"
                        bonus_table.add_row(
                            name,
                            person.get("bonus", "-"),
                            person.get("amount_aud", "-"),
                            "Feb 2026"
                        )

                # Aug 2026 bonuses
                if "expires_aug_2026" in data:
                    for person in data["expires_aug_2026"]:
                        bonus_table.add_row(
                            person.get("name", ""),
                            person.get("bonus", "-"),
                            person.get("amount_aud", person.get("amount_myr", person.get("amount_inr", "-"))),
                            "Aug 2026"
                        )

                console.print(bonus_table)

                # Show total
                if "total_annual_cost_aud" in data:
                    console.print(f"\n[bold green]Total Annual Cost:[/bold green] {data['total_annual_cost_aud']}")
                if "total_staff_with_bonuses" in data:
                    console.print(f"[bold]Total Staff with Bonuses:[/bold] {data['total_staff_with_bonuses']}")

            else:
                # Fallback to formatted JSON for other summaries
                console.print(Panel(
                    json.dumps(data, indent=2),
                    title=f"[bold]{selected['name']}[/bold]",
                    border_style="green"
                ))

        elif selected["type"] == "search":
            # Execute search
            results = client.search(selected["query"], limit=10)

            if not results:
                console.print("[yellow]No results found[/yellow]")
                return

            # Display results table
            result_table = Table(title=f"Search Results: '{selected['query']}'")
            result_table.add_column("Score", style="cyan", width=8)
            result_table.add_column("Source", style="magenta", width=30)
            result_table.add_column("Preview", style="white", width=60)

            for hit in results:
                score = f"{hit['score']:.3f}"
                source = hit.get("source", "unknown")
                text = hit.get("text", "")[:100]
                result_table.add_row(score, source, text)

            console.print(result_table)

        elif selected["type"] == "list":
            # Show recent documents
            crypto = get_crypto()
            crypto.unlock()
            sqlite_path, _ = get_database_paths()
            db = Database(db_path=sqlite_path)
            session = db.session()

            stmt = select(Document).limit(15)
            docs = session.exec(stmt).all()

            if not docs:
                console.print("[yellow]No documents found[/yellow]")
                return

            doc_table = Table(title="Recent Documents")
            doc_table.add_column("ID", style="cyan", width=12)
            doc_table.add_column("Source", style="magenta", width=30)
            doc_table.add_column("Preview", style="white", width=50)
            doc_table.add_column("Created", style="green", width=20)

            for doc in docs:
                doc_id = str(doc.id)[:8]
                source = doc.source[:28] + "..." if len(doc.source) > 30 else doc.source
                preview = doc.raw_text[:47] + "..." if len(doc.raw_text) > 50 else doc.raw_text
                created = doc.created_at.strftime("%Y-%m-%d %H:%M")
                doc_table.add_row(doc_id, source, preview, created)

            console.print(doc_table)

    except Exception as e:
        console.print(f"[red]✗[/red] Error: {e}")
        raise typer.Exit(1)


@app.command()
def init(
    db_name: str = typer.Argument(..., help="Database name (e.g., 'project_9002')"),
    passphrase: Optional[str] = typer.Option(None, help="Master passphrase"),
):
    """Initialize a new project database"""
    logger.info(f"=== INITIALIZING DATABASE: {db_name} ===")

    try:
        # Validate database name
        if db_name in ["default", "models", "logs", "qdrant"]:
            console.print(f"[red]✗[/red] Invalid database name '{db_name}'. Reserved names: default, models, logs, qdrant")
            raise typer.Exit(1)

        # Ensure crypto is setup
        crypto = CryptoManager()
        if not crypto.key_file.exists():
            console.print("[yellow]⚠[/yellow] Crypto not initialized. Initializing now...")
            crypto.setup(passphrase)
            console.print("[green]✓[/green] Crypto initialized")

        crypto.unlock()

        # Get database paths
        sqlite_path, qdrant_path = Config.get_database_paths(db_name)

        # Check if already exists
        if sqlite_path.exists() or qdrant_path.exists():
            console.print(f"[yellow]⚠[/yellow] Database '{db_name}' already exists")
            if not typer.confirm("Re-initialize? This will destroy all data in this database."):
                raise typer.Exit(0)

            # Delete old database
            import shutil
            if sqlite_path.exists():
                sqlite_path.unlink()
            if qdrant_path.exists():
                shutil.rmtree(qdrant_path)

        # Create directories
        Config.ensure_database_directories(db_name)

        # Initialize database
        logger.info(f"Creating SQLite database at {sqlite_path}...")
        db = Database(db_path=sqlite_path)
        console.print(f"[green]✓[/green] Database created: {sqlite_path}")

        # Initialize vector DB
        logger.info(f"Creating Qdrant vector store at {qdrant_path}...")
        embedder = Embedder()
        vectordb = VectorDB(path=qdrant_path)
        vectordb.initialize(dimension=embedder.dimension)
        console.print(f"[green]✓[/green] Vector database initialized: {qdrant_path}")

        console.print(f"\n[bold green]✓ Database '{db_name}' initialized successfully![/bold green]")
        console.print(f"\n[cyan]Usage examples:[/cyan]")
        console.print(f"  mydata --db={db_name} ask \"your query\"")
        console.print(f"  mydata --db={db_name} ls")
        console.print(f"  mydata --db={db_name} stats")

        logger.info(f"=== DATABASE {db_name} INITIALIZED ===")

    except Exception as e:
        console.print(f"[red]✗[/red] Initialization failed: {e}")
        logger.error(f"Init failed: {e}")
        logger.error(traceback.format_exc())
        raise typer.Exit(1)


@app.command("list-dbs")
def list_databases():
    """List all available databases"""
    try:
        databases = Config.list_databases()

        if not databases:
            console.print("[yellow]No databases found. Run 'mydata setup' to create the default database.[/yellow]")
            return

        table = Table(title="Available Databases")
        table.add_column("Name", style="cyan")
        table.add_column("SQLite Path", style="white")
        table.add_column("Status", style="green")

        for db_name in databases:
            sqlite_path, qdrant_path = Config.get_database_paths(db_name if db_name != "default" else None)

            # Check if database exists
            status = ""
            if sqlite_path.exists():
                status += "✓ SQLite "
            if qdrant_path.exists():
                status += "✓ Qdrant"

            if not status:
                status = "[dim]Not initialized[/dim]"

            table.add_row(
                db_name,
                str(sqlite_path),
                status
            )

        console.print(table)
        console.print(f"\n[dim]Use --db=<name> to switch databases[/dim]")
        console.print(f"[dim]Example: mydata --db=project_9002 ask \"your query\"[/dim]")

    except Exception as e:
        console.print(f"[red]✗[/red] Failed to list databases: {e}")
        raise typer.Exit(1)


@app.command()
def ingest(
    path: str = typer.Argument(..., help="Directory or file path to ingest"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Analyze only, don't ingest"),
    max_files: Optional[int] = typer.Option(None, "--max-files", help="Maximum files to process (for testing)"),
):
    """
    Bulk ingest files from a directory with comprehensive progress tracking.

    Supports: TXT, MD, CSV, JSON, LOG, PDF, DOCX, XLSX
    🔒 READ-ONLY: Files are never modified, only read.
    """
    from pathlib import Path
    from .bulk_ingest import BulkIngester

    try:
        source_path = Path(path)

        if not source_path.exists():
            console.print(f"[red]✗[/red] Path does not exist: {path}")
            raise typer.Exit(1)

        if _current_database:
            console.print(f"[bold cyan]Database:[/bold cyan] {_current_database}\n")

        # Use bulk ingester
        ingester = BulkIngester(db_name=_current_database)

        if source_path.is_file():
            console.print("[yellow]⚠[/yellow] Single file ingestion - use bulk ingestion for directories")
            pipeline = get_pipeline()
            result = pipeline.ingest_file(source_path)
            if result:
                console.print(f"[green]✓[/green] File ingested successfully")
            else:
                console.print(f"[red]✗[/red] Failed to ingest file")
        elif source_path.is_dir():
            ingester.ingest_directory(source_path, dry_run=dry_run, max_files=max_files)
        else:
            console.print(f"[red]✗[/red] Invalid path type")
            raise typer.Exit(1)

    except Exception as e:
        console.print(f"[red]✗[/red] Ingestion failed: {e}")
        logger.error(f"Ingestion failed: {e}")
        logger.error(traceback.format_exc())
        raise typer.Exit(1)


@app.command("api-key")
def api_key_add(
    service: str = typer.Argument(..., help="Service name (e.g., 'openai')"),
    api_key: str = typer.Argument(..., help="API key to store"),
):
    """Add or update an encrypted API key (available across all databases)"""
    from .client import Client

    client = Client()

    if not client.is_alive():
        console.print("[red]✗[/red] Daemon not running. Start it with: START.bat")
        raise typer.Exit(1)

    try:
        import requests
        response = requests.post(
            f"http://localhost:8000/api-keys",
            json={"service": service, "api_key": api_key}
        )
        response.raise_for_status()
        result = response.json()

        console.print(f"[green]✓[/green] {result['message']}")
        console.print(f"[dim]API key encrypted and stored securely[/dim]")

    except Exception as e:
        console.print(f"[red]✗[/red] Failed to add API key: {e}")
        raise typer.Exit(1)


@app.command("api-keys")
def api_keys_list():
    """List configured API keys"""
    from .client import Client

    client = Client()

    if not client.is_alive():
        console.print("[red]✗[/red] Daemon not running. Start it with: START.bat")
        raise typer.Exit(1)

    try:
        import requests
        response = requests.get("http://localhost:8000/api-keys")
        response.raise_for_status()
        keys = response.json()

        if not keys:
            console.print("[yellow]No API keys configured[/yellow]")
            return

        table = Table(title="Configured API Keys")
        table.add_column("Service", style="cyan")
        table.add_column("Enabled", style="green")
        table.add_column("Updated", style="dim")

        for key in keys:
            table.add_row(
                key["service"],
                "✓" if key["enabled"] else "✗",
                key["updated_at"][:10]
            )

        console.print(table)

    except Exception as e:
        console.print(f"[red]✗[/red] Failed to list API keys: {e}")
        raise typer.Exit(1)


@app.command()
def chat(
    message: Optional[str] = typer.Argument(None, help="Chat message"),
    conversation_id: Optional[int] = typer.Option(None, "--conversation", "-c", help="Continue conversation"),
    model: str = typer.Option("gpt-4o-mini", "--model", "-m", help="OpenAI model"),
    interactive: bool = typer.Option(False, "--interactive", "-i", help="Interactive chat mode"),
):
    """Chat with your data using RAG (Retrieval-Augmented Generation)"""
    from .client import Client
    import requests

    client = Client()

    if not client.is_alive():
        console.print("[red]✗[/red] Daemon not running. Start it with: START.bat")
        raise typer.Exit(1)

    if interactive:
        # Interactive mode
        console.print("[bold cyan]Interactive Chat Mode[/bold cyan]")
        console.print("[dim]Type 'exit' or 'quit' to end conversation[/dim]\n")

        current_conversation_id = conversation_id

        while True:
            # Get user input
            try:
                user_input = console.input("[bold green]You:[/bold green] ")
            except (KeyboardInterrupt, EOFError):
                console.print("\n[dim]Goodbye![/dim]")
                break

            if user_input.strip().lower() in ["exit", "quit", "q"]:
                console.print("[dim]Goodbye![/dim]")
                break

            if not user_input.strip():
                continue

            # Send to chatbot
            try:
                response = requests.post(
                    "http://localhost:8000/chat",
                    json={
                        "message": user_input,
                        "conversation_id": current_conversation_id,
                        "model": model,
                    }
                )
                response.raise_for_status()
                result = response.json()

                # Update conversation ID
                current_conversation_id = result["conversation_id"]

                # Display response
                console.print(f"\n[bold cyan]Assistant:[/bold cyan] {result['response']}\n")
                console.print(f"[dim]Sources: {result['chunks_retrieved']} chunks | Tokens: {result['tokens_used']}[/dim]\n")

            except Exception as e:
                console.print(f"[red]✗[/red] Error: {e}\n")

    else:
        # Single message mode
        if not message:
            console.print("[red]✗[/red] Message required (or use --interactive for chat mode)")
            raise typer.Exit(1)

        try:
            response = requests.post(
                "http://localhost:8000/chat",
                json={
                    "message": message,
                    "conversation_id": conversation_id,
                    "model": model,
                }
            )
            response.raise_for_status()
            result = response.json()

            # Display response
            console.print(f"\n[bold cyan]Response:[/bold cyan]")
            console.print(result['response'])
            console.print(f"\n[dim]Conversation ID: {result['conversation_id']}[/dim]")
            console.print(f"[dim]Sources: {result['chunks_retrieved']} chunks | Tokens: {result['tokens_used']}[/dim]")

            # Show sources if available
            if result.get('sources'):
                console.print(f"\n[bold]Sources used:[/bold]")
                for i, source in enumerate(result['sources'][:3], 1):
                    text = source.get('payload', {}).get('text', '')[:100]
                    console.print(f"{i}. {text}...")

        except Exception as e:
            console.print(f"[red]✗[/red] Chat failed: {e}")
            raise typer.Exit(1)


@app.command("conversations")
def list_conversations(limit: int = typer.Option(20, help="Number of conversations to show")):
    """List recent chat conversations"""
    from .client import Client
    import requests

    client = Client()

    if not client.is_alive():
        console.print("[red]✗[/red] Daemon not running. Start it with: START.bat")
        raise typer.Exit(1)

    try:
        response = requests.get(f"http://localhost:8000/chat/conversations?limit={limit}")
        response.raise_for_status()
        conversations = response.json()

        if not conversations:
            console.print("[yellow]No conversations found[/yellow]")
            return

        table = Table(title="Chat Conversations")
        table.add_column("ID", style="cyan", width=6)
        table.add_column("Title", style="white", width=50)
        table.add_column("Updated", style="green", width=20)

        for conv in conversations:
            table.add_row(
                str(conv["id"]),
                conv["title"],
                conv["updated_at"][:19].replace("T", " ")
            )

        console.print(table)
        console.print(f"\n[dim]Use: mydata chat --conversation <ID> \"your message\" to continue[/dim]")

    except Exception as e:
        console.print(f"[red]✗[/red] Failed: {e}")
        raise typer.Exit(1)


if __name__ == "__main__":
    app()
