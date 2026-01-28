"""InsightCache model for AI-generated insights."""

from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import Any, Optional
from uuid import UUID, uuid4

from sqlmodel import Column, Field, SQLModel
from sqlalchemy import JSON


class InsightType(str, Enum):
    """Insight type enumeration."""

    spending_pattern = "spending_pattern"
    budget_recommendation = "budget_recommendation"
    saving_tip = "saving_tip"
    anomaly = "anomaly"


class InsightSeverity(str, Enum):
    """Insight severity enumeration."""

    info = "info"
    suggestion = "suggestion"
    warning = "warning"
    alert = "alert"


class InsightCache(SQLModel, table=True):
    """Cached AI-generated insights."""

    __tablename__ = "insight_cache"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID = Field(foreign_key="users.id", index=True)
    insight_type: InsightType = Field(index=True)
    insight_key: str = Field(max_length=100)
    title: str = Field(max_length=200)
    content: str
    content_ur: Optional[str] = None  # Urdu translation for Phase III
    severity: InsightSeverity = Field(default=InsightSeverity.info)
    related_category_id: Optional[UUID] = Field(default=None, foreign_key="category.id")
    related_amount: Optional[Decimal] = Field(default=None, max_digits=15, decimal_places=2)
    extra_data: Optional[dict[str, Any]] = Field(default=None, sa_column=Column(JSON))
    is_read: bool = Field(default=False, index=True)
    is_dismissed: bool = Field(default=False)
    valid_from: datetime = Field(default_factory=datetime.utcnow)
    valid_until: datetime
    created_at: datetime = Field(default_factory=datetime.utcnow)


class InsightCacheRead(SQLModel):
    """Insight cache response schema."""

    id: UUID
    user_id: UUID
    insight_type: InsightType
    title: str
    content: str
    content_ur: Optional[str]
    severity: InsightSeverity
    related_category_id: Optional[UUID]
    related_amount: Optional[Decimal]
    is_read: bool
    is_dismissed: bool
    valid_from: datetime
    valid_until: datetime
    created_at: datetime


class InsightCacheCreate(SQLModel):
    """Insight cache creation schema."""

    insight_type: InsightType
    insight_key: str
    title: str
    content: str
    content_ur: Optional[str] = None
    severity: InsightSeverity = InsightSeverity.info
    related_category_id: Optional[UUID] = None
    related_amount: Optional[Decimal] = None
    extra_data: Optional[dict[str, Any]] = None
    valid_until: datetime
