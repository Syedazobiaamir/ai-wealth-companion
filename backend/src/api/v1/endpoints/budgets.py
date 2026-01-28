"""Budget API endpoints."""

from datetime import date
from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.deps import CurrentUser, get_db
from src.models.budget import BudgetCreate, BudgetRead, BudgetStatus, BudgetUpdate
from src.services.budget import BudgetService
from src.services.category import CategoryService

router = APIRouter()


@router.get(
    "",
    response_model=List[BudgetRead],
    summary="List budgets for period",
    description="Get all budgets for a specific month and year.",
)
async def list_budgets(
    current_user: CurrentUser,
    month: int = Query(
        default_factory=lambda: date.today().month,
        ge=1,
        le=12,
        description="Month (1-12)",
    ),
    year: int = Query(
        default_factory=lambda: date.today().year,
        ge=2020,
        description="Year",
    ),
    session: AsyncSession = Depends(get_db),
) -> List[BudgetRead]:
    """Get all budgets for a period."""
    service = BudgetService(session)
    return await service.get_all_for_period(current_user.id, month, year)


@router.get(
    "/status",
    response_model=List[BudgetStatus],
    summary="Get budget status",
    description="Get all budgets with spending status for a period.",
)
async def get_budget_status(
    current_user: CurrentUser,
    month: int = Query(
        default_factory=lambda: date.today().month,
        ge=1,
        le=12,
    ),
    year: int = Query(
        default_factory=lambda: date.today().year,
        ge=2020,
    ),
    session: AsyncSession = Depends(get_db),
) -> List[BudgetStatus]:
    """Get budget status with spending."""
    service = BudgetService(session)
    return await service.get_status_for_period(current_user.id, month, year)


@router.get(
    "/alerts",
    response_model=dict,
    summary="Get budget alerts",
    description="Get budgets that are exceeded or at warning level.",
)
async def get_budget_alerts(
    current_user: CurrentUser,
    month: int = Query(
        default_factory=lambda: date.today().month,
        ge=1,
        le=12,
    ),
    year: int = Query(
        default_factory=lambda: date.today().year,
        ge=2020,
    ),
    session: AsyncSession = Depends(get_db),
) -> dict:
    """Get budget alerts."""
    service = BudgetService(session)
    exceeded = await service.get_exceeded(current_user.id, month, year)
    warnings = await service.get_warnings(current_user.id, month, year)
    return {
        "exceeded": exceeded,
        "warnings": warnings,
    }


@router.get(
    "/{budget_id}",
    response_model=BudgetRead,
    summary="Get budget by ID",
    description="Get a single budget by its UUID.",
)
async def get_budget(
    budget_id: UUID,
    current_user: CurrentUser,
    session: AsyncSession = Depends(get_db),
) -> BudgetRead:
    """Get a budget by ID."""
    service = BudgetService(session)
    budget = await service.get_by_id(current_user.id, budget_id)
    if not budget:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Budget with ID {budget_id} not found",
        )
    return budget


@router.post(
    "",
    response_model=BudgetRead,
    status_code=status.HTTP_201_CREATED,
    summary="Create or update budget",
    description="Create a new budget or update existing for category+period.",
)
async def create_budget(
    data: BudgetCreate,
    current_user: CurrentUser,
    session: AsyncSession = Depends(get_db),
) -> BudgetRead:
    """Create or update a budget."""
    # Validate category exists
    category_service = CategoryService(session)
    if not await category_service.exists(data.category_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Category with ID {data.category_id} not found",
        )

    service = BudgetService(session)
    return await service.create_or_update(
        user_id=current_user.id,
        category_id=data.category_id,
        month=data.month,
        year=data.year,
        limit_amount=data.limit_amount,
        alert_threshold=data.alert_threshold,
    )


@router.put(
    "/{budget_id}",
    response_model=BudgetRead,
    summary="Update budget",
    description="Update an existing budget.",
)
async def update_budget(
    budget_id: UUID,
    data: BudgetUpdate,
    current_user: CurrentUser,
    session: AsyncSession = Depends(get_db),
) -> BudgetRead:
    """Update a budget."""
    service = BudgetService(session)
    budget = await service.update(current_user.id, budget_id, data)
    if not budget:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Budget with ID {budget_id} not found",
        )
    return budget


@router.delete(
    "/{budget_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete budget",
    description="Delete a budget.",
)
async def delete_budget(
    budget_id: UUID,
    current_user: CurrentUser,
    session: AsyncSession = Depends(get_db),
) -> None:
    """Delete a budget."""
    service = BudgetService(session)
    deleted = await service.delete(current_user.id, budget_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Budget with ID {budget_id} not found",
        )
