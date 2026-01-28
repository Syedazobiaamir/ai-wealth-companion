"""Transaction repository for data access."""

from datetime import date, datetime
from decimal import Decimal
from typing import List, Optional, Tuple
from uuid import UUID

from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.category import Category
from src.models.transaction import (
    Transaction,
    TransactionCreate,
    TransactionType,
    TransactionUpdate,
)
from src.repositories.base import BaseRepository


class TransactionRepository(BaseRepository[Transaction, TransactionCreate, TransactionUpdate]):
    """Repository for transaction operations with soft delete support."""

    def __init__(self, session: AsyncSession):
        super().__init__(Transaction, session)

    async def get(self, id: UUID) -> Optional[Transaction]:
        """Get a single non-deleted transaction by ID."""
        statement = select(Transaction).where(
            and_(
                Transaction.id == id,
                Transaction.is_deleted == False,
            )
        )
        result = await self.session.execute(statement)
        return result.scalar_one_or_none()

    async def get_by_user(
        self,
        user_id: UUID,
        id: UUID,
    ) -> Optional[Transaction]:
        """Get a single non-deleted transaction by ID for a user."""
        statement = select(Transaction).where(
            and_(
                Transaction.id == id,
                Transaction.user_id == user_id,
                Transaction.is_deleted == False,
            )
        )
        result = await self.session.execute(statement)
        return result.scalar_one_or_none()

    async def get_all(
        self,
        user_id: UUID,
        skip: int = 0,
        limit: int = 100,
        sort_by: str = "date",
        sort_order: str = "desc",
    ) -> List[Transaction]:
        """Get all non-deleted transactions for a user with pagination and sorting."""
        # Determine sort column
        if sort_by == "amount":
            sort_column = Transaction.amount
        elif sort_by == "date":
            sort_column = Transaction.transaction_date
        elif sort_by == "created_at":
            sort_column = Transaction.created_at
        else:
            sort_column = Transaction.transaction_date

        # Determine sort order
        if sort_order == "asc":
            order_expr = sort_column.asc()
        else:
            order_expr = sort_column.desc()

        statement = (
            select(Transaction)
            .where(
                Transaction.user_id == user_id,
                Transaction.is_deleted == False,
            )
            .order_by(order_expr, Transaction.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        result = await self.session.execute(statement)
        return list(result.scalars().all())

    async def get_with_category(
        self,
        id: UUID,
        user_id: UUID,
    ) -> Optional[Tuple[Transaction, Category]]:
        """Get transaction with its category for a user."""
        statement = (
            select(Transaction, Category)
            .join(Category, Transaction.category_id == Category.id)
            .where(
                and_(
                    Transaction.id == id,
                    Transaction.user_id == user_id,
                    Transaction.is_deleted == False,
                )
            )
        )
        result = await self.session.execute(statement)
        row = result.one_or_none()
        return row if row else None

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
    ) -> List[Transaction]:
        """Get transactions with optional filters including type."""
        conditions = [
            Transaction.user_id == user_id,
            Transaction.is_deleted == False,
        ]

        if start_date:
            conditions.append(Transaction.transaction_date >= start_date)

        if end_date:
            conditions.append(Transaction.transaction_date <= end_date)

        if transaction_type:
            conditions.append(Transaction.type == transaction_type)

        if category_id:
            conditions.append(Transaction.category_id == category_id)

        if wallet_id:
            conditions.append(Transaction.wallet_id == wallet_id)

        # Determine sort column
        if sort_by == "amount":
            sort_column = Transaction.amount
        elif sort_by == "date":
            sort_column = Transaction.transaction_date
        elif sort_by == "created_at":
            sort_column = Transaction.created_at
        else:
            sort_column = Transaction.transaction_date

        # Determine sort order
        if sort_order == "asc":
            order_expr = sort_column.asc()
        else:
            order_expr = sort_column.desc()

        statement = (
            select(Transaction)
            .where(and_(*conditions))
            .order_by(order_expr, Transaction.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        result = await self.session.execute(statement)
        return list(result.scalars().all())

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
    ) -> List[Transaction]:
        """Get transactions within a date range with optional filters and sorting."""
        conditions = [
            Transaction.user_id == user_id,
            Transaction.is_deleted == False,
            Transaction.transaction_date >= start_date,
            Transaction.transaction_date <= end_date,
        ]

        if transaction_type:
            conditions.append(Transaction.type == transaction_type)

        if category_id:
            conditions.append(Transaction.category_id == category_id)

        if wallet_id:
            conditions.append(Transaction.wallet_id == wallet_id)

        # Determine sort column
        if sort_by == "amount":
            sort_column = Transaction.amount
        elif sort_by == "date":
            sort_column = Transaction.transaction_date
        elif sort_by == "created_at":
            sort_column = Transaction.created_at
        else:
            sort_column = Transaction.transaction_date

        # Determine sort order
        if sort_order == "asc":
            order_expr = sort_column.asc()
        else:
            order_expr = sort_column.desc()

        statement = (
            select(Transaction)
            .where(and_(*conditions))
            .order_by(order_expr, Transaction.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        result = await self.session.execute(statement)
        return list(result.scalars().all())

    async def get_by_category(
        self,
        user_id: UUID,
        category_id: UUID,
        skip: int = 0,
        limit: int = 100,
    ) -> List[Transaction]:
        """Get transactions by category for a user."""
        statement = (
            select(Transaction)
            .where(
                and_(
                    Transaction.user_id == user_id,
                    Transaction.is_deleted == False,
                    Transaction.category_id == category_id,
                )
            )
            .order_by(Transaction.transaction_date.desc())
            .offset(skip)
            .limit(limit)
        )
        result = await self.session.execute(statement)
        return list(result.scalars().all())

    async def create_with_user(
        self,
        user_id: UUID,
        data: TransactionCreate,
    ) -> Transaction:
        """Create a transaction for a user."""
        transaction = Transaction(
            user_id=user_id,
            wallet_id=data.wallet_id,
            type=data.type,
            amount=data.amount,
            category_id=data.category_id,
            transaction_date=data.transaction_date,
            note=data.note,
            is_recurring=data.is_recurring,
            recurring_frequency=data.recurring_frequency,
            tags=data.tags,
        )
        self.session.add(transaction)
        await self.session.flush()
        await self.session.refresh(transaction)
        return transaction

    async def soft_delete(self, id: UUID, user_id: UUID) -> bool:
        """Soft delete a transaction for a user."""
        db_obj = await self.get_by_user(user_id, id)
        if not db_obj:
            return False

        db_obj.is_deleted = True
        db_obj.deleted_at = datetime.utcnow()
        self.session.add(db_obj)
        await self.session.flush()
        return True

    async def restore(self, id: UUID, user_id: UUID) -> Optional[Transaction]:
        """Restore a soft-deleted transaction for a user."""
        statement = select(Transaction).where(
            and_(
                Transaction.id == id,
                Transaction.user_id == user_id,
                Transaction.is_deleted == True,
            )
        )
        result = await self.session.execute(statement)
        db_obj = result.scalar_one_or_none()

        if not db_obj:
            return None

        db_obj.is_deleted = False
        db_obj.deleted_at = None
        self.session.add(db_obj)
        await self.session.flush()
        await self.session.refresh(db_obj)
        return db_obj

    async def get_totals_by_type(
        self,
        user_id: UUID,
        start_date: date,
        end_date: date,
    ) -> dict:
        """Get total income and expense for a date range."""
        statement = (
            select(
                Transaction.type,
                func.sum(Transaction.amount).label("total"),
            )
            .where(
                and_(
                    Transaction.user_id == user_id,
                    Transaction.is_deleted == False,
                    Transaction.transaction_date >= start_date,
                    Transaction.transaction_date <= end_date,
                )
            )
            .group_by(Transaction.type)
        )
        result = await self.session.execute(statement)
        rows = result.all()

        totals = {
            TransactionType.income: Decimal("0"),
            TransactionType.expense: Decimal("0"),
        }
        for row in rows:
            totals[row.type] = row.total or Decimal("0")

        return totals

    async def get_totals_by_category(
        self,
        user_id: UUID,
        start_date: date,
        end_date: date,
        transaction_type: Optional[TransactionType] = None,
    ) -> List[dict]:
        """Get totals grouped by category for a date range."""
        conditions = [
            Transaction.user_id == user_id,
            Transaction.is_deleted == False,
            Transaction.transaction_date >= start_date,
            Transaction.transaction_date <= end_date,
        ]

        if transaction_type:
            conditions.append(Transaction.type == transaction_type)

        statement = (
            select(
                Category.id,
                Category.name,
                Category.emoji,
                func.sum(Transaction.amount).label("total"),
                func.count(Transaction.id).label("count"),
            )
            .join(Category, Transaction.category_id == Category.id)
            .where(and_(*conditions))
            .group_by(Category.id, Category.name, Category.emoji)
            .order_by(func.sum(Transaction.amount).desc())
        )
        result = await self.session.execute(statement)
        rows = result.all()

        return [
            {
                "category_id": str(row.id),
                "category_name": row.name,
                "category_emoji": row.emoji,
                "total": row.total,
                "count": row.count,
            }
            for row in rows
        ]

    async def get_monthly_totals(
        self,
        user_id: UUID,
        year: int,
    ) -> List[dict]:
        """Get monthly income/expense totals for a year."""
        statement = (
            select(
                func.extract("month", Transaction.transaction_date).label("month"),
                Transaction.type,
                func.sum(Transaction.amount).label("total"),
            )
            .where(
                and_(
                    Transaction.user_id == user_id,
                    Transaction.is_deleted == False,
                    func.extract("year", Transaction.transaction_date) == year,
                )
            )
            .group_by(
                func.extract("month", Transaction.transaction_date),
                Transaction.type,
            )
            .order_by(func.extract("month", Transaction.transaction_date))
        )
        result = await self.session.execute(statement)
        rows = result.all()

        # Organize by month
        monthly_data = {}
        for row in rows:
            month = int(row.month)
            if month not in monthly_data:
                monthly_data[month] = {
                    "month": month,
                    "year": year,
                    "income": Decimal("0"),
                    "expense": Decimal("0"),
                }
            if row.type == TransactionType.income:
                monthly_data[month]["income"] = row.total
            else:
                monthly_data[month]["expense"] = row.total

        return list(monthly_data.values())

    async def search(
        self,
        user_id: UUID,
        query: str,
        skip: int = 0,
        limit: int = 100,
    ) -> List[Transaction]:
        """Search transactions by note for a user."""
        statement = (
            select(Transaction)
            .where(
                and_(
                    Transaction.user_id == user_id,
                    Transaction.is_deleted == False,
                    Transaction.note.ilike(f"%{query}%"),
                )
            )
            .order_by(Transaction.transaction_date.desc())
            .offset(skip)
            .limit(limit)
        )
        result = await self.session.execute(statement)
        return list(result.scalars().all())

    async def count_active(self, user_id: UUID) -> int:
        """Count non-deleted transactions for a user."""
        statement = (
            select(func.count())
            .select_from(Transaction)
            .where(
                Transaction.user_id == user_id,
                Transaction.is_deleted == False,
            )
        )
        result = await self.session.execute(statement)
        return result.scalar_one()
