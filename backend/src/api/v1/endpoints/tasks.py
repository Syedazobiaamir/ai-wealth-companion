"""Task API endpoints."""

from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.deps import CurrentUser, get_db
from src.models.task import TaskCreate, TaskRead, TaskUpdate, TaskPriority, TaskCategory
from src.services.task import TaskService

router = APIRouter()


class TaskSummaryResponse(BaseModel):
    """Response schema for tasks summary."""

    total_tasks: int
    active_tasks: int
    completed_tasks: int
    overdue_count: int
    due_soon_count: int
    overdue_tasks: List[dict]
    due_soon_tasks: List[dict]


@router.get(
    "",
    response_model=List[TaskRead],
    summary="List tasks",
    description="Get all tasks for the current user with optional filters.",
)
async def list_tasks(
    current_user: CurrentUser,
    is_completed: Optional[bool] = Query(None, alias="completed"),
    priority: Optional[TaskPriority] = Query(None),
    category: Optional[TaskCategory] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    session: AsyncSession = Depends(get_db),
) -> List[TaskRead]:
    """Get all tasks for the authenticated user."""
    service = TaskService(session)
    tasks = await service.get_all(
        user_id=current_user.id,
        is_completed=is_completed,
        priority=priority,
        category=category,
        skip=skip,
        limit=limit,
    )
    return [TaskRead.model_validate(t) for t in tasks]


@router.get(
    "/active",
    response_model=List[TaskRead],
    summary="List active tasks",
    description="Get all active (incomplete) tasks for the current user.",
)
async def list_active_tasks(
    current_user: CurrentUser,
    session: AsyncSession = Depends(get_db),
) -> List[TaskRead]:
    """Get all active tasks."""
    service = TaskService(session)
    tasks = await service.get_active(current_user.id)
    return [TaskRead.model_validate(t) for t in tasks]


@router.get(
    "/overdue",
    response_model=List[TaskRead],
    summary="List overdue tasks",
    description="Get all overdue tasks for the current user.",
)
async def list_overdue_tasks(
    current_user: CurrentUser,
    session: AsyncSession = Depends(get_db),
) -> List[TaskRead]:
    """Get all overdue tasks."""
    service = TaskService(session)
    tasks = await service.get_overdue(current_user.id)
    return [TaskRead.model_validate(t) for t in tasks]


@router.get(
    "/summary",
    response_model=TaskSummaryResponse,
    summary="Get tasks summary",
    description="Get summary statistics for user's tasks.",
)
async def get_tasks_summary(
    current_user: CurrentUser,
    session: AsyncSession = Depends(get_db),
) -> TaskSummaryResponse:
    """Get tasks summary."""
    service = TaskService(session)
    summary = await service.get_summary(current_user.id)
    return TaskSummaryResponse(**summary)


@router.get(
    "/{task_id}",
    response_model=TaskRead,
    summary="Get task by ID",
    description="Get a specific task by its UUID.",
)
async def get_task(
    task_id: UUID,
    current_user: CurrentUser,
    session: AsyncSession = Depends(get_db),
) -> TaskRead:
    """Get a task by ID."""
    service = TaskService(session)
    task = await service.get_by_id(task_id, current_user.id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task with ID {task_id} not found",
        )
    return TaskRead.model_validate(task)


@router.post(
    "",
    response_model=TaskRead,
    status_code=status.HTTP_201_CREATED,
    summary="Create task",
    description="Create a new financial task.",
)
async def create_task(
    task_data: TaskCreate,
    current_user: CurrentUser,
    session: AsyncSession = Depends(get_db),
) -> TaskRead:
    """Create a new task."""
    service = TaskService(session)
    task = await service.create(current_user.id, task_data)
    return TaskRead.model_validate(task)


@router.put(
    "/{task_id}",
    response_model=TaskRead,
    summary="Update task",
    description="Update an existing task.",
)
async def update_task(
    task_id: UUID,
    task_data: TaskUpdate,
    current_user: CurrentUser,
    session: AsyncSession = Depends(get_db),
) -> TaskRead:
    """Update a task."""
    service = TaskService(session)
    task = await service.update(task_id, current_user.id, task_data)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task with ID {task_id} not found",
        )
    return TaskRead.model_validate(task)


@router.delete(
    "/{task_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete task",
    description="Delete a task.",
)
async def delete_task(
    task_id: UUID,
    current_user: CurrentUser,
    session: AsyncSession = Depends(get_db),
) -> None:
    """Delete a task."""
    service = TaskService(session)
    deleted = await service.delete(task_id, current_user.id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task with ID {task_id} not found",
        )


@router.post(
    "/{task_id}/toggle",
    response_model=TaskRead,
    summary="Toggle task completion",
    description="Toggle task completion status. For recurring tasks, creates the next occurrence.",
)
async def toggle_task_completion(
    task_id: UUID,
    current_user: CurrentUser,
    session: AsyncSession = Depends(get_db),
) -> TaskRead:
    """Toggle task completion."""
    service = TaskService(session)
    task = await service.toggle_complete(task_id, current_user.id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task with ID {task_id} not found",
        )
    return TaskRead.model_validate(task)
