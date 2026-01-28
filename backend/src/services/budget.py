"""Budget service for business logic."""

from datetime import datetime
from decimal import Decimal
from typing import List, Optional
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from src.models.budget import Budget, BudgetCreate, BudgetRead, BudgetStatus, BudgetUpdate
from src.repositories.budget import BudgetRepository


class BudgetService:
    """Service for budget operations."""

    def __init__(self, session: AsyncSession):
        self.repository = BudgetRepository(session)

    async def get_all_for_period(
        self,
        user_id: UUID,
        month: int,
        year: int,
    ) -> List[BudgetRead]:
        """Get all budgets for a specific month/year for a user."""
        budgets = await self.repository.get_budgets_for_period(user_id, month, year)
        return [BudgetRead.model_validate(b) for b in budgets]

    async def get_by_id(self, user_id: UUID, budget_id: UUID) -> Optional[BudgetRead]:
        """Get a budget by ID for a user."""
        budget = await self.repository.get_by_user(user_id, budget_id)
        if not budget:
            return None
        return BudgetRead.model_validate(budget)

    async def get_by_category_and_period(
        self,
        user_id: UUID,
        category_id: UUID,
        month: int,
        year: int,
    ) -> Optional[BudgetRead]:
        """Get budget for a specific category and period for a user."""
        budget = await self.repository.get_by_category_and_period(
            user_id, category_id, month, year
        )
        if not budget:
            return None
        return BudgetRead.model_validate(budget)

    async def create(self, user_id: UUID, data: BudgetCreate) -> BudgetRead:
        """Create a new budget for a user."""
        budget = await self.repository.create_with_user(user_id, data)
        return BudgetRead.model_validate(budget)

    async def create_or_update(
        self,
        user_id: UUID,
        category_id: UUID,
        month: int,
        year: int,
        limit_amount: Decimal,
        alert_threshold: int = 80,
    ) -> BudgetRead:
        """Create or update a budget for a category and period."""
        budget = await self.repository.create_or_update(
            user_id=user_id,
            category_id=category_id,
            month=month,
            year=year,
            limit_amount=limit_amount,
            alert_threshold=alert_threshold,
        )
        return BudgetRead.model_validate(budget)

    async def update(
        self,
        user_id: UUID,
        budget_id: UUID,
        data: BudgetUpdate,
    ) -> Optional[BudgetRead]:
        """Update an existing budget for a user."""
        budget = await self.repository.get_by_user(user_id, budget_id)
        if not budget:
            return None

        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(budget, field, value)

        budget.updated_at = datetime.utcnow()
        self.repository.session.add(budget)
        await self.repository.session.flush()
        await self.repository.session.refresh(budget)
        return BudgetRead.model_validate(budget)

    async def delete(self, user_id: UUID, budget_id: UUID) -> bool:
        """Delete a budget for a user."""
        budget = await self.repository.get_by_user(user_id, budget_id)
        if not budget:
            return False
        return await self.repository.delete(budget_id)

    async def get_status_for_period(
        self,
        user_id: UUID,
        month: int,
        year: int,
    ) -> List[BudgetStatus]:
        """Get budget status with spending for a period."""
        statuses = await self.repository.get_with_status(user_id, month, year)
        return [
            BudgetStatus(
                category=s["category"],
                emoji=s["emoji"],
                limit=s["limit"],
                spent=s["spent"],
                remaining=s["remaining"],
                percentage=s["percentage"],
                exceeded=s["exceeded"],
                warning=s["warning"],
            )
            for s in statuses
        ]

    async def get_exceeded(self, user_id: UUID, month: int, year: int) -> List[dict]:
        """Get budgets that have been exceeded."""
        return await self.repository.get_exceeded_budgets(user_id, month, year)

    async def get_warnings(self, user_id: UUID, month: int, year: int) -> List[dict]:
        """Get budgets at warning level (80%+)."""
        return await self.repository.get_warning_budgets(user_id, month, year)
