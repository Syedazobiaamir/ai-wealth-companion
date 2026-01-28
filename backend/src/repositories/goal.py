"""Goal repository for database operations."""

from datetime import datetime
from typing import List, Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.goal import Goal, GoalCreate, GoalStatus, GoalUpdate
from src.repositories.base import BaseRepository


class GoalRepository(BaseRepository[Goal, GoalCreate, GoalUpdate]):
    """Repository for goal database operations."""

    def __init__(self, session: AsyncSession):
        super().__init__(Goal, session)

    async def get_by_user(
        self,
        user_id: UUID,
        status: Optional[GoalStatus] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> List[Goal]:
        """Get all goals for a user with optional status filter."""
        statement = select(Goal).where(Goal.user_id == user_id)
        if status:
            statement = statement.where(Goal.status == status)
        statement = statement.order_by(Goal.priority.desc(), Goal.created_at.desc())
        statement = statement.offset(skip).limit(limit)
        result = await self.session.execute(statement)
        return list(result.scalars().all())

    async def get_by_id_and_user(
        self,
        goal_id: UUID,
        user_id: UUID,
    ) -> Optional[Goal]:
        """Get a goal by ID for a specific user."""
        statement = select(Goal).where(
            Goal.id == goal_id,
            Goal.user_id == user_id,
        )
        result = await self.session.execute(statement)
        return result.scalar_one_or_none()

    async def get_active(self, user_id: UUID) -> List[Goal]:
        """Get all active goals for a user."""
        return await self.get_by_user(user_id, status=GoalStatus.active)

    async def create_with_user(
        self,
        user_id: UUID,
        goal_data: GoalCreate,
    ) -> Goal:
        """Create a goal for a user."""
        goal = Goal(
            user_id=user_id,
            name=goal_data.name,
            description=goal_data.description,
            target_amount=goal_data.target_amount,
            currency=goal_data.currency,
            target_date=goal_data.target_date,
            emoji=goal_data.emoji,
            color=goal_data.color,
            priority=goal_data.priority,
        )
        self.session.add(goal)
        await self.session.flush()
        await self.session.refresh(goal)
        return goal

    async def update_progress(
        self,
        goal_id: UUID,
        amount_change: float,
    ) -> Optional[Goal]:
        """Update goal progress by adding to current amount."""
        goal = await self.get(goal_id)
        if not goal:
            return None

        goal.current_amount = goal.current_amount + amount_change
        goal.updated_at = datetime.utcnow()

        # Auto-complete if target reached
        if goal.current_amount >= goal.target_amount:
            goal.status = GoalStatus.completed
            goal.completed_at = datetime.utcnow()

        self.session.add(goal)
        await self.session.flush()
        await self.session.refresh(goal)
        return goal

    async def mark_completed(
        self,
        goal_id: UUID,
        user_id: UUID,
    ) -> Optional[Goal]:
        """Mark a goal as completed."""
        goal = await self.get_by_id_and_user(goal_id, user_id)
        if not goal:
            return None

        goal.status = GoalStatus.completed
        goal.completed_at = datetime.utcnow()
        goal.updated_at = datetime.utcnow()

        self.session.add(goal)
        await self.session.flush()
        await self.session.refresh(goal)
        return goal

    async def count_by_user(
        self,
        user_id: UUID,
        status: Optional[GoalStatus] = None,
    ) -> int:
        """Count goals for a user."""
        from sqlalchemy import func

        statement = select(func.count()).select_from(Goal).where(
            Goal.user_id == user_id
        )
        if status:
            statement = statement.where(Goal.status == status)
        result = await self.session.execute(statement)
        return result.scalar_one()

    async def get_near_completion(
        self,
        user_id: UUID,
        threshold_percent: float = 80.0,
    ) -> List[Goal]:
        """Get goals that are near completion."""
        goals = await self.get_active(user_id)
        return [
            g for g in goals
            if g.target_amount > 0
            and (float(g.current_amount) / float(g.target_amount)) * 100 >= threshold_percent
        ]

    async def get_total_saved(self, user_id: UUID) -> float:
        """Get total amount saved across all goals."""
        from sqlalchemy import func

        statement = select(func.sum(Goal.current_amount)).where(
            Goal.user_id == user_id,
            Goal.status == GoalStatus.active,
        )
        result = await self.session.execute(statement)
        total = result.scalar_one_or_none()
        return float(total) if total else 0.0
