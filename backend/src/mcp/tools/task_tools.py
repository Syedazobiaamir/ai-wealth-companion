"""MCP tools for task management — wraps TaskService for agent consumption."""

from datetime import date
from typing import Any, Dict, List, Optional
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from src.models.task import TaskCreate, TaskPriority, TaskCategory
from src.services.task import TaskService


async def create_task(
    user_id: UUID,
    session: AsyncSession,
    title: str,
    priority: str = "medium",
    category: str = "other",
    due_date: Optional[str] = None,
) -> Dict[str, Any]:
    """Create a new task via TaskService."""
    service = TaskService(session)

    # Resolve enums
    try:
        pri = TaskPriority(priority)
    except ValueError:
        pri = TaskPriority.medium

    try:
        cat = TaskCategory(category)
    except ValueError:
        cat = TaskCategory.other

    parsed_date: Optional[date] = None
    if due_date:
        try:
            parsed_date = date.fromisoformat(due_date)
        except ValueError:
            pass

    task_data = TaskCreate(
        title=title,
        priority=pri,
        category=cat,
        due_date=parsed_date,
    )

    task = await service.create(user_id, task_data)
    return {
        "message": f"Task created: {task.title}" + (f" (due {task.due_date})" if task.due_date else ""),
        "task_id": str(task.id),
        "title": task.title,
        "priority": task.priority,
        "category": task.category,
        "due_date": task.due_date.isoformat() if task.due_date else None,
    }


async def list_tasks(
    user_id: UUID,
    session: AsyncSession,
    status: str = "active",
) -> Dict[str, Any]:
    """List tasks filtered by status (active | overdue | all)."""
    service = TaskService(session)

    if status == "overdue":
        tasks = await service.get_overdue(user_id)
    elif status == "active":
        tasks = await service.get_active(user_id)
    else:
        tasks = await service.get_all(user_id)

    task_list = [
        {
            "id": str(t.id),
            "title": t.title,
            "priority": t.priority,
            "category": t.category,
            "due_date": t.due_date.isoformat() if t.due_date else None,
            "is_completed": t.is_completed,
        }
        for t in tasks
    ]

    return {
        "count": len(task_list),
        "status_filter": status,
        "tasks": task_list,
    }


async def get_task_summary(
    user_id: UUID,
    session: AsyncSession,
) -> Dict[str, Any]:
    """Get a summary of the user's tasks."""
    service = TaskService(session)
    return await service.get_summary(user_id)
