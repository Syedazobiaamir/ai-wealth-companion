"""
Phase V: Event Publisher Module
AI Wealth Companion Cloud-Native Events

Provides event publishing capabilities using Dapr pub/sub component.
Supports both synchronous and asynchronous publishing with retry logic.
"""

import asyncio
import logging
from typing import Any, Dict, Optional
from uuid import UUID

import httpx

from .schemas import (
    BaseEvent,
    TransactionCreatedEvent,
    TransactionUpdatedEvent,
    BudgetExceededEvent,
    AIInsightGeneratedEvent,
    UserAlertSentEvent,
    EventType,
)

logger = logging.getLogger(__name__)


class EventPublisher:
    """
    Event publisher using Dapr pub/sub.

    This class provides methods to publish events to Kafka topics via Dapr sidecar.
    It includes retry logic, error handling, and optional async batch publishing.
    """

    # Dapr sidecar configuration
    DAPR_HTTP_PORT = 3500
    DAPR_PUBSUB_NAME = "pubsub"

    # Topic mapping
    TOPIC_MAPPING = {
        EventType.TRANSACTION_CREATED: "transactions",
        EventType.TRANSACTION_UPDATED: "transactions",
        EventType.TRANSACTION_DELETED: "transactions",
        EventType.BUDGET_EXCEEDED: "budget-alerts",
        EventType.BUDGET_WARNING: "budget-alerts",
        EventType.BUDGET_CREATED: "budget-alerts",
        EventType.BUDGET_UPDATED: "budget-alerts",
        EventType.AI_INSIGHT_GENERATED: "ai-insights",
        EventType.AI_ANALYSIS_COMPLETED: "ai-insights",
        EventType.USER_ALERT_SENT: "notifications",
        EventType.USER_NOTIFICATION_DELIVERED: "notifications",
        EventType.GOAL_PROGRESS_UPDATED: "notifications",
        EventType.GOAL_ACHIEVED: "notifications",
    }

    def __init__(
        self,
        dapr_host: str = "localhost",
        dapr_port: int = None,
        pubsub_name: str = None,
        max_retries: int = 3,
        retry_delay: float = 0.5,
    ):
        """
        Initialize the event publisher.

        Args:
            dapr_host: Dapr sidecar host (default: localhost)
            dapr_port: Dapr sidecar HTTP port (default: 3500)
            pubsub_name: Dapr pub/sub component name (default: pubsub)
            max_retries: Maximum retry attempts on failure
            retry_delay: Base delay between retries (exponential backoff)
        """
        self.dapr_host = dapr_host
        self.dapr_port = dapr_port or self.DAPR_HTTP_PORT
        self.pubsub_name = pubsub_name or self.DAPR_PUBSUB_NAME
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self._client: Optional[httpx.AsyncClient] = None

    @property
    def base_url(self) -> str:
        """Get the Dapr sidecar base URL."""
        return f"http://{self.dapr_host}:{self.dapr_port}"

    @property
    def publish_url(self) -> str:
        """Get the Dapr publish endpoint URL."""
        return f"{self.base_url}/v1.0/publish/{self.pubsub_name}"

    async def _get_client(self) -> httpx.AsyncClient:
        """Get or create an async HTTP client."""
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(timeout=30.0)
        return self._client

    async def close(self):
        """Close the HTTP client."""
        if self._client and not self._client.is_closed:
            await self._client.aclose()
            self._client = None

    def _get_topic(self, event: BaseEvent) -> str:
        """Get the topic for an event type."""
        return self.TOPIC_MAPPING.get(event.type, "default")

    async def publish(
        self,
        event: BaseEvent,
        topic: Optional[str] = None,
        metadata: Optional[Dict[str, str]] = None,
    ) -> bool:
        """
        Publish an event to Dapr pub/sub.

        Args:
            event: The event to publish
            topic: Optional topic override (uses event type mapping if not specified)
            metadata: Optional Dapr metadata headers

        Returns:
            True if published successfully, False otherwise

        Raises:
            Exception on fatal errors after retries exhausted
        """
        topic = topic or self._get_topic(event)
        url = f"{self.publish_url}/{topic}"

        # Prepare event payload
        payload = event.model_dump(mode="json")

        # Prepare headers
        headers = {
            "Content-Type": "application/cloudevents+json",
        }
        if metadata:
            for key, value in metadata.items():
                headers[f"metadata.{key}"] = value

        # Retry loop with exponential backoff
        client = await self._get_client()
        last_error = None

        for attempt in range(self.max_retries):
            try:
                response = await client.post(url, json=payload, headers=headers)

                if response.status_code in (200, 204):
                    logger.info(
                        f"Published event {event.id} to topic '{topic}' "
                        f"(type: {event.type}, attempt: {attempt + 1})"
                    )
                    return True

                logger.warning(
                    f"Failed to publish event {event.id}: "
                    f"status={response.status_code}, body={response.text}"
                )
                last_error = Exception(f"HTTP {response.status_code}: {response.text}")

            except httpx.RequestError as e:
                logger.warning(
                    f"Request error publishing event {event.id} "
                    f"(attempt {attempt + 1}/{self.max_retries}): {e}"
                )
                last_error = e

            # Exponential backoff
            if attempt < self.max_retries - 1:
                delay = self.retry_delay * (2**attempt)
                await asyncio.sleep(delay)

        logger.error(f"Failed to publish event {event.id} after {self.max_retries} attempts")
        raise last_error or Exception("Unknown error publishing event")

    async def publish_batch(
        self,
        events: list[BaseEvent],
        topic: Optional[str] = None,
    ) -> Dict[UUID, bool]:
        """
        Publish multiple events concurrently.

        Args:
            events: List of events to publish
            topic: Optional topic override for all events

        Returns:
            Dict mapping event IDs to publish success status
        """
        results = {}
        tasks = []

        for event in events:
            task = asyncio.create_task(self._publish_with_result(event, topic))
            tasks.append((event.id, task))

        for event_id, task in tasks:
            try:
                results[event_id] = await task
            except Exception as e:
                logger.error(f"Batch publish failed for event {event_id}: {e}")
                results[event_id] = False

        return results

    async def _publish_with_result(
        self,
        event: BaseEvent,
        topic: Optional[str] = None,
    ) -> bool:
        """Publish event and return success status."""
        try:
            return await self.publish(event, topic)
        except Exception:
            return False

    # Convenience methods for specific event types

    async def publish_transaction_created(
        self,
        event: TransactionCreatedEvent,
    ) -> bool:
        """Publish a transaction created event."""
        return await self.publish(event, "transactions")

    async def publish_transaction_updated(
        self,
        event: TransactionUpdatedEvent,
    ) -> bool:
        """Publish a transaction updated event."""
        return await self.publish(event, "transactions")

    async def publish_budget_exceeded(
        self,
        event: BudgetExceededEvent,
    ) -> bool:
        """Publish a budget exceeded event."""
        return await self.publish(event, "budget-alerts")

    async def publish_ai_insight(
        self,
        event: AIInsightGeneratedEvent,
    ) -> bool:
        """Publish an AI insight generated event."""
        return await self.publish(event, "ai-insights")

    async def publish_user_alert(
        self,
        event: UserAlertSentEvent,
    ) -> bool:
        """Publish a user alert sent event."""
        return await self.publish(event, "notifications")


# Singleton publisher instance
_publisher: Optional[EventPublisher] = None


def get_event_publisher() -> EventPublisher:
    """Get the singleton event publisher instance."""
    global _publisher
    if _publisher is None:
        _publisher = EventPublisher()
    return _publisher


async def publish_event(event: BaseEvent, topic: Optional[str] = None) -> bool:
    """Convenience function to publish an event using the singleton publisher."""
    publisher = get_event_publisher()
    return await publisher.publish(event, topic)
