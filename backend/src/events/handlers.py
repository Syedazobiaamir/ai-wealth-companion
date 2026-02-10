"""
Phase V: Event Handler Module
AI Wealth Companion Cloud-Native Events

Provides base event handler infrastructure for processing events
received via Dapr pub/sub subscriptions.
"""

import asyncio
import logging
from abc import ABC, abstractmethod
from datetime import datetime
from functools import wraps
from typing import Any, Callable, Dict, List, Optional, Type, TypeVar

from fastapi import APIRouter, Request, Response
from pydantic import ValidationError

from .schemas import (
    BaseEvent,
    EventType,
    TransactionCreatedEvent,
    TransactionUpdatedEvent,
    BudgetExceededEvent,
    AIInsightGeneratedEvent,
    UserAlertSentEvent,
)
from .idempotency import IdempotencyMiddleware, get_idempotency_middleware

logger = logging.getLogger(__name__)

# Type variable for event handlers
E = TypeVar("E", bound=BaseEvent)


class EventHandler(ABC):
    """
    Abstract base class for event handlers.

    Subclasses should implement the handle method to process specific event types.
    Handlers are automatically registered with the event router.
    """

    # Event type this handler processes
    event_type: EventType

    # Whether to use idempotency checking
    use_idempotency: bool = True

    # Timeout for event processing (seconds)
    processing_timeout: float = 30.0

    def __init__(self):
        """Initialize the event handler."""
        self.idempotency = get_idempotency_middleware() if self.use_idempotency else None
        self._metrics = {
            "processed": 0,
            "failed": 0,
            "duplicates": 0,
        }

    @abstractmethod
    async def handle(self, event: BaseEvent) -> None:
        """
        Handle the event.

        Args:
            event: The event to process

        Raises:
            Exception on processing failure (will trigger retry)
        """
        pass

    async def process(self, event: BaseEvent) -> bool:
        """
        Process an event with idempotency and error handling.

        Args:
            event: The event to process

        Returns:
            True if processed successfully or was a duplicate
        """
        event_id = str(event.id)

        # Check for duplicate processing
        if self.idempotency:
            is_processed = await self.idempotency.is_processed(event_id)
            if is_processed:
                logger.info(f"Skipping duplicate event {event_id}")
                self._metrics["duplicates"] += 1
                return True

        try:
            # Process with timeout
            await asyncio.wait_for(
                self.handle(event),
                timeout=self.processing_timeout,
            )

            # Mark as processed
            if self.idempotency:
                await self.idempotency.mark_processed(event_id)

            self._metrics["processed"] += 1
            logger.info(f"Successfully processed event {event_id} (type: {event.type})")
            return True

        except asyncio.TimeoutError:
            logger.error(f"Timeout processing event {event_id}")
            self._metrics["failed"] += 1
            raise

        except Exception as e:
            logger.error(f"Error processing event {event_id}: {e}")
            self._metrics["failed"] += 1
            raise

    def get_metrics(self) -> Dict[str, int]:
        """Get handler metrics."""
        return self._metrics.copy()


# Handler registry
_handlers: Dict[str, List[EventHandler]] = {}


def register_handler(topic: str, handler: EventHandler) -> None:
    """Register an event handler for a topic."""
    if topic not in _handlers:
        _handlers[topic] = []
    _handlers[topic].append(handler)
    logger.info(f"Registered handler {handler.__class__.__name__} for topic '{topic}'")


def get_handlers(topic: str) -> List[EventHandler]:
    """Get all handlers registered for a topic."""
    return _handlers.get(topic, [])


def event_handler(
    topic: str,
    event_class: Type[BaseEvent],
    use_idempotency: bool = True,
):
    """
    Decorator to register a function as an event handler.

    Usage:
        @event_handler("transactions", TransactionCreatedEvent)
        async def handle_transaction(event: TransactionCreatedEvent):
            # Process event
            pass
    """

    def decorator(func: Callable[[BaseEvent], Any]):
        @wraps(func)
        async def wrapper(event: BaseEvent) -> Any:
            return await func(event)

        # Create a handler class dynamically
        class DynamicHandler(EventHandler):
            event_type = event_class.__fields__.get("type", {}).get("default")
            use_idempotency = use_idempotency

            async def handle(self, event: BaseEvent) -> None:
                await func(event)

        # Register the handler
        handler_instance = DynamicHandler()
        register_handler(topic, handler_instance)

        return wrapper

    return decorator


def create_event_router() -> APIRouter:
    """
    Create a FastAPI router for Dapr event subscriptions.

    Returns an APIRouter with endpoints for:
    - GET /dapr/subscribe - Returns subscription configuration
    - POST /events/{topic} - Receives events from Dapr pub/sub
    """
    router = APIRouter(tags=["events"])

    # Event type mapping
    EVENT_CLASSES: Dict[str, Type[BaseEvent]] = {
        "transaction.created": TransactionCreatedEvent,
        "transaction.updated": TransactionUpdatedEvent,
        "budget.exceeded": BudgetExceededEvent,
        "ai.insight.generated": AIInsightGeneratedEvent,
        "user.alert.sent": UserAlertSentEvent,
    }

    @router.get("/dapr/subscribe")
    async def subscribe():
        """
        Return Dapr subscription configuration.

        Dapr calls this endpoint to discover topic subscriptions.
        """
        subscriptions = []

        for topic in _handlers.keys():
            subscriptions.append({
                "pubsubname": "pubsub",
                "topic": topic,
                "route": f"/events/{topic}",
                "metadata": {
                    "deadLetterTopic": "dead-letter",
                },
            })

        return subscriptions

    @router.post("/events/{topic}")
    async def receive_event(topic: str, request: Request):
        """
        Receive and process events from Dapr pub/sub.

        Args:
            topic: The topic the event was published to
            request: The FastAPI request containing the event

        Returns:
            {"status": "SUCCESS"} on success
            {"status": "RETRY"} on retryable failure
            {"status": "DROP"} on non-retryable failure
        """
        handlers = get_handlers(topic)

        if not handlers:
            logger.warning(f"No handlers registered for topic '{topic}'")
            return Response(status_code=200)

        try:
            body = await request.json()
            logger.debug(f"Received event on topic '{topic}': {body}")

            # Parse CloudEvents envelope
            event_type = body.get("type")
            event_class = EVENT_CLASSES.get(event_type, BaseEvent)

            try:
                event = event_class.model_validate(body)
            except ValidationError as e:
                logger.error(f"Event validation failed: {e}")
                return {"status": "DROP"}

            # Process with all registered handlers
            success = True
            for handler in handlers:
                try:
                    await handler.process(event)
                except Exception as e:
                    logger.error(f"Handler {handler.__class__.__name__} failed: {e}")
                    success = False

            return {"status": "SUCCESS" if success else "RETRY"}

        except Exception as e:
            logger.error(f"Error processing event: {e}")
            return {"status": "RETRY"}

    @router.post("/events/dead-letter")
    async def receive_dead_letter(request: Request):
        """
        Receive events from the dead letter queue.

        These are events that failed processing after all retries.
        They should be logged and potentially trigger alerts.
        """
        try:
            body = await request.json()
            logger.error(f"Dead letter event received: {body}")

            # TODO: Store in database for manual review
            # TODO: Send alert to operations team

            return {"status": "SUCCESS"}

        except Exception as e:
            logger.error(f"Error processing dead letter: {e}")
            return {"status": "DROP"}

    return router


# Default event router instance
event_router = create_event_router()
