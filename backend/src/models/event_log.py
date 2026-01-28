"""EventLog model for event-driven architecture and audit trail."""

from datetime import datetime
from enum import Enum
from typing import Any, Optional
from uuid import UUID, uuid4

from sqlmodel import Column, Field, SQLModel
from sqlalchemy import JSON


class EventType(str, Enum):
    """Event type enumeration for all system events."""

    # Transaction events
    transaction_created = "TransactionCreated"
    transaction_updated = "TransactionUpdated"
    transaction_deleted = "TransactionDeleted"

    # Budget events
    budget_created = "BudgetCreated"
    budget_updated = "BudgetUpdated"
    budget_exceeded = "BudgetExceeded"
    budget_warning = "BudgetWarning"

    # Goal events
    goal_created = "GoalCreated"
    goal_updated = "GoalUpdated"
    goal_completed = "GoalCompleted"

    # User events
    user_login = "UserLogin"
    user_logout = "UserLogout"
    user_preference_changed = "UserPreferenceChanged"

    # Insight events
    insight_generated = "InsightGenerated"

    # Wallet events
    wallet_created = "WalletCreated"
    wallet_updated = "WalletUpdated"


class EventSource(str, Enum):
    """Event source enumeration."""

    api = "api"
    ui = "ui"
    agent = "agent"
    system = "system"
    scheduler = "scheduler"


class EventLog(SQLModel, table=True):
    """Immutable event log for audit trail and event-driven architecture."""

    __tablename__ = "event_logs"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID = Field(foreign_key="users.id", index=True)
    event_type: EventType = Field(index=True)
    event_source: EventSource
    aggregate_type: str = Field(max_length=50, index=True)
    aggregate_id: UUID = Field(index=True)
    event_data: dict[str, Any] = Field(sa_column=Column(JSON))
    extra_data: Optional[dict[str, Any]] = Field(default=None, sa_column=Column(JSON))
    correlation_id: Optional[UUID] = Field(default=None, index=True)
    causation_id: Optional[UUID] = None
    version: int = Field(default=1, ge=1)
    is_processed: bool = Field(default=False, index=True)
    processed_at: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow, index=True)


class EventLogRead(SQLModel):
    """Event log response schema."""

    id: UUID
    user_id: UUID
    event_type: EventType
    event_source: EventSource
    aggregate_type: str
    aggregate_id: UUID
    event_data: dict[str, Any]
    extra_data: Optional[dict[str, Any]]
    correlation_id: Optional[UUID]
    version: int
    is_processed: bool
    processed_at: Optional[datetime]
    created_at: datetime


class EventLogCreate(SQLModel):
    """Event log creation schema."""

    event_type: EventType
    event_source: EventSource
    aggregate_type: str
    aggregate_id: UUID
    event_data: dict[str, Any]
    extra_data: Optional[dict[str, Any]] = None
    correlation_id: Optional[UUID] = None
    causation_id: Optional[UUID] = None
