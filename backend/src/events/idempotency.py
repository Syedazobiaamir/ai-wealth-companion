"""
Phase V: Idempotency Middleware Module
AI Wealth Companion Cloud-Native Events

Provides idempotency checking to prevent duplicate event processing.
Uses Redis (via Dapr state store) for distributed deduplication.
"""

import asyncio
import hashlib
import logging
from datetime import datetime, timedelta
from functools import wraps
from typing import Any, Callable, Dict, Optional, Set

import httpx

logger = logging.getLogger(__name__)


class IdempotencyMiddleware:
    """
    Idempotency middleware for event deduplication.

    Uses Dapr state store (Redis) to track processed event IDs,
    ensuring each event is processed exactly once across all replicas.
    """

    # Dapr sidecar configuration
    DAPR_HTTP_PORT = 3500
    DAPR_STATESTORE_NAME = "statestore"

    # Default TTL for idempotency keys (24 hours)
    DEFAULT_TTL_HOURS = 24

    # Local cache for performance
    LOCAL_CACHE_SIZE = 10000
    LOCAL_CACHE_TTL_SECONDS = 300  # 5 minutes

    def __init__(
        self,
        dapr_host: str = "localhost",
        dapr_port: int = None,
        statestore_name: str = None,
        ttl_hours: int = None,
        use_local_cache: bool = True,
    ):
        """
        Initialize the idempotency middleware.

        Args:
            dapr_host: Dapr sidecar host
            dapr_port: Dapr sidecar HTTP port
            statestore_name: Dapr state store component name
            ttl_hours: TTL for idempotency keys in hours
            use_local_cache: Whether to use local cache for performance
        """
        self.dapr_host = dapr_host
        self.dapr_port = dapr_port or self.DAPR_HTTP_PORT
        self.statestore_name = statestore_name or self.DAPR_STATESTORE_NAME
        self.ttl_hours = ttl_hours or self.DEFAULT_TTL_HOURS
        self.use_local_cache = use_local_cache

        # Local cache: event_id -> expiry_time
        self._local_cache: Dict[str, datetime] = {}
        self._cache_lock = asyncio.Lock()
        self._client: Optional[httpx.AsyncClient] = None

    @property
    def base_url(self) -> str:
        """Get the Dapr sidecar base URL."""
        return f"http://{self.dapr_host}:{self.dapr_port}"

    @property
    def state_url(self) -> str:
        """Get the Dapr state store endpoint URL."""
        return f"{self.base_url}/v1.0/state/{self.statestore_name}"

    async def _get_client(self) -> httpx.AsyncClient:
        """Get or create an async HTTP client."""
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(timeout=10.0)
        return self._client

    async def close(self):
        """Close the HTTP client."""
        if self._client and not self._client.is_closed:
            await self._client.aclose()
            self._client = None

    def _get_key(self, event_id: str) -> str:
        """Generate a unique key for the event ID."""
        return f"idempotency:{event_id}"

    async def _check_local_cache(self, event_id: str) -> Optional[bool]:
        """
        Check the local cache for the event ID.

        Returns:
            True if event was processed (cache hit)
            None if not in cache or expired
        """
        if not self.use_local_cache:
            return None

        async with self._cache_lock:
            expiry = self._local_cache.get(event_id)
            if expiry and expiry > datetime.utcnow():
                return True

            # Clean up expired entry
            if event_id in self._local_cache:
                del self._local_cache[event_id]

            return None

    async def _update_local_cache(self, event_id: str) -> None:
        """Update the local cache with the event ID."""
        if not self.use_local_cache:
            return

        async with self._cache_lock:
            # Evict oldest entries if cache is full
            if len(self._local_cache) >= self.LOCAL_CACHE_SIZE:
                now = datetime.utcnow()
                # Remove expired entries
                expired = [
                    k for k, v in self._local_cache.items() if v <= now
                ]
                for k in expired[:len(expired) // 2 + 1]:  # Remove at least half
                    del self._local_cache[k]

            # Add new entry
            expiry = datetime.utcnow() + timedelta(seconds=self.LOCAL_CACHE_TTL_SECONDS)
            self._local_cache[event_id] = expiry

    async def is_processed(self, event_id: str) -> bool:
        """
        Check if an event has already been processed.

        Args:
            event_id: The unique event identifier

        Returns:
            True if the event was already processed, False otherwise
        """
        # Check local cache first
        cached = await self._check_local_cache(event_id)
        if cached is True:
            logger.debug(f"Event {event_id} found in local cache")
            return True

        # Check Dapr state store
        key = self._get_key(event_id)
        url = f"{self.state_url}/{key}"

        try:
            client = await self._get_client()
            response = await client.get(url)

            if response.status_code == 200 and response.text:
                logger.debug(f"Event {event_id} found in state store")
                await self._update_local_cache(event_id)
                return True

            return False

        except httpx.RequestError as e:
            logger.warning(f"Error checking idempotency for {event_id}: {e}")
            # On network error, assume not processed to avoid data loss
            return False

    async def mark_processed(
        self,
        event_id: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> bool:
        """
        Mark an event as processed.

        Args:
            event_id: The unique event identifier
            metadata: Optional metadata to store with the record

        Returns:
            True if marked successfully, False otherwise
        """
        key = self._get_key(event_id)
        ttl_seconds = self.ttl_hours * 3600

        # Prepare state value
        value = {
            "event_id": event_id,
            "processed_at": datetime.utcnow().isoformat(),
            "metadata": metadata or {},
        }

        # Store in Dapr state store
        payload = [
            {
                "key": key,
                "value": value,
                "options": {
                    "ttlInSeconds": ttl_seconds,
                },
            }
        ]

        try:
            client = await self._get_client()
            response = await client.post(self.state_url, json=payload)

            if response.status_code in (200, 204):
                await self._update_local_cache(event_id)
                logger.debug(f"Marked event {event_id} as processed")
                return True

            logger.warning(
                f"Failed to mark event {event_id} as processed: "
                f"status={response.status_code}"
            )
            return False

        except httpx.RequestError as e:
            logger.error(f"Error marking event {event_id} as processed: {e}")
            return False

    async def remove(self, event_id: str) -> bool:
        """
        Remove an event from the processed set.

        This is useful for retrying events that need reprocessing.

        Args:
            event_id: The unique event identifier

        Returns:
            True if removed successfully, False otherwise
        """
        key = self._get_key(event_id)
        url = f"{self.state_url}/{key}"

        try:
            client = await self._get_client()
            response = await client.delete(url)

            if response.status_code in (200, 204):
                # Remove from local cache
                async with self._cache_lock:
                    self._local_cache.pop(event_id, None)

                logger.debug(f"Removed event {event_id} from processed set")
                return True

            return False

        except httpx.RequestError as e:
            logger.error(f"Error removing event {event_id}: {e}")
            return False

    def get_cache_stats(self) -> Dict[str, int]:
        """Get local cache statistics."""
        now = datetime.utcnow()
        valid_entries = sum(1 for v in self._local_cache.values() if v > now)
        return {
            "total_entries": len(self._local_cache),
            "valid_entries": valid_entries,
            "expired_entries": len(self._local_cache) - valid_entries,
        }


# In-memory fallback for development/testing
class InMemoryIdempotencyMiddleware(IdempotencyMiddleware):
    """
    In-memory idempotency middleware for development/testing.

    Uses a local set instead of Dapr state store.
    Not suitable for production with multiple replicas.
    """

    def __init__(self, ttl_hours: int = 24):
        super().__init__(use_local_cache=True, ttl_hours=ttl_hours)
        self._processed: Dict[str, datetime] = {}

    async def is_processed(self, event_id: str) -> bool:
        expiry = self._processed.get(event_id)
        if expiry and expiry > datetime.utcnow():
            return True
        return False

    async def mark_processed(
        self,
        event_id: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> bool:
        expiry = datetime.utcnow() + timedelta(hours=self.ttl_hours)
        self._processed[event_id] = expiry
        return True

    async def remove(self, event_id: str) -> bool:
        self._processed.pop(event_id, None)
        return True


# Singleton instance
_middleware: Optional[IdempotencyMiddleware] = None


def get_idempotency_middleware() -> IdempotencyMiddleware:
    """Get the singleton idempotency middleware instance."""
    global _middleware
    if _middleware is None:
        # Use in-memory for development, Dapr for production
        import os
        if os.getenv("DAPR_HTTP_PORT"):
            _middleware = IdempotencyMiddleware()
        else:
            _middleware = InMemoryIdempotencyMiddleware()
    return _middleware


def idempotent(func: Callable) -> Callable:
    """
    Decorator to make an async function idempotent.

    The function's first argument must be an object with an 'id' attribute.

    Usage:
        @idempotent
        async def process_event(event: BaseEvent):
            # Process event - will only run once per event ID
            pass
    """

    @wraps(func)
    async def wrapper(*args, **kwargs):
        # Get the event from args
        event = args[0] if args else kwargs.get("event")
        if not event or not hasattr(event, "id"):
            return await func(*args, **kwargs)

        middleware = get_idempotency_middleware()
        event_id = str(event.id)

        # Check if already processed
        if await middleware.is_processed(event_id):
            logger.info(f"Skipping duplicate event {event_id}")
            return None

        try:
            # Execute the function
            result = await func(*args, **kwargs)

            # Mark as processed
            await middleware.mark_processed(event_id)

            return result

        except Exception as e:
            # Don't mark as processed on failure
            logger.error(f"Event {event_id} processing failed: {e}")
            raise

    return wrapper
