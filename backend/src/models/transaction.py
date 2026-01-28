"""Transaction model for income/expense tracking."""

from datetime import date, datetime
from decimal import Decimal
from enum import Enum
from typing import Optional
from uuid import UUID, uuid4

from sqlmodel import Field, SQLModel


class TransactionType(str, Enum):
    """Transaction type enumeration."""

    income = "income"
    expense = "expense"


class TransactionBase(SQLModel):
    """Base transaction schema for validation."""

    type: TransactionType
    amount: Decimal = Field(gt=0, max_digits=12, decimal_places=2)
    category_id: UUID
    transaction_date: date
    note: Optional[str] = Field(default=None, max_length=255)
    is_recurring: bool = Field(default=False)
    recurring_frequency: Optional[str] = Field(default=None, max_length=20)
    tags: Optional[str] = Field(default=None, max_length=500)


class Transaction(TransactionBase, table=True):
    """Transaction database model with soft delete support."""

    __tablename__ = "transactions"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID = Field(foreign_key="users.id", index=True)
    wallet_id: Optional[UUID] = Field(default=None, foreign_key="wallets.id", index=True)
    is_deleted: bool = Field(default=False, index=True)
    deleted_at: Optional[datetime] = Field(default=None)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Alias for backward compatibility with Phase I
    @property
    def date(self) -> date:
        return self.transaction_date

    @property
    def recurring(self) -> bool:
        return self.is_recurring


class TransactionCreate(SQLModel):
    """Transaction creation schema."""

    type: TransactionType
    amount: Decimal = Field(gt=0, max_digits=12, decimal_places=2)
    category_id: UUID
    wallet_id: Optional[UUID] = None
    transaction_date: date
    note: Optional[str] = Field(default=None, max_length=255)
    is_recurring: bool = Field(default=False)
    recurring_frequency: Optional[str] = Field(default=None, max_length=20)
    tags: Optional[str] = Field(default=None, max_length=500)


class TransactionUpdate(SQLModel):
    """Transaction update schema with optional fields."""

    type: Optional[TransactionType] = None
    amount: Optional[Decimal] = Field(default=None, gt=0, max_digits=12, decimal_places=2)
    category_id: Optional[UUID] = None
    wallet_id: Optional[UUID] = None
    transaction_date: Optional[date] = None
    note: Optional[str] = Field(default=None, max_length=255)
    is_recurring: Optional[bool] = None
    recurring_frequency: Optional[str] = None
    tags: Optional[str] = None


class TransactionRead(SQLModel):
    """Transaction response schema."""

    id: UUID
    user_id: UUID
    wallet_id: Optional[UUID]
    type: TransactionType
    amount: Decimal
    category_id: UUID
    transaction_date: date
    note: Optional[str]
    is_recurring: bool
    recurring_frequency: Optional[str]
    tags: Optional[str]
    created_at: datetime
    updated_at: datetime


class TransactionWithCategory(TransactionRead):
    """Transaction response with category details."""

    category_name: Optional[str] = None
    category_emoji: Optional[str] = None
