#!/usr/bin/env python3
"""
Promethean Light Daemon Status Checker
Comprehensive health check for daemon, database, ML, and vector DB.
"""

import os
import sys
import json
import sqlite3
import requests
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, Any
import traceback

# Configuration
API_BASE = "http://127.0.0.1:8000"
MYDATA_HOME = Path.home() / ".mydata"
DATABASE_PATH = MYDATA_HOME / "mydata.db"
QDRANT_PATH = MYDATA_HOME / "qdrant"
LOGS_PATH = MYDATA_HOME / "logs"

# ANSI colors for terminal output
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    DIM = '\033[2m'
    RESET = '\033[0m'

def c(text: str, color: str) -> str:
    """Colorize text."""
    return f"{color}{text}{Colors.RESET}"

def format_bytes(size_bytes: int) -> str:
    """Format bytes to human readable."""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.2f} TB"

def format_timedelta(td: timedelta) -> str:
    """Format timedelta to human readable."""
    total_seconds = int(td.total_seconds())
    days = total_seconds // 86400
    hours = (total_seconds % 86400) // 3600
    minutes = (total_seconds % 3600) // 60
    seconds = total_seconds % 60

    parts = []
    if days > 0:
        parts.append(f"{days}d")
    if hours > 0:
        parts.append(f"{hours}h")
    if minutes > 0:
        parts.append(f"{minutes}m")
    if seconds > 0 or not parts:
        parts.append(f"{seconds}s")
    return " ".join(parts)

