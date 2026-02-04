"""Message model for individual chat exchanges."""

from datetime import datetime
from enum import Enum
from typing import Any, Optional
from uuid import UUID, uuid4

from sqlalchemy import JSON, Column
from sqlmodel import Field, SQLModel


class MessageRole(str, Enum):
    """Message sender type."""

    user = "user"
    assistant = "assistant"
    system = "system"


class InputMethod(str, Enum):
    """How the message was entered."""

    text = "text"
    voice = "voice"


class Message(SQLModel, table=True):
    """An individual exchange within a conversation."""

    __tablename__ = "messages"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    conversation_id: UUID = Field(foreign_key="conversations.id", index=True)
    role: MessageRole
    content: str
    content_ur: Optional[str] = None
    intent: Optional[str] = Field(default=None, max_length=50)
    entities: Optional[dict[str, Any]] = Field(default=None, sa_column=Column(JSON))
    tool_calls: Optional[list[dict[str, Any]]] = Field(
        default=None, sa_column=Column(JSON)
    )
    confidence: Optional[float] = None
    input_method: InputMethod = Field(default=InputMethod.text)
    processing_time_ms: Optional[int] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)


class MessageCreate(SQLModel):
    """Message creation schema."""

    conversation_id: UUID
    role: MessageRole
    content: str
    content_ur: Optional[str] = None
    intent: Optional[str] = None
    entities: Optional[dict[str, Any]] = None
    tool_calls: Optional[list[dict[str, Any]]] = None
    confidence: Optional[float] = None
    input_method: InputMethod = InputMethod.text
    processing_time_ms: Optional[int] = None


class MessageRead(SQLModel):
    """Message response schema."""

    id: UUID
    conversation_id: UUID
    role: MessageRole
    content: str
    content_ur: Optional[str]
    intent: Optional[str]
    entities: Optional[dict[str, Any]]
    tool_calls: Optional[list[dict[str, Any]]]
    confidence: Optional[float]
    input_method: InputMethod
    processing_time_ms: Optional[int]
    created_at: datetime
