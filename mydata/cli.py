"""Command-line interface for MyData"""

import sys
import traceback
from pathlib import Path
from typing import Optional, List
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
from sqlmodel import select
from .models import Document, Tag, Cluster

logger = get_logger()

app = typer.Typer(
    help="Prometheus Light - God Mode: Encrypted Personal Knowledge Base",
    add_completion=False,
)
console = Console()


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
    )
):
    """Prometheus Light - God Mode"""
    pass


def get_crypto() -> CryptoManager:
    """Get initialized crypto manager"""
    crypto = CryptoManager()
    if not crypto.key_file.exists():
        console.print("[red]✗[/red] Not initialized. Run 'mydata setup' first.")
        raise typer.Exit(1)
    return crypto


def get_pipeline() -> IngestionPipeline:
    """Get initialized ingestion pipeline"""
    crypto = get_crypto()
    crypto.unlock()

    db = Database()
    storage = EncryptedStorage(crypto)
    embedder = Embedder()
    vectordb = VectorDB()
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

        # Initialize database
        logger.info("Initializing database...")
        db = Database()
        console.print("[green]✓[/green] Database created")
        logger.info("Database created")

        # Initialize vector DB
        logger.info("Initializing embedder and vector DB...")
        embedder = Embedder()
        logger.debug(f"Embedder model: {embedder.model_name}")

        vectordb = VectorDB()
        vectordb.initialize(dimension=embedder.dimension)
        console.print("[green]✓[/green] Vector database initialized")
        logger.info(f"Vector DB initialized with dimension {embedder.dimension}")

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

    db = Database()
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

    db = Database()
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

    db = Database()
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

    db = Database()
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

            # Pretty print JSON
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
            db = Database()
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


if __name__ == "__main__":
    app()
