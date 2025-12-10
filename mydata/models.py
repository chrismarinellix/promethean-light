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
    updated_at: datetime = Field(default_factory=datetime.utcnow, index=True)  # Index for sorting
    cluster_id: Optional[int] = Field(default=None, index=True)

    # File metadata for change tracking
    file_modified_at: Optional[datetime] = Field(default=None, index=True)  # When file was last modified
    file_created_at: Optional[datetime] = Field(default=None, index=True)  # When file was created
    file_size_bytes: Optional[int] = None  # File size in bytes
    file_owner: Optional[str] = None  # File owner/author (from Windows attributes)

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
    created_at: datetime = Field(default_factory=datetime.utcnow, index=True)  # Index for time-based queries

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


class Project(SQLModel, table=True):
    """Grid connection study projects"""

    __tablename__ = "projects"

    id: int = Field(default=None, primary_key=True)
    name: str = Field(index=True)  # Project name
    client_name: str = Field(index=True)  # Client name
    project_type: Optional[str] = None  # "Solar", "Wind", "BESS", "Hybrid"
    capacity_mw: Optional[float] = None  # Project capacity in MW
    status: str = Field(default="Active")  # "Active", "On Hold", "Completed", "Cancelled"
    start_date: Optional[datetime] = None
    target_completion: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    checklists: List["WeeklyChecklist"] = Relationship(back_populates="project")


class WeeklyChecklist(SQLModel, table=True):
    """Weekly client check-in checklists"""

    __tablename__ = "weekly_checklists"

    id: int = Field(default=None, primary_key=True)
    project_id: int = Field(foreign_key="projects.id", index=True)
    engineer_name: str = Field(index=True)
    week_ending: datetime = Field(index=True)

    # Health rating
    health_rating: str  # "GREEN", "YELLOW", "RED"

    # JSON stored data (for flexibility)
    checklist_data: str  # JSON string of all checkbox/field values

    # Key extracted fields for quick querying
    has_scope_changes: bool = False
    has_client_concerns: bool = False
    has_blockers: bool = False
    on_schedule: bool = True
    on_budget: bool = True

    # Summary fields
    going_well: Optional[str] = None
    needs_attention: Optional[str] = None
    key_message: Optional[str] = None

    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationship
    project: Project = Relationship(back_populates="checklists")


class ApiKey(SQLModel, table=True):
    """Encrypted API keys (shared across all databases)"""

    __tablename__ = "api_keys"

    id: int = Field(default=None, primary_key=True)
    service: str = Field(unique=True, index=True)  # "openai", "anthropic", etc.
    encrypted_key: bytes  # Fernet-encrypted API key
    enabled: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class ChatConversation(SQLModel, table=True):
    """Chat conversation threads"""

    __tablename__ = "chat_conversations"

    id: int = Field(default=None, primary_key=True)
    title: Optional[str] = None  # Auto-generated from first message
    created_at: datetime = Field(default_factory=datetime.utcnow, index=True)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    messages: List["ChatMessage"] = Relationship(back_populates="conversation")


class ChatMessage(SQLModel, table=True):
    """Individual chat messages"""

    __tablename__ = "chat_messages"

    id: int = Field(default=None, primary_key=True)
    conversation_id: int = Field(foreign_key="chat_conversations.id", index=True)
    role: str = Field(index=True)  # "user", "assistant", "system"
    content: str  # Message content

    # RAG metadata
    sources_used: Optional[str] = None  # JSON array of document IDs used
    retrieved_chunks: Optional[int] = None  # Number of chunks retrieved

    created_at: datetime = Field(default_factory=datetime.utcnow, index=True)

    # Relationship
    conversation: ChatConversation = Relationship(back_populates="messages")


class SavedSearch(SQLModel, table=True):
    """Saved searches/queries with responses"""

    __tablename__ = "saved_searches"

    id: int = Field(default=None, primary_key=True)
    folder: str = Field(default="general", index=True)  # Folder name for organization
    query: str  # The search query
    response: str  # The response/answer
    sources: Optional[str] = None  # JSON array of source documents

    created_at: datetime = Field(default_factory=datetime.utcnow, index=True)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
