"""Demo mode API endpoints."""

from typing import Any, Dict

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.deps import CurrentUser, get_db
from src.services.demo import DemoService

router = APIRouter()


@router.post(
    "/seed",
    response_model=Dict[str, Any],
    summary="Seed demo data",
    description="Generate comprehensive demo data for the current user.",
)
async def seed_demo_data(
    current_user: CurrentUser,
    months: int = Query(6, ge=1, le=12, description="Number of months of data to generate"),
    session: AsyncSession = Depends(get_db),
) -> Dict[str, Any]:
    """Generate demo data for testing and demonstration."""
    service = DemoService(session)
    return await service.seed_demo_data(
        user_id=current_user.id,
        months=months,
    )


@router.post(
    "/reset",
    response_model=Dict[str, Any],
    summary="Reset demo data",
    description="Clear all demo data for the current user.",
)
async def reset_demo_data(
    current_user: CurrentUser,
    session: AsyncSession = Depends(get_db),
) -> Dict[str, Any]:
    """Reset/clear demo data."""
    service = DemoService(session)
    return await service.reset_demo_data(current_user.id)
