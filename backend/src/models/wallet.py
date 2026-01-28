"""Wallet model for financial accounts."""

from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import Optional
from uuid import UUID, uuid4

from sqlmodel import Field, SQLModel


class WalletType(str, Enum):
    """Wallet type enumeration."""

    cash = "cash"
    bank = "bank"
    credit = "credit"
    savings = "savings"
    investment = "investment"


class WalletBase(SQLModel):
    """Base wallet schema with common fields."""

    name: str = Field(max_length=100)
    type: WalletType
    currency: str = Field(default="PKR", max_length=3)
    initial_balance: Decimal = Field(default=Decimal("0.00"), max_digits=15, decimal_places=2)
    color: Optional[str] = Field(default=None, max_length=7)
    icon: Optional[str] = Field(default=None, max_length=50)


class Wallet(WalletBase, table=True):
    """Wallet database model."""

    __tablename__ = "wallets"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID = Field(foreign_key="users.id", index=True)
    current_balance: Decimal = Field(default=Decimal("0.00"), max_digits=15, decimal_places=2)
    is_active: bool = Field(default=True)
    is_default: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class WalletCreate(WalletBase):
    """Wallet creation schema."""

    pass


class WalletRead(WalletBase):
    """Wallet response schema."""

    id: UUID
    user_id: UUID
    current_balance: Decimal
    is_active: bool
    is_default: bool
    created_at: datetime


class WalletUpdate(SQLModel):
    """Wallet update schema."""

    name: Optional[str] = None
    type: Optional[WalletType] = None
    color: Optional[str] = None
    icon: Optional[str] = None
    is_default: Optional[bool] = None
