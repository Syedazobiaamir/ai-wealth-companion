"""Budget repository for data access."""

from datetime import date
from decimal import Decimal
from typing import List, Optional
from uuid import UUID

from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.budget import Budget, BudgetCreate, BudgetUpdate
from src.models.category import Category
from src.models.transaction import Transaction, TransactionType
from src.repositories.base import BaseRepository


class BudgetRepository(BaseRepository[Budget, BudgetCreate, BudgetUpdate]):
    """Repository for budget operations."""

    def __init__(self, session: AsyncSession):
        super().__init__(Budget, session)

    async def get_by_user(
        self,
        user_id: UUID,
        budget_id: UUID,
    ) -> Optional[Budget]:
        """Get a budget by ID for a user."""
        statement = select(Budget).where(
            and_(
                Budget.id == budget_id,
                Budget.user_id == user_id,
            )
        )
        result = await self.session.execute(statement)
        return result.scalar_one_or_none()

    async def get_by_category_and_period(
        self,
        user_id: UUID,
        category_id: UUID,
        month: int,
        year: int,
    ) -> Optional[Budget]:
        """Get budget for a specific category and month/year for a user."""
        statement = select(Budget).where(
            and_(
                Budget.user_id == user_id,
                Budget.category_id == category_id,
                Budget.month == month,
                Budget.year == year,
            )
        )
        result = await self.session.execute(statement)
        return result.scalar_one_or_none()

    async def get_budgets_for_period(
        self,
        user_id: UUID,
        month: int,
        year: int,
    ) -> List[Budget]:
        """Get all budgets for a specific month/year for a user."""
        statement = (
            select(Budget)
            .where(
                and_(
                    Budget.user_id == user_id,
                    Budget.month == month,
                    Budget.year == year,
                )
            )
            .order_by(Budget.created_at)
        )
        result = await self.session.execute(statement)
        return list(result.scalars().all())

    async def get_with_status(
        self,
        user_id: UUID,
        month: int,
        year: int,
    ) -> List[dict]:
        """Get all budgets with spending status for a period."""
        from calendar import monthrange

        # Calculate date range for the month
        _, last_day = monthrange(year, month)
        start_date = date(year, month, 1)
        end_date = date(year, month, last_day)

        # Get budgets with category info
        budget_statement = (
            select(Budget, Category)
            .join(Category, Budget.category_id == Category.id)
            .where(
                and_(
                    Budget.user_id == user_id,
                    Budget.month == month,
                    Budget.year == year,
                )
            )
        )
        budget_result = await self.session.execute(budget_statement)
        budgets = budget_result.all()

        # Get spending per category
        spending_statement = (
            select(
                Transaction.category_id,
                func.sum(Transaction.amount).label("spent"),
            )
            .where(
                and_(
                    Transaction.user_id == user_id,
                    Transaction.is_deleted == False,
                    Transaction.type == TransactionType.expense,
                    Transaction.transaction_date >= start_date,
                    Transaction.transaction_date <= end_date,
                )
            )
            .group_by(Transaction.category_id)
        )
        spending_result = await self.session.execute(spending_statement)
        spending_by_category = {
            str(row.category_id): row.spent
            for row in spending_result.all()
        }

        # Build status list
        statuses = []
        for budget, category in budgets:
            spent = spending_by_category.get(str(budget.category_id), Decimal("0"))
            limit_amount = budget.limit_amount
            remaining = limit_amount - spent
            percentage = (spent / limit_amount * 100) if limit_amount > 0 else Decimal("0")
            threshold = budget.alert_threshold or 80

            statuses.append({
                "id": str(budget.id),
                "category_id": str(category.id),
                "category": category.name,
                "emoji": category.emoji,
                "limit": limit_amount,
                "spent": spent,
                "remaining": remaining,
                "percentage": round(percentage, 2),
                "exceeded": spent > limit_amount,
                "warning": percentage >= threshold and not spent > limit_amount,
            })

        return statuses

    async def create_with_user(
        self,
        user_id: UUID,
        data: BudgetCreate,
    ) -> Budget:
        """Create a budget for a user."""
        budget = Budget(
            user_id=user_id,
            category_id=data.category_id,
            limit_amount=data.limit_amount,
            month=data.month,
            year=data.year,
            alert_threshold=data.alert_threshold,
        )
        self.session.add(budget)
        await self.session.flush()
        await self.session.refresh(budget)
        return budget

    async def create_or_update(
        self,
        user_id: UUID,
        category_id: UUID,
        month: int,
        year: int,
        limit_amount: Decimal,
        alert_threshold: int = 80,
    ) -> Budget:
        """Create or update a budget for a category and period."""
        existing = await self.get_by_category_and_period(user_id, category_id, month, year)

        if existing:
            existing.limit_amount = limit_amount
            existing.alert_threshold = alert_threshold
            from datetime import datetime
            existing.updated_at = datetime.utcnow()
            self.session.add(existing)
            await self.session.flush()
            await self.session.refresh(existing)
            return existing

        budget = Budget(
            user_id=user_id,
            category_id=category_id,
            limit_amount=limit_amount,
            month=month,
            year=year,
            alert_threshold=alert_threshold,
        )
        self.session.add(budget)
        await self.session.flush()
        await self.session.refresh(budget)
        return budget

    async def get_exceeded_budgets(
        self,
        user_id: UUID,
        month: int,
        year: int,
    ) -> List[dict]:
        """Get budgets that have been exceeded."""
        statuses = await self.get_with_status(user_id, month, year)
        return [s for s in statuses if s["exceeded"]]

    async def get_warning_budgets(
        self,
        user_id: UUID,
        month: int,
        year: int,
    ) -> List[dict]:
        """Get budgets at 80%+ usage but not exceeded."""
        statuses = await self.get_with_status(user_id, month, year)
        return [s for s in statuses if s["warning"]]
