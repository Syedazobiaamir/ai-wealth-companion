"""Budget model for monthly spending limits."""

from datetime import datetime
from decimal import Decimal
from typing import Optional
from uuid import UUID, uuid4

from sqlmodel import Field, SQLModel, UniqueConstraint


class BudgetBase(SQLModel):
    """Base budget schema for validation."""

    category_id: UUID
    limit_amount: Decimal = Field(gt=0, max_digits=12, decimal_places=2)
    month: int = Field(ge=1, le=12)
    year: int = Field(ge=2020)
    alert_threshold: int = Field(default=80, ge=0, le=100)


class Budget(BudgetBase, table=True):
    """Budget database model with unique constraint on user+category+month+year."""

    __tablename__ = "budgets"
    __table_args__ = (
        UniqueConstraint("user_id", "category_id", "month", "year", name="uq_budget_user_category_month_year"),
    )

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID = Field(foreign_key="users.id", index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class BudgetCreate(BudgetBase):
    """Budget creation schema."""

    pass


class BudgetUpdate(SQLModel):
    """Budget update schema with optional fields."""

    limit_amount: Optional[Decimal] = Field(default=None, gt=0, max_digits=12, decimal_places=2)
    month: Optional[int] = Field(default=None, ge=1, le=12)
    year: Optional[int] = Field(default=None, ge=2020)


class BudgetRead(BudgetBase):
    """Budget response schema."""

    id: UUID
    user_id: UUID
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class BudgetStatus(SQLModel):
    """Computed budget status with spending analysis."""

    category: str
    emoji: str
    limit: Decimal
    spent: Decimal
    remaining: Decimal
    percentage: Decimal
    exceeded: bool
    warning: bool  # True if percentage >= 80
