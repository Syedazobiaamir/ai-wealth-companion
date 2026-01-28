"""Goal API endpoints."""

from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.deps import CurrentUser, get_db
from src.models.goal import GoalCreate, GoalRead, GoalStatus, GoalUpdate
from src.services.goal import GoalService

router = APIRouter()


class GoalProgressRequest(BaseModel):
    """Request schema for adding goal progress."""

    amount: float


class GoalSummaryResponse(BaseModel):
    """Response schema for goals summary."""

    active_goals: int
    completed_goals: int
    total_saved: float
    near_completion: List[dict]


@router.get(
    "",
    response_model=List[GoalRead],
    summary="List goals",
    description="Get all goals for the current user.",
)
async def list_goals(
    current_user: CurrentUser,
    status_filter: Optional[GoalStatus] = Query(None, alias="status"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    session: AsyncSession = Depends(get_db),
) -> List[GoalRead]:
    """Get all goals for the authenticated user."""
    service = GoalService(session)
    goals = await service.get_all(
        user_id=current_user.id,
        status=status_filter,
        skip=skip,
        limit=limit,
    )
    return [GoalRead.model_validate(g) for g in goals]


@router.get(
    "/active",
    response_model=List[GoalRead],
    summary="List active goals",
    description="Get all active goals for the current user.",
)
async def list_active_goals(
    current_user: CurrentUser,
    session: AsyncSession = Depends(get_db),
) -> List[GoalRead]:
    """Get all active goals."""
    service = GoalService(session)
    goals = await service.get_active(current_user.id)
    return [GoalRead.model_validate(g) for g in goals]


@router.get(
    "/summary",
    response_model=GoalSummaryResponse,
    summary="Get goals summary",
    description="Get summary statistics for user's goals.",
)
async def get_goals_summary(
    current_user: CurrentUser,
    session: AsyncSession = Depends(get_db),
) -> GoalSummaryResponse:
    """Get goals summary."""
    service = GoalService(session)
    summary = await service.get_summary(current_user.id)
    return GoalSummaryResponse(**summary)


@router.get(
    "/{goal_id}",
    response_model=GoalRead,
    summary="Get goal by ID",
    description="Get a specific goal by its UUID.",
)
async def get_goal(
    goal_id: UUID,
    current_user: CurrentUser,
    session: AsyncSession = Depends(get_db),
) -> GoalRead:
    """Get a goal by ID."""
    service = GoalService(session)
    goal = await service.get_by_id(goal_id, current_user.id)
    if not goal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Goal with ID {goal_id} not found",
        )
    return GoalRead.model_validate(goal)


@router.post(
    "",
    response_model=GoalRead,
    status_code=status.HTTP_201_CREATED,
    summary="Create goal",
    description="Create a new financial goal.",
)
async def create_goal(
    goal_data: GoalCreate,
    current_user: CurrentUser,
    session: AsyncSession = Depends(get_db),
) -> GoalRead:
    """Create a new goal."""
    service = GoalService(session)
    goal = await service.create(current_user.id, goal_data)
    return GoalRead.model_validate(goal)


@router.put(
    "/{goal_id}",
    response_model=GoalRead,
    summary="Update goal",
    description="Update an existing goal.",
)
async def update_goal(
    goal_id: UUID,
    goal_data: GoalUpdate,
    current_user: CurrentUser,
    session: AsyncSession = Depends(get_db),
) -> GoalRead:
    """Update a goal."""
    service = GoalService(session)
    goal = await service.update(goal_id, current_user.id, goal_data)
    if not goal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Goal with ID {goal_id} not found",
        )
    return GoalRead.model_validate(goal)


@router.delete(
    "/{goal_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete goal",
    description="Delete a goal.",
)
async def delete_goal(
    goal_id: UUID,
    current_user: CurrentUser,
    session: AsyncSession = Depends(get_db),
) -> None:
    """Delete a goal."""
    service = GoalService(session)
    deleted = await service.delete(goal_id, current_user.id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Goal with ID {goal_id} not found",
        )


@router.post(
    "/{goal_id}/progress",
    response_model=GoalRead,
    summary="Add progress to goal",
    description="Add an amount to the goal's current progress.",
)
async def add_goal_progress(
    goal_id: UUID,
    progress_data: GoalProgressRequest,
    current_user: CurrentUser,
    session: AsyncSession = Depends(get_db),
) -> GoalRead:
    """Add progress to a goal."""
    service = GoalService(session)
    goal = await service.add_progress(
        goal_id, current_user.id, progress_data.amount
    )
    if not goal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Goal with ID {goal_id} not found",
        )
    return GoalRead.model_validate(goal)


@router.post(
    "/{goal_id}/complete",
    response_model=GoalRead,
    summary="Mark goal as completed",
    description="Mark a goal as completed.",
)
async def complete_goal(
    goal_id: UUID,
    current_user: CurrentUser,
    session: AsyncSession = Depends(get_db),
) -> GoalRead:
    """Mark a goal as completed."""
    service = GoalService(session)
    goal = await service.mark_completed(goal_id, current_user.id)
    if not goal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Goal with ID {goal_id} not found",
        )
    return GoalRead.model_validate(goal)
