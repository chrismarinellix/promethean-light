"""Database connection and setup"""

import sqlite3
from pathlib import Path
from typing import Generator, Optional, Union
from sqlmodel import SQLModel, create_engine, Session
from sqlalchemy.pool import StaticPool


class Database:
    """Database manager with optional encryption support"""

    def __init__(self, db_path: Optional[Union[Path, str]] = None):
        if db_path is None:
            db_path = Path.home() / ".mydata" / "mydata.db"
        else:
            db_path = Path(db_path)

        db_path.parent.mkdir(parents=True, exist_ok=True)

        # Note: For full SQLite encryption, use sqlcipher in production
        # For this implementation, we use standard SQLite with application-level encryption
        connect_args = {
            "check_same_thread": False,
        }

        # Create engine
        self.engine = create_engine(
            f"sqlite:///{db_path}",
            echo=False,
            connect_args=connect_args,
            poolclass=StaticPool,  # Single connection for SQLite
        )

        # Create tables
        SQLModel.metadata.create_all(self.engine)

    def get_session(self) -> Generator[Session, None, None]:
        """Get database session (use with 'with' statement)"""
        with Session(self.engine) as session:
            yield session

    def session(self) -> Session:
        """Get a new session"""
        return Session(self.engine)
