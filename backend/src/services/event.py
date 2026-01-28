"""Event service for event logging and emission."""

from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.event_log import EventLog, EventType


class EventService:
    """Service for event logging and emission."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def emit(
        self,
        event_type: EventType,
        user_id: UUID,
        entity_type: str,
        entity_id: UUID,
        data: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> EventLog:
        """Emit and log an event."""
        event = EventLog(
            event_type=event_type,
            user_id=user_id,
            entity_type=entity_type,
            entity_id=entity_id,
            data=data or {},
            metadata=metadata or {},
        )
        self.session.add(event)
        await self.session.flush()
        await self.session.refresh(event)
        return event

    async def get_user_events(
        self,
        user_id: UUID,
        event_types: Optional[List[EventType]] = None,
        skip: int = 0,
        limit: int = 50,
    ) -> List[EventLog]:
        """Get events for a user."""
        statement = select(EventLog).where(EventLog.user_id == user_id)
        if event_types:
            statement = statement.where(EventLog.event_type.in_(event_types))
        statement = statement.order_by(EventLog.created_at.desc())
        statement = statement.offset(skip).limit(limit)
        result = await self.session.execute(statement)
        return list(result.scalars().all())

    async def get_entity_events(
        self,
        entity_type: str,
        entity_id: UUID,
        skip: int = 0,
        limit: int = 50,
    ) -> List[EventLog]:
        """Get events for a specific entity."""
        statement = (
            select(EventLog)
            .where(
                EventLog.entity_type == entity_type,
                EventLog.entity_id == entity_id,
            )
            .order_by(EventLog.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        result = await self.session.execute(statement)
        return list(result.scalars().all())

    async def get_recent_events(
        self,
        user_id: UUID,
        hours: int = 24,
    ) -> List[EventLog]:
        """Get recent events within specified hours."""
        from datetime import timedelta

        cutoff = datetime.utcnow() - timedelta(hours=hours)
        statement = (
            select(EventLog)
            .where(
                EventLog.user_id == user_id,
                EventLog.created_at >= cutoff,
            )
            .order_by(EventLog.created_at.desc())
        )
        result = await self.session.execute(statement)
        return list(result.scalars().all())

    # Convenience methods for common events
    async def emit_transaction_created(
        self,
        user_id: UUID,
        transaction_id: UUID,
        data: Dict[str, Any],
    ) -> EventLog:
        """Emit transaction created event."""
        return await self.emit(
            event_type=EventType.transaction_created,
            user_id=user_id,
            entity_type="transaction",
            entity_id=transaction_id,
            data=data,
        )

    async def emit_transaction_updated(
        self,
        user_id: UUID,
        transaction_id: UUID,
        data: Dict[str, Any],
    ) -> EventLog:
        """Emit transaction updated event."""
        return await self.emit(
            event_type=EventType.transaction_updated,
            user_id=user_id,
            entity_type="transaction",
            entity_id=transaction_id,
            data=data,
        )

    async def emit_budget_exceeded(
        self,
        user_id: UUID,
        budget_id: UUID,
        data: Dict[str, Any],
    ) -> EventLog:
        """Emit budget exceeded event."""
        return await self.emit(
            event_type=EventType.budget_exceeded,
            user_id=user_id,
            entity_type="budget",
            entity_id=budget_id,
            data=data,
        )

    async def emit_budget_warning(
        self,
        user_id: UUID,
        budget_id: UUID,
        data: Dict[str, Any],
    ) -> EventLog:
        """Emit budget warning event."""
        return await self.emit(
            event_type=EventType.budget_warning,
            user_id=user_id,
            entity_type="budget",
            entity_id=budget_id,
            data=data,
        )

    async def emit_goal_completed(
        self,
        user_id: UUID,
        goal_id: UUID,
        data: Dict[str, Any],
    ) -> EventLog:
        """Emit goal completed event."""
        return await self.emit(
            event_type=EventType.goal_completed,
            user_id=user_id,
            entity_type="goal",
            entity_id=goal_id,
            data=data,
        )

    async def emit_goal_progress(
        self,
        user_id: UUID,
        goal_id: UUID,
        data: Dict[str, Any],
    ) -> EventLog:
        """Emit goal progress event."""
        return await self.emit(
            event_type=EventType.goal_progress,
            user_id=user_id,
            entity_type="goal",
            entity_id=goal_id,
            data=data,
        )

    async def emit_user_login(
        self,
        user_id: UUID,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> EventLog:
        """Emit user login event."""
        return await self.emit(
            event_type=EventType.user_login,
            user_id=user_id,
            entity_type="user",
            entity_id=user_id,
            metadata=metadata,
        )
