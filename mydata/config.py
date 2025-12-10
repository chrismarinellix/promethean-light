"""Configuration management with environment variable support"""

import os
from pathlib import Path
from typing import List, Optional, Tuple


class Config:
    """Centralized configuration with environment variable fallbacks"""

    # Base paths
    MYDATA_HOME: Path = Path(os.getenv("MYDATA_HOME", str(Path.home() / ".mydata")))

    # Database
    DATABASE_PATH: Path = MYDATA_HOME / "mydata.db"
    DATABASE_TIMEOUT: int = int(os.getenv("DATABASE_TIMEOUT", "30"))

    # Vector Store
    QDRANT_PATH: Path = MYDATA_HOME / "qdrant"
    QDRANT_HOST: str = os.getenv("QDRANT_HOST", "localhost")
    QDRANT_PORT: int = int(os.getenv("QDRANT_PORT", "6333"))

    # API Server
    API_HOST: str = os.getenv("API_HOST", "127.0.0.1")
    API_PORT: int = int(os.getenv("API_PORT", "8000"))

    # ML / Embedding
    EMBEDDING_MODEL: str = os.getenv("EMBEDDING_MODEL", "BAAI/bge-base-en-v1.5")
    MODELS_CACHE_DIR: Path = MYDATA_HOME / "models"
    CHUNK_SIZE: int = int(os.getenv("CHUNK_SIZE", "512"))
    CHUNK_OVERLAP: int = int(os.getenv("CHUNK_OVERLAP", "50"))
    EMBEDDING_BATCH_SIZE: int = int(os.getenv("EMBEDDING_BATCH_SIZE", "32"))

    # Search
    SEMANTIC_SIMILARITY_THRESHOLD: float = float(os.getenv("SEMANTIC_SIMILARITY_THRESHOLD", "0.95"))
    HYBRID_SEARCH_VECTOR_WEIGHT: float = float(os.getenv("HYBRID_SEARCH_VECTOR_WEIGHT", "0.7"))
    HYBRID_SEARCH_BM25_WEIGHT: float = float(os.getenv("HYBRID_SEARCH_BM25_WEIGHT", "0.3"))
    DEFAULT_SEARCH_LIMIT: int = int(os.getenv("DEFAULT_SEARCH_LIMIT", "10"))

    # Cache
    CACHE_TTL_SECONDS: int = int(os.getenv("CACHE_TTL_SECONDS", "300"))
    CACHE_MAX_SIZE: int = int(os.getenv("CACHE_MAX_SIZE", "1000"))

    # File Watcher
    @staticmethod
    def _load_watch_directories() -> List[Path]:
        """Load watch directories from config file or environment."""
        # First check environment variable
        env_dirs = os.getenv("WATCH_DIRECTORIES")
        if env_dirs:
            return [Path(d.strip()) for d in env_dirs.split(",") if d.strip()]

        # Then check config file
        config_file = Path.home() / ".mydata" / "watch_directories.txt"
        if config_file.exists():
            try:
                dirs = []
                for line in config_file.read_text().strip().split("\n"):
                    line = line.strip()
                    if line and not line.startswith("#"):
                        dirs.append(Path(line))
                if dirs:
                    return dirs
            except Exception:
                pass

        # Default fallback
        return [Path.home() / "Documents", Path.home() / "Downloads"]

    WATCH_DIRECTORIES: List[Path] = _load_watch_directories.__func__()
    FILE_WATCHER_DEBOUNCE: float = float(os.getenv("FILE_WATCHER_DEBOUNCE", "0.5"))

    # Email Watcher
    EMAIL_POLL_INTERVAL: int = int(os.getenv("EMAIL_POLL_INTERVAL", "60"))
    EMAIL_HISTORY_HOURS: int = int(os.getenv("EMAIL_HISTORY_HOURS", "1440"))  # 60 days

    # Anonymization (for LLM context protection)
    # Set to "false" to send real names to OpenAI (better answers but less privacy)
    ENABLE_LLM_ANONYMIZATION: bool = os.getenv("ENABLE_LLM_ANONYMIZATION", "false").lower() == "true"
    USE_SPACY_NER: bool = os.getenv("USE_SPACY_NER", "true").lower() == "true"
    SPACY_MODEL: str = os.getenv("SPACY_MODEL", "en_core_web_sm")
    KNOWN_CLIENTS: List[str] = [
        c.strip() for c in os.getenv(
            "KNOWN_CLIENTS",
            "Alinta Energy,Origin Energy,AGL,EnergyAustralia"
        ).split(",") if c.strip()
    ]
    KNOWN_PROJECTS: List[str] = [
        p.strip() for p in os.getenv(
            "KNOWN_PROJECTS",
            "Boulder Creek,Dundonnell"
        ).split(",") if p.strip()
    ]
    KNOWN_EMPLOYEES: List[str] = [
        e.strip() for e in os.getenv(
            "KNOWN_EMPLOYEES",
            ""  # Will be populated from email senders
        ).split(",") if e.strip()
    ]

    # ML Organizer
    ML_POLL_INTERVAL: int = int(os.getenv("ML_POLL_INTERVAL", "300"))  # 5 minutes
    ML_MIN_CLUSTER_SIZE: int = int(os.getenv("ML_MIN_CLUSTER_SIZE", "5"))
    ML_MIN_SAMPLES: int = int(os.getenv("ML_MIN_SAMPLES", "3"))

    # Logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    LOG_DIR: Path = MYDATA_HOME / "logs"

    # Encryption
    PASSPHRASE_ENV: str = "MYDATA_PASSPHRASE"
    KEY_DERIVATION_ITERATIONS: int = int(os.getenv("KEY_DERIVATION_ITERATIONS", "600000"))

    @classmethod
    def ensure_directories(cls) -> None:
        """Create necessary directories if they don't exist"""
        cls.MYDATA_HOME.mkdir(parents=True, exist_ok=True)
        cls.MODELS_CACHE_DIR.mkdir(parents=True, exist_ok=True)
        cls.LOG_DIR.mkdir(parents=True, exist_ok=True)
        cls.QDRANT_PATH.mkdir(parents=True, exist_ok=True)

    @classmethod
    def get_passphrase_from_env(cls) -> Optional[str]:
        """Get passphrase from environment variable"""
        return os.getenv(cls.PASSPHRASE_ENV)

    @classmethod
    def print_config(cls) -> None:
        """Print current configuration (for debugging)"""
        print("\n=== Configuration ===")
        print(f"Data Directory: {cls.MYDATA_HOME}")
        print(f"Database: {cls.DATABASE_PATH}")
        print(f"API Server: {cls.API_HOST}:{cls.API_PORT}")
        print(f"Embedding Model: {cls.EMBEDDING_MODEL}")
        print(f"Chunk Size: {cls.CHUNK_SIZE}")
        print(f"Cache TTL: {cls.CACHE_TTL_SECONDS}s (max {cls.CACHE_MAX_SIZE} items)")
        print(f"Watch Directories: {', '.join(str(d) for d in cls.WATCH_DIRECTORIES)}")
        print(f"ML Poll Interval: {cls.ML_POLL_INTERVAL}s")
        print("=" * 50 + "\n")

    @classmethod
    def get_database_paths(cls, db_name: Optional[str] = None) -> Tuple[Path, Path]:
        """
        Get database-specific paths for SQLite and Qdrant.

        Args:
            db_name: Database name (e.g., "project_9002"). If None, returns default paths.

        Returns:
            Tuple of (sqlite_path, qdrant_path)

        Examples:
            get_database_paths(None) -> (~/.mydata/mydata.db, ~/.mydata/qdrant)
            get_database_paths("project_9002") -> (~/.mydata/project_9002/mydata.db, ~/.mydata/project_9002/qdrant)
        """
        if db_name is None or db_name == "default":
            # Default database paths (backward compatible)
            return (cls.DATABASE_PATH, cls.QDRANT_PATH)
        else:
            # Project-specific database paths
            db_dir = cls.MYDATA_HOME / db_name
            sqlite_path = db_dir / "mydata.db"
            qdrant_path = db_dir / "qdrant"
            return (sqlite_path, qdrant_path)

    @classmethod
    def ensure_database_directories(cls, db_name: Optional[str] = None) -> None:
        """Ensure database directories exist for the specified database"""
        sqlite_path, qdrant_path = cls.get_database_paths(db_name)
        sqlite_path.parent.mkdir(parents=True, exist_ok=True)
        qdrant_path.mkdir(parents=True, exist_ok=True)

    @classmethod
    def list_databases(cls) -> List[str]:
        """List all available databases (subdirectories in MYDATA_HOME)"""
        if not cls.MYDATA_HOME.exists():
            return []

        databases = ["default"]  # Default database is always available

        for item in cls.MYDATA_HOME.iterdir():
            if item.is_dir() and item.name not in ["models", "logs", "qdrant"]:
                # Check if it looks like a database (has mydata.db or qdrant folder)
                if (item / "mydata.db").exists() or (item / "qdrant").exists():
                    databases.append(item.name)

        return sorted(databases)


# Ensure directories exist on import
Config.ensure_directories()