def time_ago(timestamp_str: str) -> str:
    """Convert timestamp to 'X ago' format."""
    if not timestamp_str:
        return "Never"
    try:
        # Handle various timestamp formats
        for fmt in ["%Y-%m-%dT%H:%M:%S.%f", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%d %H:%M:%S.%f", "%Y-%m-%d %H:%M:%S"]:
            try:
                dt = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
                break
            except:
                try:
                    dt = datetime.strptime(timestamp_str, fmt)
                    break
                except:
                    continue
        else:
            return timestamp_str

        delta = datetime.now() - dt.replace(tzinfo=None)
        return f"{format_timedelta(delta)} ago"
    except Exception as e:
        return timestamp_str

def get_folder_size(path: Path) -> int:
    """Get total size of folder in bytes."""
    total = 0
    if path.exists():
        for file in path.rglob('*'):
            if file.is_file():
                total += file.stat().st_size
    return total

def check_api_health() -> dict:
    """Check if API is responding."""
    try:
        resp = requests.get(f"{API_BASE}/", timeout=5)
        return {"online": True, "status_code": resp.status_code, "data": resp.json()}
    except requests.exceptions.ConnectionError:
        return {"online": False, "error": "Connection refused - daemon not running"}
    except Exception as e:
        return {"online": False, "error": str(e)}

def get_dashboard_stats() -> Optional[dict]:
    """Get comprehensive dashboard stats."""
    try:
        resp = requests.get(f"{API_BASE}/dashboard/stats", timeout=10)
        return resp.json() if resp.status_code == 200 else None
    except:
        return None

def get_admin_info() -> Optional[dict]:
    """Get admin panel info."""
    try:
        resp = requests.get(f"{API_BASE}/admin/info", timeout=10)
        return resp.json() if resp.status_code == 200 else None
    except:
        return None

def get_vector_status() -> Optional[dict]:
    """Get vector DB rebuild/sync status."""
    try:
        resp = requests.get(f"{API_BASE}/admin/rebuild-vectors/status", timeout=10)
        return resp.json() if resp.status_code == 200 else None
    except:
        return None

def get_email_status() -> Optional[dict]:
    """Get email watcher status."""
    try:
        resp = requests.get(f"{API_BASE}/email/status", timeout=10)
        return resp.json() if resp.status_code == 200 else None
    except:
        return None

def get_database_stats_direct() -> dict:
    """Query database directly for detailed stats."""
    stats = {
        "connected": False,
        "total_documents": 0,
        "total_chunks": 0,
        "total_tags": 0,
        "total_clusters": 0,
        "docs_last_24h": 0,
        "docs_last_7d": 0,
        "docs_by_source": {},
        "recent_ingestions": [],
        "oldest_doc": None,
        "newest_doc": None,
        "avg_chunks_per_doc": 0,
        "email_credentials": 0,
        "conversations": 0,
        "saved_searches": 0,
    }

    if not DATABASE_PATH.exists():
        stats["error"] = f"Database not found at {DATABASE_PATH}"
        return stats

    try:
        conn = sqlite3.connect(str(DATABASE_PATH))
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        stats["connected"] = True

        # Total counts
        cursor.execute("SELECT COUNT(*) FROM documents")
        stats["total_documents"] = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM chunks")
        stats["total_chunks"] = cursor.fetchone()[0]

        try:
            cursor.execute("SELECT COUNT(*) FROM tags")
            stats["total_tags"] = cursor.fetchone()[0]
        except:
            pass

        try:
            cursor.execute("SELECT COUNT(*) FROM clusters")
            stats["total_clusters"] = cursor.fetchone()[0]
        except:
            pass

        # Calculate average chunks per doc
        if stats["total_documents"] > 0:
            stats["avg_chunks_per_doc"] = round(stats["total_chunks"] / stats["total_documents"], 1)

        # Documents in last 24 hours
        yesterday = (datetime.now() - timedelta(hours=24)).isoformat()
        cursor.execute("SELECT COUNT(*) FROM documents WHERE created_at > ?", (yesterday,))
        stats["docs_last_24h"] = cursor.fetchone()[0]

        # Documents in last 7 days
        week_ago = (datetime.now() - timedelta(days=7)).isoformat()
        cursor.execute("SELECT COUNT(*) FROM documents WHERE created_at > ?", (week_ago,))
        stats["docs_last_7d"] = cursor.fetchone()[0]

        # Documents by source type (classify based on source field)
        cursor.execute("SELECT source FROM documents")
        sources = {"emails": 0, "files": 0, "notes": 0, "other": 0}
        for row in cursor.fetchall():
            src = (row[0] or "").lower()
            if any(x in src for x in ["email:", "@", "outlook", "/o=", "imap"]):
                sources["emails"] += 1
            elif any(x in src for x in ["api", "paste", "note", "text", "saved-chat", "saved-response", "stdin"]):
                sources["notes"] += 1
            elif src.startswith("file://") or "/" in src or "\\" in src:
                sources["files"] += 1
            else:
                sources["other"] += 1
        stats["docs_by_source"] = sources

        # Recent ingestions (last 24h) with details
        cursor.execute("""
            SELECT source, source_type, mime_type, created_at, file_size_bytes
            FROM documents
            WHERE created_at > ?
            ORDER BY created_at DESC
            LIMIT 50
        """, (yesterday,))
        for row in cursor.fetchall():
            stats["recent_ingestions"].append({
                "source": row[0][:80] + "..." if len(row[0] or "") > 80 else row[0],
                "type": row[1],
                "mime": row[2],
                "when": row[3],
                "size": row[4]
            })

        # Oldest and newest documents
        cursor.execute("SELECT MIN(created_at), MAX(created_at) FROM documents")
        row = cursor.fetchone()
        stats["oldest_doc"] = row[0]
        stats["newest_doc"] = row[1]

        # Email credentials count
        try:
            cursor.execute("SELECT COUNT(*) FROM email_credentials WHERE enabled = 1")
            stats["email_credentials"] = cursor.fetchone()[0]
        except:
            pass

        # Chat conversations
        try:
            cursor.execute("SELECT COUNT(*) FROM chat_conversations")
            stats["conversations"] = cursor.fetchone()[0]
        except:
            pass

        # Saved searches
        try:
            cursor.execute("SELECT COUNT(*) FROM saved_searches")
            stats["saved_searches"] = cursor.fetchone()[0]
        except:
            pass

        # Hourly ingestion breakdown for last 24 hours
        hourly = []
        for i in range(24, 0, -1):
            start = (datetime.now() - timedelta(hours=i)).isoformat()
            end = (datetime.now() - timedelta(hours=i-1)).isoformat()
            cursor.execute("SELECT COUNT(*) FROM documents WHERE created_at > ? AND created_at <= ?", (start, end))
            count = cursor.fetchone()[0]
            if count > 0:
                hourly.append({"hour": f"-{i}h", "count": count})
        stats["hourly_ingestion"] = hourly

        # Tag distribution by confidence
        try:
            cursor.execute("""
                SELECT
                    SUM(CASE WHEN confidence >= 0.9 THEN 1 ELSE 0 END) as high,
                    SUM(CASE WHEN confidence >= 0.7 AND confidence < 0.9 THEN 1 ELSE 0 END) as medium,
                    SUM(CASE WHEN confidence < 0.7 THEN 1 ELSE 0 END) as low
                FROM tags
            """)
            row = cursor.fetchone()
            stats["tag_confidence"] = {
                "high": row[0] or 0,
                "medium": row[1] or 0,
                "low": row[2] or 0
            }
        except:
            stats["tag_confidence"] = {"high": 0, "medium": 0, "low": 0}

        # Cluster distribution
        try:
            cursor.execute("SELECT label, document_count FROM clusters ORDER BY document_count DESC LIMIT 10")
            stats["top_clusters"] = [{"label": row[0], "count": row[1]} for row in cursor.fetchall()]
        except:
            stats["top_clusters"] = []

        # Documents not in any cluster (noise)
        try:
            cursor.execute("SELECT COUNT(*) FROM documents WHERE cluster_id IS NULL OR cluster_id = -1")
            stats["unclustered_docs"] = cursor.fetchone()[0]
        except:
            stats["unclustered_docs"] = 0

        conn.close()

    except Exception as e:
        stats["error"] = str(e)
        stats["traceback"] = traceback.format_exc()

    return stats

def get_storage_stats() -> dict:
    """Get storage/disk stats."""
    stats = {
        "mydata_home": str(MYDATA_HOME),
        "database_size": 0,
        "qdrant_size": 0,
        "logs_size": 0,
        "total_size": 0,
    }

    if DATABASE_PATH.exists():
        stats["database_size"] = DATABASE_PATH.stat().st_size

    stats["qdrant_size"] = get_folder_size(QDRANT_PATH)
    stats["logs_size"] = get_folder_size(LOGS_PATH)
    stats["total_size"] = stats["database_size"] + stats["qdrant_size"] + stats["logs_size"]

    return stats

def check_log_for_errors() -> dict:
    """Check recent logs for errors."""
    log_info = {
        "recent_errors": [],
        "last_heartbeat": None,
        "ml_iterations": 0,
    }

    log_file = LOGS_PATH / "daemon.log"
    if not log_file.exists():
        return log_info

    try:
        with open(log_file, 'r', encoding='utf-8', errors='ignore') as f:
            # Read last 500 lines
            lines = f.readlines()[-500:]

        for line in lines:
            if "[ERROR]" in line or "ERROR:" in line or "Traceback" in line:
                log_info["recent_errors"].append(line.strip()[:150])
            if "[HEARTBEAT]" in line or "heartbeat" in line.lower():
                log_info["last_heartbeat"] = line.strip()[:100]
            if "ML loop iteration" in line or "clustering" in line.lower():
                log_info["ml_iterations"] += 1

        # Keep only last 10 errors
        log_info["recent_errors"] = log_info["recent_errors"][-10:]

    except Exception as e:
        log_info["error"] = str(e)

    return log_info

def print_section(title: str):
    """Print a section header."""
    print(f"\n{c('=' * 60, Colors.DIM)}")
    print(c(f"  {title}", Colors.BOLD + Colors.CYAN))
    print(c('=' * 60, Colors.DIM))

def print_item(label: str, value: Any, color: str = Colors.RESET, indent: int = 2):
    """Print a labeled item."""
    spaces = " " * indent
    print(f"{spaces}{c(label + ':', Colors.DIM)} {c(str(value), color)}")

def print_status(label: str, ok: bool, details: str = ""):
    """Print a status line with OK/FAIL indicator."""
    status = c("[OK]", Colors.GREEN) if ok else c("[FAIL]", Colors.RED)
    detail_str = f" - {details}" if details else ""
    print(f"  {status} {label}{detail_str}")

def print_warning(message: str):
    """Print a warning message."""
    print(f"  {c('[WARN]', Colors.YELLOW)} {message}")

def main():
    """Run comprehensive daemon status check."""
    print(c("\n" + "=" * 60, Colors.BOLD + Colors.BLUE))
    print(c("   PROMETHEAN LIGHT - DAEMON STATUS CHECK", Colors.BOLD + Colors.BLUE))
    print(c("   " + datetime.now().strftime("%Y-%m-%d %H:%M:%S"), Colors.DIM))
    print(c("=" * 60, Colors.BOLD + Colors.BLUE))

    warnings = []
    critical = []

    # ========== API/DAEMON STATUS ==========
    print_section("DAEMON STATUS")

    api_health = check_api_health()
    if api_health["online"]:
        print_status("API Server", True, f"Responding on {API_BASE}")
        crypto_status = api_health.get("data", {}).get("crypto_ready", False)
        print_status("Crypto Unlocked", crypto_status, "Encryption/decryption ready" if crypto_status else "Locked - some features unavailable")
        if not crypto_status:
            warnings.append("Crypto not unlocked - API key decryption unavailable")
    else:
        print_status("API Server", False, api_health.get("error", "Unknown error"))
        critical.append("Daemon API is not responding - daemon may not be running")

    # Get more detailed status from dashboard
    dashboard = get_dashboard_stats()
    if dashboard:
        daemon_status = dashboard.get("daemon_status", "unknown")
        print_status("Daemon Process", daemon_status == "running", f"Status: {daemon_status}")

    # ========== DATABASE STATUS ==========
    print_section("DATABASE STATUS")

    db_stats = get_database_stats_direct()
    storage = get_storage_stats()

    print_status("Database Connected", db_stats["connected"], str(DATABASE_PATH))
    if db_stats["connected"]:
        print_item("Database Size", format_bytes(storage["database_size"]), Colors.CYAN)
        print_item("Total Documents", f"{db_stats['total_documents']:,}", Colors.GREEN)
        print_item("Total Chunks", f"{db_stats['total_chunks']:,}", Colors.GREEN)
        print_item("Avg Chunks/Doc", db_stats["avg_chunks_per_doc"])
        print_item("Total Tags", f"{db_stats['total_tags']:,}")
        print_item("Total Clusters", db_stats["total_clusters"])
        print_item("Chat Conversations", db_stats["conversations"])
        print_item("Saved Searches", db_stats["saved_searches"])

        if db_stats["newest_doc"]:
            print_item("Latest Ingestion", time_ago(db_stats["newest_doc"]), Colors.YELLOW)
        if db_stats["oldest_doc"]:
            print_item("Oldest Document", time_ago(db_stats["oldest_doc"]))
    else:
        critical.append(f"Database not accessible: {db_stats.get('error', 'Unknown')}")

    # ========== INGESTION ACTIVITY (Last 24h) ==========
    print_section("INGESTION ACTIVITY (Last 24 Hours)")

    if db_stats["connected"]:
        docs_24h = db_stats["docs_last_24h"]
        docs_7d = db_stats["docs_last_7d"]

        status_24h = docs_24h > 0
        print_status("Documents Ingested (24h)", status_24h, f"{docs_24h:,} documents")
        print_item("Documents (7 days)", f"{docs_7d:,}")

        # Source breakdown
        print(f"\n  {c('By Source Type:', Colors.DIM)}")
        for src, count in db_stats["docs_by_source"].items():
            if count > 0:
                pct = round(count / db_stats["total_documents"] * 100, 1) if db_stats["total_documents"] > 0 else 0
                print_item(f"  {src.capitalize()}", f"{count:,} ({pct}%)", Colors.CYAN, indent=2)

        # Hourly breakdown
        if db_stats.get("hourly_ingestion"):
            print(f"\n  {c('Hourly Activity:', Colors.DIM)}")
            for h in db_stats["hourly_ingestion"][-12:]:  # Last 12 hours with activity
                bar = "#" * min(h["count"], 30)
                print(f"    {h['hour']:>4}: {c(bar, Colors.GREEN)} {h['count']}")

        # Recent ingestions detail
        if db_stats["recent_ingestions"]:
            print(f"\n  {c('Recent Documents (newest first):', Colors.DIM)}")
            for i, doc in enumerate(db_stats["recent_ingestions"][:15]):
                src_short = doc["source"]
                if len(src_short) > 50:
                    src_short = "..." + src_short[-47:]
                time_str = time_ago(doc["when"])
                size_str = format_bytes(doc["size"]) if doc["size"] else "?"
                print(f"    {c(time_str, Colors.YELLOW):>15} | {doc['type'] or '?':>6} | {size_str:>10} | {src_short}")

        if docs_24h == 0:
            warnings.append("No documents ingested in the last 24 hours")

    # ========== ML/CLUSTERING STATUS ==========
    print_section("ML ORGANIZATION STATUS")

    if db_stats["connected"]:
        cluster_count = db_stats["total_clusters"]
        unclustered = db_stats["unclustered_docs"]
        total_docs = db_stats["total_documents"]

        print_status("Clustering", cluster_count > 0, f"{cluster_count} clusters found")

        if total_docs > 0:
            clustered_pct = round((total_docs - unclustered) / total_docs * 100, 1)
            print_item("Clustered Documents", f"{total_docs - unclustered:,} ({clustered_pct}%)", Colors.GREEN)
            print_item("Unclustered (noise)", f"{unclustered:,} ({100 - clustered_pct}%)", Colors.YELLOW if unclustered > total_docs * 0.5 else Colors.RESET)

        # Tag confidence breakdown
        tc = db_stats.get("tag_confidence", {})
        if tc.get("high", 0) + tc.get("medium", 0) + tc.get("low", 0) > 0:
            print(f"\n  {c('Tag Confidence Distribution:', Colors.DIM)}")
            print_item("  High (>=90%)", tc.get("high", 0), Colors.GREEN, indent=2)
            print_item("  Medium (70-90%)", tc.get("medium", 0), Colors.YELLOW, indent=2)
            print_item("  Low (<70%)", tc.get("low", 0), Colors.RED, indent=2)

        # Top clusters
        if db_stats.get("top_clusters"):
            print(f"\n  {c('Top Clusters:', Colors.DIM)}")
            for cl in db_stats["top_clusters"][:5]:
                label = cl["label"][:40] if cl["label"] else "Unnamed"
                print(f"    {c(str(cl['count']), Colors.CYAN):>5} docs | {label}")

        if cluster_count == 0 and total_docs >= 5:
            warnings.append("No clusters created yet - ML organizer may not have run")

    # ========== VECTOR DATABASE STATUS ==========
    print_section("VECTOR DATABASE STATUS")

    print_item("Qdrant Path", str(QDRANT_PATH))
    print_item("Storage Size", format_bytes(storage["qdrant_size"]), Colors.CYAN)

    vector_status = get_vector_status()
    if vector_status:
        total_chunks = db_stats.get("total_chunks", 0)
        vector_count = vector_status.get("vector_count", 0)
        sync_pct = vector_status.get("sync_percentage", 0)
        in_sync = vector_status.get("in_sync", False)
        rebuild_status = vector_status.get("status", "unknown")

        print_status("Vector DB Sync", in_sync, f"{sync_pct:.1f}% ({vector_count:,} / {total_chunks:,} vectors)")
        print_item("Rebuild Status", rebuild_status, Colors.GREEN if rebuild_status == "idle" else Colors.YELLOW)

        if not in_sync:
            warnings.append(f"Vector DB out of sync ({sync_pct:.1f}%) - consider rebuilding")
    else:
        print_status("Vector DB Status", False, "Could not retrieve status")

    # ========== EMAIL WATCHER STATUS ==========
    print_section("EMAIL WATCHER STATUS")

    email_status = get_email_status()
    if email_status:
        email_count = email_status.get("email_count", 0)
        last_email = email_status.get("last_email_at")
        watchers = email_status.get("watcher_info", [])

        print_item("Total Emails Indexed", f"{email_count:,}", Colors.GREEN)
        print_item("Last Email Received", time_ago(last_email) if last_email else "Never", Colors.YELLOW)
        print_item("Configured Watchers", len(watchers))

        if watchers:
            print(f"\n  {c('Watcher Details:', Colors.DIM)}")
            for w in watchers:
                running = w.get("running", False)
                wtype = w.get("type", "Unknown")
                tracked = w.get("emails_tracked", 0)
                last_proc = w.get("last_processed")

                status_icon = c("[ON]", Colors.GREEN) if running else c("[OFF]", Colors.RED)
                print(f"    {status_icon} {wtype}: {tracked:,} tracked, last: {time_ago(last_proc) if last_proc else 'Never'}")

        active_watchers = sum(1 for w in watchers if w.get("running"))
        if active_watchers == 0 and db_stats.get("email_credentials", 0) > 0:
            warnings.append("No email watchers running but credentials are configured")
    else:
        print_status("Email Status", False, "Could not retrieve status")

    # ========== STORAGE SUMMARY ==========
    print_section("STORAGE SUMMARY")

    print_item("MyData Home", str(MYDATA_HOME))
    print_item("Database", format_bytes(storage["database_size"]), Colors.CYAN)
    print_item("Vector DB", format_bytes(storage["qdrant_size"]), Colors.CYAN)
    print_item("Logs", format_bytes(storage["logs_size"]))
    print_item("Total", format_bytes(storage["total_size"]), Colors.BOLD + Colors.GREEN)

    # ========== LOG ANALYSIS ==========
    print_section("RECENT LOG ANALYSIS")

    log_info = check_log_for_errors()
    if log_info.get("last_heartbeat"):
        print_item("Last Heartbeat", log_info["last_heartbeat"])
    print_item("ML Iterations (recent)", log_info["ml_iterations"])

    if log_info.get("recent_errors"):
        print(f"\n  {c('Recent Errors:', Colors.RED)}")
        for err in log_info["recent_errors"][-5:]:
            print(f"    {c('!', Colors.RED)} {err[:100]}")
        warnings.append(f"Found {len(log_info['recent_errors'])} errors in recent logs")
    else:
        print_status("Log Errors", True, "No recent errors found")

    # ========== SYSTEM INFO ==========
    admin_info = get_admin_info()
    if admin_info:
        print_section("SYSTEM CONFIGURATION")

        sys_info = admin_info.get("system", {})
        config = admin_info.get("config", {})

        print_item("Platform", sys_info.get("platform", "Unknown"))
        print_item("Python Version", sys_info.get("python_version", "Unknown"))
        print_item("API Host:Port", f"{config.get('api_host', '?')}:{config.get('api_port', '?')}")
        print_item("Embedding Model", config.get("embedding_model", "Unknown"))
        print_item("Chunk Size", config.get("chunk_size", "?"))

    # ========== WARNINGS & ISSUES ==========
    if warnings or critical:
        print_section("WARNINGS & ISSUES")

        for c_msg in critical:
            print(f"  {c('[CRITICAL]', Colors.RED + Colors.BOLD)} {c_msg}")

        for w_msg in warnings:
            print(f"  {c('[WARNING]', Colors.YELLOW)} {w_msg}")

    # ========== SUMMARY ==========
    print_section("SUMMARY")

    health_score = 100
    if critical:
        health_score -= len(critical) * 30
    if warnings:
        health_score -= len(warnings) * 10
    health_score = max(0, health_score)

    if health_score >= 80:
        health_color = Colors.GREEN
        health_status = "HEALTHY"
    elif health_score >= 50:
        health_color = Colors.YELLOW
        health_status = "DEGRADED"
    else:
        health_color = Colors.RED
        health_status = "UNHEALTHY"

    print(f"\n  {c('Overall Health:', Colors.BOLD)} {c(f'{health_status} ({health_score}%)', health_color + Colors.BOLD)}")
    print(f"  {c('Critical Issues:', Colors.DIM)} {len(critical)}")
    print(f"  {c('Warnings:', Colors.DIM)} {len(warnings)}")

    if api_health["online"] and db_stats["connected"]:
        print(f"\n  {c('Quick Stats:', Colors.BOLD)}")
        print(f"    Documents: {db_stats['total_documents']:,} total, {db_stats['docs_last_24h']:,} in 24h")
        print(f"    Clusters: {db_stats['total_clusters']} | Tags: {db_stats['total_tags']:,}")
        print(f"    Emails: {email_status.get('email_count', 0) if email_status else 'N/A':,}")

    print(f"\n{c('=' * 60, Colors.DIM)}\n")

    # Exit code based on health
    sys.exit(0 if health_score >= 50 else 1)

if __name__ == "__main__":
    main()
