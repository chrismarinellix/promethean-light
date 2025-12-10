"""Authentication models for user management"""

from datetime import datetime
from typing import Optional
from sqlmodel import Field, SQLModel


class User(SQLModel, table=True):
    """User account model"""
    __tablename__ = "users"

    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(unique=True, index=True)
    full_name: str
    hashed_password: str
    is_active: bool = Field(default=False)  # Activated after email verification
    is_admin: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    last_login: Optional[datetime] = None

    # Email verification
    verification_token: Optional[str] = None
    verification_token_expires: Optional[datetime] = None
    email_verified: bool = Field(default=False)

    # Password reset
    reset_token: Optional[str] = None
    reset_token_expires: Optional[datetime] = None


class UserSession(SQLModel, table=True):
    """User session tracking"""
    __tablename__ = "user_sessions"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id")
    token: str = Field(unique=True, index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    expires_at: datetime
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None


class LoginAttempt(SQLModel, table=True):
    """Track login attempts for security"""
    __tablename__ = "login_attempts"

    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(index=True)
    success: bool
    ip_address: Optional[str] = None
    attempted_at: datetime = Field(default_factory=datetime.utcnow)
