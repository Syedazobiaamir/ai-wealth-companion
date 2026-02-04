"""Conversation model for AI chat sessions."""

from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4

from sqlmodel import Field, SQLModel


class Conversation(SQLModel, table=True):
    """Represents an ongoing chat session between a user and the AI assistant."""

    __tablename__ = "conversations"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID = Field(foreign_key="users.id", index=True)
    title: Optional[str] = Field(default=None, max_length=200)
    language: str = Field(default="en", max_length=5)
    is_active: bool = Field(default=True, index=True)
    message_count: int = Field(default=0)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class ConversationCreate(SQLModel):
    """Conversation creation schema."""

    title: Optional[str] = None
    language: str = "en"


class ConversationRead(SQLModel):
    """Conversation response schema."""

    id: UUID
    user_id: UUID
    title: Optional[str]
    language: str
    is_active: bool
    message_count: int
    created_at: datetime
    updated_at: datetime
