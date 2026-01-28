"""Task service for business logic."""

from datetime import datetime, timedelta
from typing import List, Optional
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from src.models.task import Task, TaskCreate, TaskUpdate, TaskPriority, TaskCategory, RecurringFrequency
from src.repositories.task import TaskRepository


class TaskService:
    """Service for task operations."""

    def __init__(self, session: AsyncSession):
        self.repo = TaskRepository(session)

    async def get_all(
        self,
        user_id: UUID,
        is_completed: Optional[bool] = None,
        priority: Optional[TaskPriority] = None,
        category: Optional[TaskCategory] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> List[Task]:
        """Get all tasks for a user."""
        return await self.repo.get_by_user(
            user_id, is_completed, priority, category, skip, limit
        )

    async def get_by_id(
        self,
        task_id: UUID,
        user_id: UUID,
    ) -> Optional[Task]:
        """Get a task by ID for a user."""
        return await self.repo.get_by_id_and_user(task_id, user_id)

    async def get_active(self, user_id: UUID) -> List[Task]:
        """Get all active tasks for a user."""
        return await self.repo.get_active(user_id)

    async def get_overdue(self, user_id: UUID) -> List[Task]:
        """Get overdue tasks for a user."""
        return await self.repo.get_overdue(user_id)

    async def create(
        self,
        user_id: UUID,
        task_data: TaskCreate,
    ) -> Task:
        """Create a new task."""
        return await self.repo.create_with_user(user_id, task_data)

    async def update(
        self,
        task_id: UUID,
        user_id: UUID,
        task_data: TaskUpdate,
    ) -> Optional[Task]:
        """Update a task."""
        task = await self.repo.get_by_id_and_user(task_id, user_id)
        if not task:
            return None

        update_data = task_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(task, field, value)
        task.updated_at = datetime.utcnow()

        # Handle completion status change
        if task_data.is_completed is True and task.completed_at is None:
            task.completed_at = datetime.utcnow()
        elif task_data.is_completed is False:
            task.completed_at = None

        return await self.repo.update(task_id, task_data)

    async def delete(
        self,
        task_id: UUID,
        user_id: UUID,
    ) -> bool:
        """Delete a task."""
        task = await self.repo.get_by_id_and_user(task_id, user_id)
        if not task:
            return False
        return await self.repo.delete(task_id)

    async def toggle_complete(
        self,
        task_id: UUID,
        user_id: UUID,
    ) -> Optional[Task]:
        """Toggle task completion and handle recurring tasks."""
        task = await self.repo.get_by_id_and_user(task_id, user_id)
        if not task:
            return None

        # Toggle completion
        updated_task = await self.repo.toggle_complete(task_id, user_id)

        # If completing a recurring task, create the next occurrence
        if updated_task and updated_task.is_completed and task.is_recurring and task.recurring_frequency:
            await self._create_next_recurring(user_id, task)

        return updated_task

    async def _create_next_recurring(
        self,
        user_id: UUID,
        original_task: Task,
    ) -> Task:
        """Create the next occurrence of a recurring task."""
        next_due = original_task.due_date or datetime.utcnow().date()

        if original_task.recurring_frequency == RecurringFrequency.daily:
            next_due = next_due + timedelta(days=1)
        elif original_task.recurring_frequency == RecurringFrequency.weekly:
            next_due = next_due + timedelta(weeks=1)
        elif original_task.recurring_frequency == RecurringFrequency.monthly:
            # Add approximately one month
            next_due = next_due + timedelta(days=30)

        new_task_data = TaskCreate(
            title=original_task.title,
            description=original_task.description,
            priority=original_task.priority,
            category=original_task.category,
            due_date=next_due,
            is_recurring=True,
            recurring_frequency=original_task.recurring_frequency,
        )

        return await self.repo.create_with_user(user_id, new_task_data)

    async def get_summary(self, user_id: UUID) -> dict:
        """Get tasks summary for a user."""
        total_count = await self.repo.count_by_user(user_id)
        active_count = await self.repo.count_by_user(user_id, is_completed=False)
        completed_count = await self.repo.count_by_user(user_id, is_completed=True)
        overdue_tasks = await self.repo.get_overdue(user_id)
        due_soon_tasks = await self.repo.get_due_soon(user_id, days=3)

        return {
            "total_tasks": total_count,
            "active_tasks": active_count,
            "completed_tasks": completed_count,
            "overdue_count": len(overdue_tasks),
            "due_soon_count": len(due_soon_tasks),
            "overdue_tasks": [
                {
                    "id": str(t.id),
                    "title": t.title,
                    "due_date": t.due_date.isoformat() if t.due_date else None,
                    "priority": t.priority,
                }
                for t in overdue_tasks[:5]  # Limit to 5
            ],
            "due_soon_tasks": [
                {
                    "id": str(t.id),
                    "title": t.title,
                    "due_date": t.due_date.isoformat() if t.due_date else None,
                    "priority": t.priority,
                }
                for t in due_soon_tasks[:5]  # Limit to 5
            ],
        }
