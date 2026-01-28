"""Goal model for financial targets."""

from datetime import date, datetime
from decimal import Decimal
from enum import Enum
from typing import Optional
from uuid import UUID, uuid4

from sqlmodel import Field, SQLModel


class GoalStatus(str, Enum):
    """Goal status enumeration."""

    active = "active"
    completed = "completed"
    paused = "paused"
    cancelled = "cancelled"


class GoalBase(SQLModel):
    """Base goal schema with common fields."""

    name: str = Field(max_length=100)
    description: Optional[str] = Field(default=None, max_length=500)
    target_amount: Decimal = Field(max_digits=15, decimal_places=2, gt=0)
    currency: str = Field(default="PKR", max_length=3)
    target_date: Optional[date] = None
    emoji: str = Field(default="🎯", max_length=10)
    color: Optional[str] = Field(default=None, max_length=7)
    priority: int = Field(default=0)


class Goal(GoalBase, table=True):
    """Goal database model."""

    __tablename__ = "goals"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID = Field(foreign_key="users.id", index=True)
    current_amount: Decimal = Field(default=Decimal("0.00"), max_digits=15, decimal_places=2)
    status: GoalStatus = Field(default=GoalStatus.active, index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None


class GoalCreate(GoalBase):
    """Goal creation schema."""

    pass


class GoalRead(GoalBase):
    """Goal response schema with computed fields."""

    id: UUID
    user_id: UUID
    current_amount: Decimal
    status: GoalStatus
    created_at: datetime
    completed_at: Optional[datetime]

    @property
    def percentage_complete(self) -> float:
        """Calculate completion percentage."""
        if self.target_amount == 0:
            return 100.0
        return float((self.current_amount / self.target_amount) * 100)

    @property
    def remaining_amount(self) -> Decimal:
        """Calculate remaining amount."""
        return self.target_amount - self.current_amount


class GoalUpdate(SQLModel):
    """Goal update schema."""

    name: Optional[str] = None
    description: Optional[str] = None
    target_amount: Optional[Decimal] = None
    current_amount: Optional[Decimal] = None
    target_date: Optional[date] = None
    emoji: Optional[str] = None
    color: Optional[str] = None
    priority: Optional[int] = None
    status: Optional[GoalStatus] = None
