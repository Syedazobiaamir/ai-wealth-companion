"""Category model for transaction categorization."""

from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4

from sqlmodel import Field, SQLModel


class CategoryBase(SQLModel):
    """Base category schema for validation."""

    name: str = Field(max_length=50, index=True)
    emoji: str = Field(max_length=10)


class Category(CategoryBase, table=True):
    """Category database model."""

    __tablename__ = "category"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)


class CategoryRead(CategoryBase):
    """Category response schema."""

    id: UUID
    created_at: Optional[datetime] = None
