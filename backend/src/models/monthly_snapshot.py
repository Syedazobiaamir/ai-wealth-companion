"""MonthlySnapshot model for pre-computed financial summaries."""

from datetime import datetime
from decimal import Decimal
from typing import Any, Optional
from uuid import UUID, uuid4

from sqlmodel import Column, Field, SQLModel
from sqlalchemy import JSON


class MonthlySnapshot(SQLModel, table=True):
    """Monthly financial snapshot for performance optimization."""

    __tablename__ = "monthly_snapshots"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID = Field(foreign_key="users.id", index=True)
    year: int = Field(ge=2000, le=2100)
    month: int = Field(ge=1, le=12)
    total_income: Decimal = Field(default=Decimal("0.00"), max_digits=15, decimal_places=2)
    total_expenses: Decimal = Field(default=Decimal("0.00"), max_digits=15, decimal_places=2)
    net_savings: Decimal = Field(default=Decimal("0.00"), max_digits=15, decimal_places=2)
    savings_rate: Decimal = Field(default=Decimal("0.00"), max_digits=5, decimal_places=2)
    top_expense_category: Optional[str] = Field(default=None, max_length=50)
    top_expense_amount: Decimal = Field(default=Decimal("0.00"), max_digits=15, decimal_places=2)
    transaction_count: int = Field(default=0)
    budget_adherence_rate: Decimal = Field(default=Decimal("0.00"), max_digits=5, decimal_places=2)
    category_breakdown: Optional[dict[str, Any]] = Field(default=None, sa_column=Column(JSON))
    computed_at: datetime = Field(default_factory=datetime.utcnow)
    created_at: datetime = Field(default_factory=datetime.utcnow)


class MonthlySnapshotRead(SQLModel):
    """Monthly snapshot response schema."""

    id: UUID
    user_id: UUID
    year: int
    month: int
    total_income: Decimal
    total_expenses: Decimal
    net_savings: Decimal
    savings_rate: Decimal
    top_expense_category: Optional[str]
    top_expense_amount: Decimal
    transaction_count: int
    budget_adherence_rate: Decimal
    category_breakdown: Optional[dict[str, Any]]
    computed_at: datetime
