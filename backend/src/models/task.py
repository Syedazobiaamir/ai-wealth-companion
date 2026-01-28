"""Task model for financial tasks and reminders."""

from datetime import date, datetime
from enum import Enum
from typing import Optional
from uuid import UUID, uuid4

from sqlmodel import Field, SQLModel


class TaskPriority(str, Enum):
    """Task priority enumeration."""

    high = "high"
    medium = "medium"
    low = "low"


class TaskCategory(str, Enum):
    """Task category enumeration."""

    bills = "bills"
    savings = "savings"
    review = "review"
    investment = "investment"
    budget = "budget"
    other = "other"


class RecurringFrequency(str, Enum):
    """Recurring frequency enumeration."""

    daily = "daily"
    weekly = "weekly"
    monthly = "monthly"


class TaskBase(SQLModel):
    """Base task schema with common fields."""

    title: str = Field(max_length=200)
    description: Optional[str] = Field(default=None, max_length=1000)
    priority: TaskPriority = Field(default=TaskPriority.medium)
    category: TaskCategory = Field(default=TaskCategory.other)
    due_date: Optional[date] = None
    is_recurring: bool = Field(default=False)
    recurring_frequency: Optional[RecurringFrequency] = None


class Task(TaskBase, table=True):
    """Task database model."""

    __tablename__ = "tasks"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID = Field(foreign_key="users.id", index=True)
    is_completed: bool = Field(default=False, index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None


class TaskCreate(TaskBase):
    """Task creation schema."""

    pass


class TaskRead(TaskBase):
    """Task response schema."""

    id: UUID
    user_id: UUID
    is_completed: bool
    created_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime]


class TaskUpdate(SQLModel):
    """Task update schema."""

    title: Optional[str] = None
    description: Optional[str] = None
    priority: Optional[TaskPriority] = None
    category: Optional[TaskCategory] = None
    due_date: Optional[date] = None
    is_recurring: Optional[bool] = None
    recurring_frequency: Optional[RecurringFrequency] = None
    is_completed: Optional[bool] = None
