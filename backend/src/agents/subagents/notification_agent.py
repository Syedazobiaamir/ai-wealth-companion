"""
Phase V: Notification Agent for Event-Driven Delivery
AI Wealth Companion Cloud-Native System

This agent processes AI insights and budget alerts, transforming them
into user-facing notifications delivered via multiple channels.
"""

import logging
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
from uuid import UUID, uuid4

from src.events import (
    EventHandler,
    BudgetExceededEvent,
    AIInsightGeneratedEvent,
    UserAlertSentEvent,
    EventType,
    event_handler,
    publish_event,
)

logger = logging.getLogger(__name__)


class NotificationChannel(str, Enum):
    """Available notification delivery channels."""
    IN_APP = "in_app"
    PUSH = "push"
    EMAIL = "email"
    SMS = "sms"


class NotificationPriority(str, Enum):
    """Notification priority levels."""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"


class NotificationAgent(EventHandler):
    """
    Notification agent that delivers alerts to users.

    Subscribes to:
    - ai-insights: AI-generated insights and recommendations
    - budget-alerts: Budget threshold warnings and exceeded alerts

    Publishes to:
    - notifications: User alert delivery confirmations

    Delivers via:
    - In-app notifications (always)
    - Push notifications (for high/urgent priority)
    - Email (for daily digests or urgent alerts)
    """

    event_type = EventType.AI_INSIGHT_GENERATED
    use_idempotency = True
    processing_timeout = 15.0

    # Configuration
    PUSH_ENABLED = True
    EMAIL_ENABLED = False  # Requires email service configuration
    BATCH_NOTIFICATIONS = True
    BATCH_WINDOW_SECONDS = 60

    def __init__(self):
        super().__init__()
        # In-memory notification queue (production would use Redis)
        self._notification_queue: Dict[str, List[Dict[str, Any]]] = {}
        self._user_preferences: Dict[str, Dict[str, Any]] = {}

    async def handle(self, event: AIInsightGeneratedEvent) -> None:
        """
        Handle an ai.insight.generated event.

        Transforms the insight into a user notification and delivers
        it via appropriate channels based on priority.
        """
        logger.info(f"Notification agent processing insight {event.id}")

        user_id = event.data.user_id
        priority = self._map_priority(event.priority)

        # Create notification
        notification = await self._create_notification(
            user_id=user_id,
            title=event.data.title,
            message=event.data.content,
            alert_type="insight",
            priority=priority,
            correlation_id=event.id,
            metadata={
                "insight_type": event.data.insight_type,
                "recommendations": event.data.recommendations,
                "confidence": event.data.confidence_score,
            },
        )

        # Determine delivery channels based on priority
        channels = self._get_delivery_channels(priority)

        # Deliver notification
        await self._deliver_notification(notification, channels)

        # Publish delivery confirmation event
        await self._publish_alert_sent(notification, channels, event)

    async def handle_budget_alert(self, event: BudgetExceededEvent) -> None:
        """
        Handle a budget.exceeded event.

        Creates and delivers a budget alert notification.
        """
        logger.info(f"Notification agent processing budget alert {event.id}")

        user_id = event.data.user_id
        severity = event.severity

        # Map severity to priority
        priority_map = {
            "warning": NotificationPriority.NORMAL,
            "critical": NotificationPriority.HIGH,
            "exceeded": NotificationPriority.URGENT,
        }
        priority = priority_map.get(severity, NotificationPriority.NORMAL)

        # Create notification
        category_name = event.data.category_name or "Overall"
        notification = await self._create_notification(
            user_id=user_id,
            title=f"Budget Alert: {category_name}",
            message=self._format_budget_message(event),
            alert_type="budget",
            priority=priority,
            correlation_id=event.id,
            action_url=f"/budgets/{event.data.budget_id}",
            action_label="View Budget",
            metadata={
                "budget_id": str(event.data.budget_id),
                "category_id": str(event.data.category_id) if event.data.category_id else None,
                "percentage_used": event.data.percentage_used,
                "severity": severity,
            },
        )

        # Determine delivery channels (budget alerts get push notifications)
        channels = self._get_delivery_channels(priority)

        # Deliver notification
        await self._deliver_notification(notification, channels)

        # Publish delivery confirmation
        alert_event = UserAlertSentEvent.from_budget_exceeded(event, channels)
        await publish_event(alert_event, "notifications")

    def _format_budget_message(self, event: BudgetExceededEvent) -> str:
        """Format a human-readable budget alert message."""
        percentage = event.data.percentage_used
        category = event.data.category_name or "your overall budget"

        if percentage >= 100:
            return (
                f"You've exceeded {category} by ${event.data.exceeded_by:.2f}. "
                f"Total spent: ${event.data.spent_amount:.2f} of ${event.data.budget_amount:.2f} budget."
            )
        elif percentage >= 95:
            return (
                f"Critical: You've used {percentage:.0f}% of {category}. "
                f"Only ${event.data.budget_amount - event.data.spent_amount:.2f} remaining."
            )
        else:
            return (
                f"You've used {percentage:.0f}% of {category}. "
                f"${event.data.budget_amount - event.data.spent_amount:.2f} remaining this period."
            )

    def _map_priority(self, priority_str: str) -> NotificationPriority:
        """Map string priority to NotificationPriority enum."""
        priority_map = {
            "low": NotificationPriority.LOW,
            "normal": NotificationPriority.NORMAL,
            "high": NotificationPriority.HIGH,
            "urgent": NotificationPriority.URGENT,
        }
        return priority_map.get(priority_str, NotificationPriority.NORMAL)

    def _get_delivery_channels(
        self,
        priority: NotificationPriority,
    ) -> List[str]:
        """Determine which channels to use based on priority."""
        channels = [NotificationChannel.IN_APP.value]

        if priority in (NotificationPriority.HIGH, NotificationPriority.URGENT):
            if self.PUSH_ENABLED:
                channels.append(NotificationChannel.PUSH.value)

        if priority == NotificationPriority.URGENT and self.EMAIL_ENABLED:
            channels.append(NotificationChannel.EMAIL.value)

        return channels

    async def _create_notification(
        self,
        user_id: UUID,
        title: str,
        message: str,
        alert_type: str,
        priority: NotificationPriority,
        correlation_id: UUID = None,
        action_url: str = None,
        action_label: str = None,
        metadata: Dict[str, Any] = None,
    ) -> Dict[str, Any]:
        """Create a notification record."""
        notification = {
            "id": uuid4(),
            "user_id": user_id,
            "title": title,
            "message": message,
            "alert_type": alert_type,
            "priority": priority.value,
            "correlation_id": correlation_id,
            "action_url": action_url,
            "action_label": action_label,
            "metadata": metadata or {},
            "is_read": False,
            "created_at": datetime.utcnow(),
            "delivered_via": [],
        }

        return notification

    async def _deliver_notification(
        self,
        notification: Dict[str, Any],
        channels: List[str],
    ) -> None:
        """Deliver notification via specified channels."""
        delivered = []

        for channel in channels:
            try:
                if channel == NotificationChannel.IN_APP.value:
                    await self._deliver_in_app(notification)
                    delivered.append(channel)
                elif channel == NotificationChannel.PUSH.value:
                    await self._deliver_push(notification)
                    delivered.append(channel)
                elif channel == NotificationChannel.EMAIL.value:
                    await self._deliver_email(notification)
                    delivered.append(channel)
            except Exception as e:
                logger.error(f"Failed to deliver via {channel}: {e}")

        notification["delivered_via"] = delivered
        logger.info(
            f"Delivered notification {notification['id']} "
            f"to user {notification['user_id']} via {delivered}"
        )

    async def _deliver_in_app(self, notification: Dict[str, Any]) -> None:
        """Deliver notification to in-app notification center."""
        # In production, this would store in database and notify via WebSocket
        user_key = str(notification["user_id"])

        if user_key not in self._notification_queue:
            self._notification_queue[user_key] = []

        self._notification_queue[user_key].append(notification)

        # Limit queue size
        if len(self._notification_queue[user_key]) > 100:
            self._notification_queue[user_key] = self._notification_queue[user_key][-100:]

        logger.debug(f"Stored in-app notification for user {user_key}")

    async def _deliver_push(self, notification: Dict[str, Any]) -> None:
        """Deliver push notification."""
        # In production, this would use Firebase Cloud Messaging or similar
        logger.info(
            f"[PUSH] {notification['title']}: {notification['message'][:50]}... "
            f"to user {notification['user_id']}"
        )

    async def _deliver_email(self, notification: Dict[str, Any]) -> None:
        """Deliver email notification."""
        # In production, this would use SendGrid, AWS SES, or similar
        logger.info(
            f"[EMAIL] {notification['title']} to user {notification['user_id']}"
        )

    async def _publish_alert_sent(
        self,
        notification: Dict[str, Any],
        channels: List[str],
        source_event: AIInsightGeneratedEvent,
    ) -> None:
        """Publish a user.alert.sent confirmation event."""
        try:
            alert = UserAlertSentEvent.from_insight(source_event, channels)
            await publish_event(alert, "notifications")
            logger.debug(f"Published alert.sent event for notification {notification['id']}")
        except Exception as e:
            logger.error(f"Failed to publish alert.sent event: {e}")

    def get_user_notifications(
        self,
        user_id: UUID,
        limit: int = 20,
    ) -> List[Dict[str, Any]]:
        """Get notifications for a user (for API access)."""
        user_key = str(user_id)
        notifications = self._notification_queue.get(user_key, [])
        return sorted(
            notifications,
            key=lambda n: n["created_at"],
            reverse=True,
        )[:limit]

    def mark_as_read(self, user_id: UUID, notification_id: UUID) -> bool:
        """Mark a notification as read."""
        user_key = str(user_id)
        notifications = self._notification_queue.get(user_key, [])

        for notification in notifications:
            if notification["id"] == notification_id:
                notification["is_read"] = True
                return True

        return False


# Register the notification agent as event handlers
@event_handler("ai-insights", AIInsightGeneratedEvent)
async def handle_ai_insight(event: AIInsightGeneratedEvent) -> None:
    """Handle ai.insight.generated events."""
    agent = NotificationAgent()
    await agent.handle(event)


@event_handler("budget-alerts", BudgetExceededEvent)
async def handle_budget_alert(event: BudgetExceededEvent) -> None:
    """Handle budget.exceeded events."""
    agent = NotificationAgent()
    await agent.handle_budget_alert(event)
