"""AgentMemory model for AI agent context storage."""

from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import Optional
from uuid import UUID, uuid4

from sqlmodel import Field, SQLModel


class AgentType(str, Enum):
    """Agent type enumeration."""

    chatbot = "chatbot"
    analytics = "analytics"
    notification = "notification"
    budget = "budget"


class MemoryType(str, Enum):
    """Memory type enumeration."""

    conversation = "conversation"
    preference = "preference"
    context = "context"
    summary = "summary"


class AgentMemory(SQLModel, table=True):
    """Agent memory for AI context storage (Phase III ready)."""

    __tablename__ = "agent_memory"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID = Field(foreign_key="users.id", index=True)
    agent_type: AgentType = Field(index=True)
    memory_type: MemoryType
    memory_key: str = Field(max_length=100, index=True)
    content: str
    # embedding_vector: VECTOR(1536) - Added in Phase III with pgvector extension
    importance_score: Decimal = Field(default=Decimal("0.50"), max_digits=3, decimal_places=2)
    access_count: int = Field(default=0)
    last_accessed_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class AgentMemoryRead(SQLModel):
    """Agent memory response schema."""

    id: UUID
    user_id: UUID
    agent_type: AgentType
    memory_type: MemoryType
    memory_key: str
    content: str
    importance_score: Decimal
    access_count: int
    last_accessed_at: Optional[datetime]
    expires_at: Optional[datetime]
    created_at: datetime


class AgentMemoryCreate(SQLModel):
    """Agent memory creation schema."""

    agent_type: AgentType
    memory_type: MemoryType
    memory_key: str
    content: str
    importance_score: Decimal = Decimal("0.50")
    expires_at: Optional[datetime] = None


class AgentMemoryUpdate(SQLModel):
    """Agent memory update schema."""

    content: Optional[str] = None
    importance_score: Optional[Decimal] = None
    expires_at: Optional[datetime] = None
