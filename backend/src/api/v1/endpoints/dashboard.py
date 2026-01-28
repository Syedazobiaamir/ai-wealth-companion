"""Dashboard API endpoints."""

from datetime import date
from typing import Any, Dict, Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.deps import CurrentUser, get_db
from src.services.dashboard import DashboardService

router = APIRouter()


@router.get(
    "/summary",
    response_model=Dict[str, Any],
    summary="Get dashboard summary",
    description="Get financial overview for dashboard.",
)
async def get_dashboard_summary(
    current_user: CurrentUser,
    period: str = Query("month", description="Period: week, month, year, custom"),
    start_date: Optional[date] = Query(None, description="Custom period start"),
    end_date: Optional[date] = Query(None, description="Custom period end"),
    session: AsyncSession = Depends(get_db),
) -> Dict[str, Any]:
    """Get dashboard summary with totals and comparisons."""
    service = DashboardService(session)
    return await service.get_summary(
        user_id=current_user.id,
        period=period,
        start_date=start_date,
        end_date=end_date,
    )


@router.get(
    "/charts/spending-by-category",
    response_model=Dict[str, Any],
    summary="Get category breakdown chart",
    description="Get data for category breakdown pie chart.",
)
async def get_spending_by_category(
    current_user: CurrentUser,
    month: Optional[int] = Query(None, ge=1, le=12, description="Month (1-12)"),
    year: Optional[int] = Query(None, ge=2020, description="Year"),
    session: AsyncSession = Depends(get_db),
) -> Dict[str, Any]:
    """Get spending by category for pie chart."""
    service = DashboardService(session)
    return await service.get_spending_by_category(
        user_id=current_user.id,
        month=month,
        year=year,
    )


@router.get(
    "/charts/spending-trend",
    response_model=Dict[str, Any],
    summary="Get spending trend chart",
    description="Get data for spending trend line chart.",
)
async def get_spending_trend(
    current_user: CurrentUser,
    months: int = Query(6, ge=1, le=12, description="Number of months"),
    session: AsyncSession = Depends(get_db),
) -> Dict[str, Any]:
    """Get spending trend over months."""
    service = DashboardService(session)
    return await service.get_spending_trend(
        user_id=current_user.id,
        months=months,
    )
