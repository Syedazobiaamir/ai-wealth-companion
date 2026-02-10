"""
Phase V: Event-Driven Architecture Module
AI Wealth Companion Cloud-Native Events

This module provides event-driven capabilities using Dapr pub/sub
for real-time financial event processing.
"""

from .schemas import (
    BaseEvent,
    EventType,
    TransactionData,
    TransactionCreatedEvent,
    TransactionUpdatedEvent,
    BudgetExceededData,
    BudgetExceededEvent,
    AIInsightData,
    AIInsightGeneratedEvent,
    UserAlertData,
    UserAlertSentEvent,
)
from .publishers import EventPublisher, publish_event, get_event_publisher
from .handlers import EventHandler, event_handler, event_router, create_event_router
from .idempotency import IdempotencyMiddleware, idempotent, get_idempotency_middleware

__all__ = [
    # Event Types
    "EventType",
    # Base
    "BaseEvent",
    # Transaction Events
    "TransactionData",
    "TransactionCreatedEvent",
    "TransactionUpdatedEvent",
    # Budget Events
    "BudgetExceededData",
    "BudgetExceededEvent",
    # AI Events
    "AIInsightData",
    "AIInsightGeneratedEvent",
    # User Events
    "UserAlertData",
    "UserAlertSentEvent",
    # Publishers
    "EventPublisher",
    "publish_event",
    "get_event_publisher",
    # Handlers
    "EventHandler",
    "event_handler",
    "event_router",
    "create_event_router",
    # Idempotency
    "IdempotencyMiddleware",
    "idempotent",
    "get_idempotency_middleware",
]
