"""Task repository for database operations."""

from datetime import datetime
from typing import List, Optional
from uuid import UUID

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.task import Task, TaskCreate, TaskUpdate, TaskPriority, TaskCategory
from src.repositories.base import BaseRepository


class TaskRepository(BaseRepository[Task, TaskCreate, TaskUpdate]):
    """Repository for task database operations."""

    def __init__(self, session: AsyncSession):
        super().__init__(Task, session)

    async def get_by_user(
        self,
        user_id: UUID,
        is_completed: Optional[bool] = None,
        priority: Optional[TaskPriority] = None,
        category: Optional[TaskCategory] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> List[Task]:
        """Get all tasks for a user with optional filters."""
        statement = select(Task).where(Task.user_id == user_id)

        if is_completed is not None:
            statement = statement.where(Task.is_completed == is_completed)
        if priority:
            statement = statement.where(Task.priority == priority)
        if category:
            statement = statement.where(Task.category == category)

        # Order by: incomplete first, then by due_date (nulls last), then priority
        statement = statement.order_by(
            Task.is_completed.asc(),
            Task.due_date.asc().nulls_last(),
            Task.created_at.desc()
        )
        statement = statement.offset(skip).limit(limit)

        result = await self.session.execute(statement)
        return list(result.scalars().all())

    async def get_by_id_and_user(
        self,
        task_id: UUID,
        user_id: UUID,
    ) -> Optional[Task]:
        """Get a task by ID for a specific user."""
        statement = select(Task).where(
            Task.id == task_id,
            Task.user_id == user_id,
        )
        result = await self.session.execute(statement)
        return result.scalar_one_or_none()

    async def get_active(self, user_id: UUID) -> List[Task]:
        """Get all active (incomplete) tasks for a user."""
        return await self.get_by_user(user_id, is_completed=False)

    async def get_overdue(self, user_id: UUID) -> List[Task]:
        """Get overdue tasks for a user."""
        today = datetime.utcnow().date()
        statement = select(Task).where(
            Task.user_id == user_id,
            Task.is_completed == False,
            Task.due_date < today,
        ).order_by(Task.due_date.asc())

        result = await self.session.execute(statement)
        return list(result.scalars().all())

    async def create_with_user(
        self,
        user_id: UUID,
        task_data: TaskCreate,
    ) -> Task:
        """Create a task for a user."""
        task = Task(
            user_id=user_id,
            title=task_data.title,
            description=task_data.description,
            priority=task_data.priority,
            category=task_data.category,
            due_date=task_data.due_date,
            is_recurring=task_data.is_recurring,
            recurring_frequency=task_data.recurring_frequency,
        )
        self.session.add(task)
        await self.session.flush()
        await self.session.refresh(task)
        return task

    async def toggle_complete(
        self,
        task_id: UUID,
        user_id: UUID,
    ) -> Optional[Task]:
        """Toggle task completion status."""
        task = await self.get_by_id_and_user(task_id, user_id)
        if not task:
            return None

        task.is_completed = not task.is_completed
        task.updated_at = datetime.utcnow()

        if task.is_completed:
            task.completed_at = datetime.utcnow()
        else:
            task.completed_at = None

        self.session.add(task)
        await self.session.flush()
        await self.session.refresh(task)
        return task

    async def count_by_user(
        self,
        user_id: UUID,
        is_completed: Optional[bool] = None,
    ) -> int:
        """Count tasks for a user."""
        statement = select(func.count()).select_from(Task).where(
            Task.user_id == user_id
        )
        if is_completed is not None:
            statement = statement.where(Task.is_completed == is_completed)
        result = await self.session.execute(statement)
        return result.scalar_one()

    async def get_due_soon(
        self,
        user_id: UUID,
        days: int = 3,
    ) -> List[Task]:
        """Get tasks due within the next N days."""
        from datetime import timedelta

        today = datetime.utcnow().date()
        future_date = today + timedelta(days=days)

        statement = select(Task).where(
            Task.user_id == user_id,
            Task.is_completed == False,
            Task.due_date >= today,
            Task.due_date <= future_date,
        ).order_by(Task.due_date.asc())

        result = await self.session.execute(statement)
        return list(result.scalars().all())
