"""Transaction service for business logic."""

import logging
from datetime import date, datetime
from decimal import Decimal
from typing import List, Optional
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from src.models.transaction import (
    Transaction,
    TransactionCreate,
    TransactionRead,
    TransactionType,
    TransactionUpdate,
    TransactionWithCategory,
)
from src.repositories.transaction import TransactionRepository

# Phase V: Event-driven imports
try:
    from src.events import (
        TransactionCreatedEvent,
        TransactionUpdatedEvent,
        TransactionData,
        publish_event,
    )
    EVENTS_ENABLED = True
except ImportError:
    EVENTS_ENABLED = False

logger = logging.getLogger(__name__)


class TransactionService:
    """Service for transaction operations."""

    def __init__(self, session: AsyncSession, enable_events: bool = True):
        self.repository = TransactionRepository(session)
        self.events_enabled = enable_events and EVENTS_ENABLED

    async def get_all(
        self,
        user_id: UUID,
        skip: int = 0,
        limit: int = 100,
        sort_by: str = "date",
        sort_order: str = "desc",
    ) -> List[TransactionRead]:
        """Get all transactions for a user with pagination and sorting."""
        transactions = await self.repository.get_all(
            user_id=user_id,
            skip=skip,
            limit=limit,
            sort_by=sort_by,
            sort_order=sort_order,
        )
        return [TransactionRead.model_validate(t) for t in transactions]

    async def get_by_id(
        self,
        user_id: UUID,
        transaction_id: UUID,
    ) -> Optional[TransactionRead]:
        """Get a transaction by ID for a user."""
        transaction = await self.repository.get_by_user(user_id, transaction_id)
        if not transaction:
            return None
        return TransactionRead.model_validate(transaction)

    async def get_with_category(
        self,
        user_id: UUID,
        transaction_id: UUID,
    ) -> Optional[TransactionWithCategory]:
        """Get a transaction with its category details for a user."""
        result = await self.repository.get_with_category(transaction_id, user_id)
        if not result:
            return None

        transaction, category = result
        return TransactionWithCategory(
            id=transaction.id,
            user_id=transaction.user_id,
            wallet_id=transaction.wallet_id,
            type=transaction.type,
            amount=transaction.amount,
            category_id=transaction.category_id,
            transaction_date=transaction.transaction_date,
            note=transaction.note,
            is_recurring=transaction.is_recurring,
            recurring_frequency=transaction.recurring_frequency,
            tags=transaction.tags,
            created_at=transaction.created_at,
            updated_at=transaction.updated_at,
            category_name=category.name,
            category_emoji=category.emoji,
        )

    async def get_by_filters(
        self,
        user_id: UUID,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        transaction_type: Optional[TransactionType] = None,
        category_id: Optional[UUID] = None,
        wallet_id: Optional[UUID] = None,
        skip: int = 0,
        limit: int = 100,
        sort_by: str = "date",
        sort_order: str = "desc",
    ) -> List[TransactionRead]:
        """Get transactions with optional filters including type."""
        transactions = await self.repository.get_by_filters(
            user_id=user_id,
            start_date=start_date,
            end_date=end_date,
            transaction_type=transaction_type,
            category_id=category_id,
            wallet_id=wallet_id,
            skip=skip,
            limit=limit,
            sort_by=sort_by,
            sort_order=sort_order,
        )
        return [TransactionRead.model_validate(t) for t in transactions]

    async def get_by_date_range(
        self,
        user_id: UUID,
        start_date: date,
        end_date: date,
        transaction_type: Optional[TransactionType] = None,
        category_id: Optional[UUID] = None,
        wallet_id: Optional[UUID] = None,
        skip: int = 0,
        limit: int = 100,
        sort_by: str = "date",
        sort_order: str = "desc",
    ) -> List[TransactionRead]:
        """Get transactions within a date range for a user with optional sorting."""
        transactions = await self.repository.get_by_date_range(
            user_id=user_id,
            start_date=start_date,
            end_date=end_date,
            transaction_type=transaction_type,
            category_id=category_id,
            wallet_id=wallet_id,
            skip=skip,
            limit=limit,
            sort_by=sort_by,
            sort_order=sort_order,
        )
        return [TransactionRead.model_validate(t) for t in transactions]

    async def create(
        self,
        user_id: UUID,
        data: TransactionCreate,
    ) -> TransactionRead:
        """Create a new transaction for a user."""
        transaction = await self.repository.create_with_user(user_id, data)
        result = TransactionRead.model_validate(transaction)

        # Phase V: Publish transaction.created event
        if self.events_enabled:
            await self._publish_transaction_created(transaction, user_id)

        return result

    async def _publish_transaction_created(
        self,
        transaction: Transaction,
        user_id: UUID,
    ) -> None:
        """Publish a transaction.created event to Kafka via Dapr."""
        try:
            event = TransactionCreatedEvent(
                subject=str(user_id),
                data=TransactionData(
                    transaction_id=transaction.id,
                    user_id=user_id,
                    wallet_id=transaction.wallet_id,
                    amount=Decimal(str(transaction.amount)),
                    currency="USD",
                    category_id=transaction.category_id,
                    description=transaction.note,
                    transaction_type=transaction.type.value if hasattr(transaction.type, 'value') else str(transaction.type),
                    transaction_date=transaction.transaction_date,
                ),
            )
            await publish_event(event, "transactions")
            logger.info(f"Published transaction.created event: {event.id}")
        except Exception as e:
            # Log but don't fail the transaction
            logger.error(f"Failed to publish transaction.created event: {e}")

    async def update(
        self,
        user_id: UUID,
        transaction_id: UUID,
        data: TransactionUpdate,
    ) -> Optional[TransactionRead]:
        """Update an existing transaction for a user."""
        transaction = await self.repository.get_by_user(user_id, transaction_id)
        if not transaction:
            return None

        # Store previous values for event
        previous_amount = Decimal(str(transaction.amount)) if transaction.amount else None
        previous_category_id = transaction.category_id

        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(transaction, field, value)

        transaction.updated_at = datetime.utcnow()
        self.repository.session.add(transaction)
        await self.repository.session.flush()
        await self.repository.session.refresh(transaction)

        result = TransactionRead.model_validate(transaction)

        # Phase V: Publish transaction.updated event
        if self.events_enabled:
            await self._publish_transaction_updated(
                transaction, user_id, previous_amount, previous_category_id
            )

        return result

    async def _publish_transaction_updated(
        self,
        transaction: Transaction,
        user_id: UUID,
        previous_amount: Optional[Decimal],
        previous_category_id: Optional[UUID],
    ) -> None:
        """Publish a transaction.updated event to Kafka via Dapr."""
        try:
            event = TransactionUpdatedEvent(
                subject=str(user_id),
                previous_amount=previous_amount,
                previous_category_id=previous_category_id,
                data=TransactionData(
                    transaction_id=transaction.id,
                    user_id=user_id,
                    wallet_id=transaction.wallet_id,
                    amount=Decimal(str(transaction.amount)),
                    currency="USD",
                    category_id=transaction.category_id,
                    description=transaction.note,
                    transaction_type=transaction.type.value if hasattr(transaction.type, 'value') else str(transaction.type),
                    transaction_date=transaction.transaction_date,
                ),
            )
            await publish_event(event, "transactions")
            logger.info(f"Published transaction.updated event: {event.id}")
        except Exception as e:
            # Log but don't fail the transaction
            logger.error(f"Failed to publish transaction.updated event: {e}")

    async def delete(self, user_id: UUID, transaction_id: UUID) -> bool:
        """Soft delete a transaction for a user."""
        return await self.repository.soft_delete(transaction_id, user_id)

    async def restore(
        self,
        user_id: UUID,
        transaction_id: UUID,
    ) -> Optional[TransactionRead]:
        """Restore a soft-deleted transaction for a user."""
        transaction = await self.repository.restore(transaction_id, user_id)
        if not transaction:
            return None
        return TransactionRead.model_validate(transaction)

    async def search(
        self,
        user_id: UUID,
        query: str,
        skip: int = 0,
        limit: int = 100,
    ) -> List[TransactionRead]:
        """Search transactions by note for a user."""
        transactions = await self.repository.search(
            user_id, query, skip=skip, limit=limit
        )
        return [TransactionRead.model_validate(t) for t in transactions]

    async def count(self, user_id: UUID) -> int:
        """Count active transactions for a user."""
        return await self.repository.count_active(user_id)
