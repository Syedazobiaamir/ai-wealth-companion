"""Summary API endpoints for financial aggregations."""

from datetime import date
from typing import List, Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.deps import CurrentUser, get_db
from src.models.summary import (
    CategorySummary,
    DashboardSummary,
    FinancialSummary,
    MonthlyTrend,
)
from src.models.transaction import TransactionType
from src.services.summary import SummaryService

router = APIRouter()


def get_default_start_date() -> date:
    """Get first day of current month."""
    today = date.today()
    return date(today.year, today.month, 1)


def get_default_end_date() -> date:
    """Get today's date."""
    return date.today()


@router.get(
    "/financial",
    response_model=FinancialSummary,
    summary="Get financial summary",
    description="Get total income, expense, and net balance for a date range.",
)
async def get_financial_summary(
    current_user: CurrentUser,
    start_date: date = Query(default_factory=get_default_start_date),
    end_date: date = Query(default_factory=get_default_end_date),
    session: AsyncSession = Depends(get_db),
) -> FinancialSummary:
    """Get financial summary."""
    service = SummaryService(session)
    return await service.get_financial_summary(current_user.id, start_date, end_date)


@router.get(
    "/categories",
    response_model=List[CategorySummary],
    summary="Get category breakdown",
    description="Get spending/income breakdown by category.",
)
async def get_category_breakdown(
    current_user: CurrentUser,
    start_date: date = Query(default_factory=get_default_start_date),
    end_date: date = Query(default_factory=get_default_end_date),
    type: Optional[TransactionType] = Query(
        TransactionType.expense,
        description="Transaction type to summarize",
    ),
    session: AsyncSession = Depends(get_db),
) -> List[CategorySummary]:
    """Get category breakdown."""
    service = SummaryService(session)
    return await service.get_category_breakdown(current_user.id, start_date, end_date, type)


@router.get(
    "/trends",
    response_model=List[MonthlyTrend],
    summary="Get monthly trends",
    description="Get monthly income/expense trends for a year.",
)
async def get_monthly_trends(
    current_user: CurrentUser,
    year: int = Query(default_factory=lambda: date.today().year, ge=2020),
    session: AsyncSession = Depends(get_db),
) -> List[MonthlyTrend]:
    """Get monthly trends."""
    service = SummaryService(session)
    return await service.get_monthly_trends(current_user.id, year)


@router.get(
    "/dashboard",
    response_model=DashboardSummary,
    summary="Get dashboard summary",
    description="Get complete dashboard data including summary, categories, trends, and alerts.",
)
async def get_dashboard_summary(
    current_user: CurrentUser,
    start_date: date = Query(default_factory=get_default_start_date),
    end_date: date = Query(default_factory=get_default_end_date),
    include_trends: bool = Query(True, description="Include monthly trends"),
    session: AsyncSession = Depends(get_db),
) -> DashboardSummary:
    """Get complete dashboard summary."""
    service = SummaryService(session)
    return await service.get_dashboard_summary(
        current_user.id, start_date, end_date, include_trends
    )
