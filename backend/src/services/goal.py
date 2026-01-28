"""Goal service for business logic."""

from datetime import datetime
from typing import List, Optional
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from src.models.goal import Goal, GoalCreate, GoalStatus, GoalUpdate
from src.repositories.goal import GoalRepository


class GoalService:
    """Service for goal operations."""

    def __init__(self, session: AsyncSession):
        self.repo = GoalRepository(session)

    async def get_all(
        self,
        user_id: UUID,
        status: Optional[GoalStatus] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> List[Goal]:
        """Get all goals for a user."""
        return await self.repo.get_by_user(user_id, status, skip, limit)

    async def get_by_id(
        self,
        goal_id: UUID,
        user_id: UUID,
    ) -> Optional[Goal]:
        """Get a goal by ID for a user."""
        return await self.repo.get_by_id_and_user(goal_id, user_id)

    async def get_active(self, user_id: UUID) -> List[Goal]:
        """Get all active goals for a user."""
        return await self.repo.get_active(user_id)

    async def create(
        self,
        user_id: UUID,
        goal_data: GoalCreate,
    ) -> Goal:
        """Create a new goal."""
        return await self.repo.create_with_user(user_id, goal_data)

    async def update(
        self,
        goal_id: UUID,
        user_id: UUID,
        goal_data: GoalUpdate,
    ) -> Optional[Goal]:
        """Update a goal."""
        goal = await self.repo.get_by_id_and_user(goal_id, user_id)
        if not goal:
            return None

        update_data = goal_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(goal, field, value)
        goal.updated_at = datetime.utcnow()

        # Check if completed via status update
        if goal_data.status == GoalStatus.completed and goal.completed_at is None:
            goal.completed_at = datetime.utcnow()

        return await self.repo.update(goal_id, goal_data)

    async def delete(
        self,
        goal_id: UUID,
        user_id: UUID,
    ) -> bool:
        """Delete a goal."""
        goal = await self.repo.get_by_id_and_user(goal_id, user_id)
        if not goal:
            return False

        return await self.repo.delete(goal_id)

    async def add_progress(
        self,
        goal_id: UUID,
        user_id: UUID,
        amount: float,
    ) -> Optional[Goal]:
        """Add progress to a goal."""
        goal = await self.repo.get_by_id_and_user(goal_id, user_id)
        if not goal:
            return None

        return await self.repo.update_progress(goal_id, amount)

    async def mark_completed(
        self,
        goal_id: UUID,
        user_id: UUID,
    ) -> Optional[Goal]:
        """Mark a goal as completed."""
        return await self.repo.mark_completed(goal_id, user_id)

    async def get_summary(self, user_id: UUID) -> dict:
        """Get goals summary for a user."""
        active_count = await self.repo.count_by_user(user_id, GoalStatus.active)
        completed_count = await self.repo.count_by_user(user_id, GoalStatus.completed)
        total_saved = await self.repo.get_total_saved(user_id)
        near_completion = await self.repo.get_near_completion(user_id)

        return {
            "active_goals": active_count,
            "completed_goals": completed_count,
            "total_saved": total_saved,
            "near_completion": [
                {
                    "id": str(g.id),
                    "name": g.name,
                    "emoji": g.emoji,
                    "percentage": round(
                        float(g.current_amount) / float(g.target_amount) * 100, 1
                    ),
                }
                for g in near_completion
            ],
        }
