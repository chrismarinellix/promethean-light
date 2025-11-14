"""Database models for MyData"""

from datetime import datetime
from uuid import UUID, uuid4
from typing import Optional, List, TYPE_CHECKING
from sqlmodel import SQLModel, Field, Relationship

if TYPE_CHECKING:
    from typing import List


class Document(SQLModel, table=True):
    """Main document table"""

    __tablename__ = "documents"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    source: str = Field(index=True)  # "file://path", "email://addr/uid", "stdin"
    source_type: str = Field(index=True)  # "file", "email", "paste"
    mime_type: Optional[str] = None
    file_hash: Optional[str] = Field(default=None, index=True)  # SHA-256 for dedup
    raw_text: str  # Original text (will be encrypted in practice)
    created_at: datetime = Field(default_factory=datetime.utcnow, index=True)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    cluster_id: Optional[int] = Field(default=None, index=True)

    # Relationships
    chunks: List["Chunk"] = Relationship(back_populates="document")
    tags: List["Tag"] = Relationship(back_populates="document")


class Chunk(SQLModel, table=True):
    """Text chunks for embedding (max 512 tokens each)"""

    __tablename__ = "chunks"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    doc_id: UUID = Field(foreign_key="documents.id", index=True)
    text: str
    start_offset: int  # Character offset in original document
    end_offset: int
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationship
    document: Document = Relationship(back_populates="chunks")


class Tag(SQLModel, table=True):
    """Auto-generated tags"""

    __tablename__ = "tags"

    id: int = Field(default=None, primary_key=True)
    doc_id: UUID = Field(foreign_key="documents.id", index=True)
    tag: str = Field(index=True)
    confidence: float = 1.0  # For ML-generated tags
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationship
    document: Document = Relationship(back_populates="tags")


class Cluster(SQLModel, table=True):
    """Document clusters from HDBSCAN"""

    __tablename__ = "clusters"

    id: int = Field(default=None, primary_key=True)
    label: str  # Auto-generated or user-provided
    description: Optional[str] = None  # Optional LLM summary
    document_count: int = 0
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class EmailCredential(SQLModel, table=True):
    """Encrypted email credentials"""

    __tablename__ = "email_credentials"

    id: int = Field(default=None, primary_key=True)
    email_address: str = Field(unique=True, index=True)
    encrypted_password: bytes  # Fernet-encrypted
    imap_server: str = "imap.gmail.com"
    imap_port: int = 993
    last_uid: Optional[str] = None  # Last processed email UID
    enabled: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)
