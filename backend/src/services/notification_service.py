"""
Phase V: Notification Service for In-App Delivery
AI Wealth Companion Cloud-Native System

This service manages user notifications, including storage, retrieval,
and real-time delivery via WebSocket connections.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Any, Callable, Dict, List, Optional, Set
from uuid import UUID, uuid4

from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class NotificationCreate(BaseModel):
    """Schema for creating a new notification."""
    title: str
    message: str
    alert_type: str = "general"  # budget, insight, goal, system
    priority: str = "normal"  # low, normal, high, urgent
    action_url: Optional[str] = None
    action_label: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    expires_at: Optional[datetime] = None


class NotificationRead(BaseModel):
    """Schema for reading a notification."""
    id: UUID
    user_id: UUID
    title: str
    message: str
    alert_type: str
    priority: str
    action_url: Optional[str] = None
    action_label: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    is_read: bool = False
    is_archived: bool = False
    created_at: datetime
    read_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class NotificationService:
    """
    Service for managing user notifications.

    Provides:
    - In-memory storage (production would use database)
    - Real-time delivery via WebSocket callbacks
    - Notification lifecycle management (read, archive, delete)
    - Batch operations and filtering
    """

    # Configuration
    MAX_NOTIFICATIONS_PER_USER = 500
    DEFAULT_EXPIRY_DAYS = 30
    CLEANUP_INTERVAL_SECONDS = 3600  # 1 hour

    def __init__(self):
        # In-memory storage: user_id -> list of notifications
        self._notifications: Dict[str, List[Dict[str, Any]]] = {}
        # WebSocket subscribers: user_id -> set of callback functions
        self._subscribers: Dict[str, Set[Callable]] = {}
        # Unread counts cache
        self._unread_counts: Dict[str, int] = {}
        # Cleanup task
        self._cleanup_task: Optional[asyncio.Task] = None

    async def start(self) -> None:
        """Start the notification service background tasks."""
        if self._cleanup_task is None:
            self._cleanup_task = asyncio.create_task(self._cleanup_loop())
            logger.info("Notification service started")

    async def stop(self) -> None:
        """Stop the notification service background tasks."""
        if self._cleanup_task:
            self._cleanup_task.cancel()
            try:
                await self._cleanup_task
            except asyncio.CancelledError:
                pass
            self._cleanup_task = None
            logger.info("Notification service stopped")

    async def _cleanup_loop(self) -> None:
        """Background task to clean up expired notifications."""
        while True:
            try:
                await asyncio.sleep(self.CLEANUP_INTERVAL_SECONDS)
                await self._cleanup_expired()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in cleanup loop: {e}")

    async def _cleanup_expired(self) -> None:
        """Remove expired notifications."""
        now = datetime.utcnow()
        total_removed = 0

        for user_id, notifications in self._notifications.items():
            before_count = len(notifications)
            self._notifications[user_id] = [
                n for n in notifications
                if not n.get("expires_at") or n["expires_at"] > now
            ]
            removed = before_count - len(self._notifications[user_id])
            if removed > 0:
                total_removed += removed
                self._update_unread_count(user_id)

        if total_removed > 0:
            logger.info(f"Cleaned up {total_removed} expired notifications")

    async def create(
        self,
        user_id: UUID,
        data: NotificationCreate,
    ) -> NotificationRead:
        """
        Create a new notification for a user.

        Args:
            user_id: The user to notify
            data: Notification data

        Returns:
            The created notification
        """
        user_key = str(user_id)

        # Initialize user's notification list if needed
        if user_key not in self._notifications:
            self._notifications[user_key] = []

        # Create notification
        notification = {
            "id": uuid4(),
            "user_id": user_id,
            "title": data.title,
            "message": data.message,
            "alert_type": data.alert_type,
            "priority": data.priority,
            "action_url": data.action_url,
            "action_label": data.action_label,
            "metadata": data.metadata,
            "is_read": False,
            "is_archived": False,
            "created_at": datetime.utcnow(),
            "read_at": None,
            "expires_at": data.expires_at or (
                datetime.utcnow() + timedelta(days=self.DEFAULT_EXPIRY_DAYS)
            ),
        }

        # Add to list (newest first)
        self._notifications[user_key].insert(0, notification)

        # Enforce max limit
        if len(self._notifications[user_key]) > self.MAX_NOTIFICATIONS_PER_USER:
            self._notifications[user_key] = self._notifications[user_key][
                :self.MAX_NOTIFICATIONS_PER_USER
            ]

        # Update unread count
        self._update_unread_count(user_key)

        # Notify real-time subscribers
        await self._notify_subscribers(user_key, "new", notification)

        logger.info(f"Created notification {notification['id']} for user {user_id}")
        return NotificationRead(**notification)

    async def get_all(
        self,
        user_id: UUID,
        include_read: bool = True,
        include_archived: bool = False,
        alert_type: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> List[NotificationRead]:
        """
        Get notifications for a user with filtering.

        Args:
            user_id: The user ID
            include_read: Include read notifications
            include_archived: Include archived notifications
            alert_type: Filter by alert type
            limit: Maximum number to return
            offset: Number to skip

        Returns:
            List of notifications
        """
        user_key = str(user_id)
        notifications = self._notifications.get(user_key, [])

        # Apply filters
        filtered = []
        for n in notifications:
            if not include_read and n["is_read"]:
                continue
            if not include_archived and n["is_archived"]:
                continue
            if alert_type and n["alert_type"] != alert_type:
                continue
            filtered.append(n)

        # Apply pagination
        paginated = filtered[offset:offset + limit]

        return [NotificationRead(**n) for n in paginated]

    async def get_by_id(
        self,
        user_id: UUID,
        notification_id: UUID,
    ) -> Optional[NotificationRead]:
        """Get a specific notification."""
        user_key = str(user_id)
        notifications = self._notifications.get(user_key, [])

        for n in notifications:
            if n["id"] == notification_id:
                return NotificationRead(**n)

        return None

    async def mark_as_read(
        self,
        user_id: UUID,
        notification_id: UUID,
    ) -> bool:
        """Mark a notification as read."""
        user_key = str(user_id)
        notifications = self._notifications.get(user_key, [])

        for n in notifications:
            if n["id"] == notification_id and not n["is_read"]:
                n["is_read"] = True
                n["read_at"] = datetime.utcnow()
                self._update_unread_count(user_key)
                await self._notify_subscribers(user_key, "read", n)
                return True

        return False

    async def mark_all_as_read(self, user_id: UUID) -> int:
        """Mark all notifications as read for a user."""
        user_key = str(user_id)
        notifications = self._notifications.get(user_key, [])
        count = 0

        now = datetime.utcnow()
        for n in notifications:
            if not n["is_read"]:
                n["is_read"] = True
                n["read_at"] = now
                count += 1

        if count > 0:
            self._update_unread_count(user_key)
            await self._notify_subscribers(user_key, "read_all", {"count": count})

        return count

    async def archive(
        self,
        user_id: UUID,
        notification_id: UUID,
    ) -> bool:
        """Archive a notification."""
        user_key = str(user_id)
        notifications = self._notifications.get(user_key, [])

        for n in notifications:
            if n["id"] == notification_id:
                n["is_archived"] = True
                if not n["is_read"]:
                    n["is_read"] = True
                    n["read_at"] = datetime.utcnow()
                self._update_unread_count(user_key)
                await self._notify_subscribers(user_key, "archived", n)
                return True

        return False

    async def delete(
        self,
        user_id: UUID,
        notification_id: UUID,
    ) -> bool:
        """Delete a notification."""
        user_key = str(user_id)
        notifications = self._notifications.get(user_key, [])

        for i, n in enumerate(notifications):
            if n["id"] == notification_id:
                del notifications[i]
                self._update_unread_count(user_key)
                await self._notify_subscribers(user_key, "deleted", {"id": notification_id})
                return True

        return False

    def get_unread_count(self, user_id: UUID) -> int:
        """Get the unread notification count for a user."""
        user_key = str(user_id)
        return self._unread_counts.get(user_key, 0)

    def _update_unread_count(self, user_key: str) -> None:
        """Update the cached unread count for a user."""
        notifications = self._notifications.get(user_key, [])
        self._unread_counts[user_key] = sum(
            1 for n in notifications
            if not n["is_read"] and not n["is_archived"]
        )

    # Real-time subscription methods

    def subscribe(
        self,
        user_id: UUID,
        callback: Callable[[str, Dict[str, Any]], None],
    ) -> None:
        """
        Subscribe to real-time notification updates for a user.

        Args:
            user_id: The user ID
            callback: Function to call with (event_type, data)
        """
        user_key = str(user_id)
        if user_key not in self._subscribers:
            self._subscribers[user_key] = set()
        self._subscribers[user_key].add(callback)
        logger.debug(f"Added subscriber for user {user_id}")

    def unsubscribe(
        self,
        user_id: UUID,
        callback: Callable[[str, Dict[str, Any]], None],
    ) -> None:
        """Unsubscribe from real-time notification updates."""
        user_key = str(user_id)
        if user_key in self._subscribers:
            self._subscribers[user_key].discard(callback)
            if not self._subscribers[user_key]:
                del self._subscribers[user_key]
            logger.debug(f"Removed subscriber for user {user_id}")

    async def _notify_subscribers(
        self,
        user_key: str,
        event_type: str,
        data: Dict[str, Any],
    ) -> None:
        """Notify all subscribers for a user of an event."""
        subscribers = self._subscribers.get(user_key, set())
        if not subscribers:
            return

        # Serialize notification data
        serialized = {
            k: str(v) if isinstance(v, (UUID, datetime)) else v
            for k, v in data.items()
        }

        for callback in subscribers.copy():
            try:
                if asyncio.iscoroutinefunction(callback):
                    await callback(event_type, serialized)
                else:
                    callback(event_type, serialized)
            except Exception as e:
                logger.error(f"Error notifying subscriber: {e}")

    # Batch operations

    async def create_batch(
        self,
        notifications: List[tuple[UUID, NotificationCreate]],
    ) -> List[NotificationRead]:
        """Create multiple notifications in batch."""
        results = []
        for user_id, data in notifications:
            result = await self.create(user_id, data)
            results.append(result)
        return results

    async def delete_all_for_user(self, user_id: UUID) -> int:
        """Delete all notifications for a user."""
        user_key = str(user_id)
        count = len(self._notifications.get(user_key, []))
        self._notifications[user_key] = []
        self._unread_counts[user_key] = 0
        await self._notify_subscribers(user_key, "deleted_all", {"count": count})
        return count


# Singleton instance
_service: Optional[NotificationService] = None


def get_notification_service() -> NotificationService:
    """Get the singleton notification service instance."""
    global _service
    if _service is None:
        _service = NotificationService()
    return _service
