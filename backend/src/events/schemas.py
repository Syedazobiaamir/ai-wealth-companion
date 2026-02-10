"""
Phase V: Event Schemas Module
AI Wealth Companion Cloud-Native Events

Defines CloudEvents-compliant event schemas for the event-driven architecture.
All events follow the CloudEvents specification v1.0.
"""

from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import Any, Dict, List, Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class EventType(str, Enum):
    """Event types for the AI Wealth Companion system."""

    # Transaction events
    TRANSACTION_CREATED = "transaction.created"
    TRANSACTION_UPDATED = "transaction.updated"
    TRANSACTION_DELETED = "transaction.deleted"

    # Budget events
    BUDGET_EXCEEDED = "budget.exceeded"
    BUDGET_WARNING = "budget.warning"
    BUDGET_CREATED = "budget.created"
    BUDGET_UPDATED = "budget.updated"

    # AI events
    AI_INSIGHT_GENERATED = "ai.insight.generated"
    AI_ANALYSIS_COMPLETED = "ai.analysis.completed"

    # User events
    USER_ALERT_SENT = "user.alert.sent"
    USER_NOTIFICATION_DELIVERED = "user.notification.delivered"

    # Goal events
    GOAL_PROGRESS_UPDATED = "goal.progress.updated"
    GOAL_ACHIEVED = "goal.achieved"


class BaseEvent(BaseModel):
    """
    Base CloudEvents-compliant event schema.

    All events in the system inherit from this base class and follow
    the CloudEvents specification v1.0.
    """

    # CloudEvents required attributes
    id: UUID = Field(default_factory=uuid4, description="Unique event identifier")
    source: str = Field(default="ai-wealth-companion", description="Event source URI")
    specversion: str = Field(default="1.0", description="CloudEvents spec version")
    type: EventType = Field(..., description="Event type")

    # CloudEvents optional attributes
    datacontenttype: str = Field(default="application/json", description="Content type")
    subject: Optional[str] = Field(None, description="Event subject (e.g., user_id)")
    time: datetime = Field(default_factory=datetime.utcnow, description="Event timestamp")

    # Extension attributes
    correlationid: Optional[UUID] = Field(None, description="Correlation ID for tracing")
    causationid: Optional[UUID] = Field(None, description="ID of event that caused this")

    # Custom metadata
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")

    class Config:
        json_encoders = {
            UUID: str,
            datetime: lambda v: v.isoformat(),
            Decimal: str,
        }
        use_enum_values = True


class TransactionData(BaseModel):
    """Transaction event data payload."""

    transaction_id: UUID
    user_id: UUID
    wallet_id: UUID
    amount: Decimal
    currency: str = "USD"
    category_id: Optional[UUID] = None
    category_name: Optional[str] = None
    description: Optional[str] = None
    transaction_type: str  # "income" or "expense"
    transaction_date: datetime

    class Config:
        json_encoders = {
            UUID: str,
            datetime: lambda v: v.isoformat(),
            Decimal: str,
        }


class TransactionCreatedEvent(BaseEvent):
    """
    Event emitted when a new transaction is created.

    Topic: transactions
    Subscribers: Analytics Agent, Notification Agent
    """

    type: EventType = Field(default=EventType.TRANSACTION_CREATED)
    data: TransactionData

    @classmethod
    def from_transaction(cls, transaction: Any, user_id: UUID) -> "TransactionCreatedEvent":
        """Create event from a transaction model instance."""
        return cls(
            subject=str(user_id),
            data=TransactionData(
                transaction_id=transaction.id,
                user_id=user_id,
                wallet_id=transaction.wallet_id,
                amount=transaction.amount,
                currency=getattr(transaction, "currency", "USD"),
                category_id=transaction.category_id,
                category_name=getattr(transaction.category, "name", None) if transaction.category else None,
                description=transaction.description,
                transaction_type=transaction.type,
                transaction_date=transaction.date,
            ),
        )


class TransactionUpdatedEvent(BaseEvent):
    """
    Event emitted when a transaction is updated.

    Topic: transactions
    Subscribers: Analytics Agent
    """

    type: EventType = Field(default=EventType.TRANSACTION_UPDATED)
    data: TransactionData
    previous_amount: Optional[Decimal] = None
    previous_category_id: Optional[UUID] = None


class BudgetExceededData(BaseModel):
    """Budget exceeded event data payload."""

    budget_id: UUID
    user_id: UUID
    category_id: Optional[UUID] = None
    category_name: Optional[str] = None
    budget_amount: Decimal
    spent_amount: Decimal
    exceeded_by: Decimal
    percentage_used: float
    period_start: datetime
    period_end: datetime

    class Config:
        json_encoders = {
            UUID: str,
            datetime: lambda v: v.isoformat(),
            Decimal: str,
        }


class BudgetExceededEvent(BaseEvent):
    """
    Event emitted when a budget threshold is exceeded.

    Topic: budget-alerts
    Subscribers: Notification Agent, AI Insights Generator
    """

    type: EventType = Field(default=EventType.BUDGET_EXCEEDED)
    data: BudgetExceededData
    severity: str = Field(default="warning", description="warning, critical, exceeded")

    @classmethod
    def from_budget_check(
        cls,
        budget: Any,
        spent_amount: Decimal,
        user_id: UUID,
        severity: str = "warning",
    ) -> "BudgetExceededEvent":
        """Create event from budget check result."""
        exceeded_by = spent_amount - budget.amount
        percentage = float(spent_amount / budget.amount * 100) if budget.amount > 0 else 0

        return cls(
            subject=str(user_id),
            severity=severity,
            data=BudgetExceededData(
                budget_id=budget.id,
                user_id=user_id,
                category_id=budget.category_id,
                category_name=getattr(budget.category, "name", None) if budget.category else None,
                budget_amount=budget.amount,
                spent_amount=spent_amount,
                exceeded_by=exceeded_by if exceeded_by > 0 else Decimal(0),
                percentage_used=percentage,
                period_start=budget.start_date,
                period_end=budget.end_date,
            ),
        )


class AIInsightData(BaseModel):
    """AI insight event data payload."""

    insight_id: UUID = Field(default_factory=uuid4)
    user_id: UUID
    insight_type: str  # "spending_pattern", "budget_warning", "savings_opportunity", etc.
    title: str
    content: str
    confidence_score: float = Field(ge=0.0, le=1.0)
    recommendations: List[str] = Field(default_factory=list)
    related_entities: Dict[str, List[str]] = Field(default_factory=dict)
    expires_at: Optional[datetime] = None

    class Config:
        json_encoders = {
            UUID: str,
            datetime: lambda v: v.isoformat(),
        }


class AIInsightGeneratedEvent(BaseEvent):
    """
    Event emitted when an AI insight is generated.

    Topic: ai-insights
    Subscribers: Notification Agent, Frontend WebSocket
    """

    type: EventType = Field(default=EventType.AI_INSIGHT_GENERATED)
    data: AIInsightData
    priority: str = Field(default="normal", description="low, normal, high, urgent")

    @classmethod
    def create_spending_pattern_insight(
        cls,
        user_id: UUID,
        title: str,
        content: str,
        recommendations: List[str],
        confidence: float = 0.85,
    ) -> "AIInsightGeneratedEvent":
        """Create a spending pattern insight event."""
        return cls(
            subject=str(user_id),
            priority="normal",
            data=AIInsightData(
                user_id=user_id,
                insight_type="spending_pattern",
                title=title,
                content=content,
                confidence_score=confidence,
                recommendations=recommendations,
            ),
        )

    @classmethod
    def create_budget_warning_insight(
        cls,
        user_id: UUID,
        budget_id: UUID,
        title: str,
        content: str,
        percentage_used: float,
    ) -> "AIInsightGeneratedEvent":
        """Create a budget warning insight event."""
        priority = "urgent" if percentage_used >= 100 else "high" if percentage_used >= 80 else "normal"

        return cls(
            subject=str(user_id),
            priority=priority,
            data=AIInsightData(
                user_id=user_id,
                insight_type="budget_warning",
                title=title,
                content=content,
                confidence_score=1.0,  # Budget calculations are deterministic
                recommendations=[
                    "Review recent expenses in this category",
                    "Consider adjusting your budget allocation",
                    "Look for areas to reduce spending",
                ],
                related_entities={"budgets": [str(budget_id)]},
            ),
        )


class UserAlertData(BaseModel):
    """User alert event data payload."""

    alert_id: UUID = Field(default_factory=uuid4)
    user_id: UUID
    alert_type: str  # "budget", "insight", "goal", "system"
    title: str
    message: str
    action_url: Optional[str] = None
    action_label: Optional[str] = None
    is_read: bool = False
    delivered_via: List[str] = Field(default_factory=list)  # "in_app", "push", "email"

    class Config:
        json_encoders = {
            UUID: str,
        }


class UserAlertSentEvent(BaseEvent):
    """
    Event emitted when a user alert is sent.

    Topic: notifications
    Subscribers: Frontend WebSocket, Push Notification Service
    """

    type: EventType = Field(default=EventType.USER_ALERT_SENT)
    data: UserAlertData

    @classmethod
    def from_insight(
        cls,
        insight_event: AIInsightGeneratedEvent,
        delivery_channels: List[str] = None,
    ) -> "UserAlertSentEvent":
        """Create alert from an AI insight event."""
        return cls(
            subject=str(insight_event.data.user_id),
            correlationid=insight_event.id,
            data=UserAlertData(
                user_id=insight_event.data.user_id,
                alert_type="insight",
                title=insight_event.data.title,
                message=insight_event.data.content,
                delivered_via=delivery_channels or ["in_app"],
            ),
        )

    @classmethod
    def from_budget_exceeded(
        cls,
        budget_event: BudgetExceededEvent,
        delivery_channels: List[str] = None,
    ) -> "UserAlertSentEvent":
        """Create alert from a budget exceeded event."""
        return cls(
            subject=str(budget_event.data.user_id),
            correlationid=budget_event.id,
            data=UserAlertData(
                user_id=budget_event.data.user_id,
                alert_type="budget",
                title=f"Budget Alert: {budget_event.data.category_name or 'Overall'}",
                message=f"You've used {budget_event.data.percentage_used:.1f}% of your budget.",
                action_url=f"/budgets/{budget_event.data.budget_id}",
                action_label="View Budget",
                delivered_via=delivery_channels or ["in_app", "push"],
            ),
        )
