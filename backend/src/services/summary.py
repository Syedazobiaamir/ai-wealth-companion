"""Summary service for financial aggregations."""

from datetime import date
from decimal import Decimal
from typing import List, Optional
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from src.models.summary import (
    CategorySummary,
    DashboardSummary,
    FinancialSummary,
    MonthlyTrend,
)
from src.models.transaction import TransactionType
from src.repositories.transaction import TransactionRepository
from src.repositories.budget import BudgetRepository


class SummaryService:
    """Service for financial summary operations."""

    def __init__(self, session: AsyncSession):
        self.transaction_repo = TransactionRepository(session)
        self.budget_repo = BudgetRepository(session)

    async def get_financial_summary(
        self,
        user_id: UUID,
        start_date: date,
        end_date: date,
    ) -> FinancialSummary:
        """Get financial summary for a date range."""
        totals = await self.transaction_repo.get_totals_by_type(
            user_id, start_date, end_date
        )

        total_income = totals.get(TransactionType.income, Decimal("0"))
        total_expense = totals.get(TransactionType.expense, Decimal("0"))
        net_balance = total_income - total_expense

        return FinancialSummary(
            total_income=total_income,
            total_expense=total_expense,
            net_balance=net_balance,
            period_start=start_date,
            period_end=end_date,
        )

    async def get_category_breakdown(
        self,
        user_id: UUID,
        start_date: date,
        end_date: date,
        transaction_type: Optional[TransactionType] = TransactionType.expense,
    ) -> List[CategorySummary]:
        """Get spending breakdown by category."""
        category_totals = await self.transaction_repo.get_totals_by_category(
            user_id, start_date, end_date, transaction_type
        )

        # Calculate total for percentages
        total = sum(c["total"] for c in category_totals)

        return [
            CategorySummary(
                category_id=c["category_id"],
                category_name=c["category_name"],
                category_emoji=c["category_emoji"],
                total_amount=c["total"],
                transaction_count=c["count"],
                percentage_of_total=(
                    round(c["total"] / total * 100, 2) if total > 0 else Decimal("0")
                ),
            )
            for c in category_totals
        ]

    async def get_monthly_trends(
        self,
        user_id: UUID,
        year: int,
    ) -> List[MonthlyTrend]:
        """Get monthly income/expense trends for a year."""
        monthly_data = await self.transaction_repo.get_monthly_totals(user_id, year)

        return [
            MonthlyTrend(
                month=m["month"],
                year=m["year"],
                total_income=m["income"],
                total_expense=m["expense"],
                net=m["income"] - m["expense"],
            )
            for m in monthly_data
        ]

    async def get_dashboard_summary(
        self,
        user_id: UUID,
        start_date: date,
        end_date: date,
        include_trends: bool = True,
    ) -> DashboardSummary:
        """Get complete dashboard summary data."""
        # Get financial summary
        financial_summary = await self.get_financial_summary(user_id, start_date, end_date)

        # Get category breakdown
        category_breakdown = await self.get_category_breakdown(
            user_id, start_date, end_date, TransactionType.expense
        )

        # Get monthly trends if requested
        monthly_trends = None
        if include_trends:
            monthly_trends = await self.get_monthly_trends(user_id, start_date.year)

        # Get budget alerts
        budget_alerts = []
        exceeded = await self.budget_repo.get_exceeded_budgets(
            user_id, end_date.month, end_date.year
        )
        warnings = await self.budget_repo.get_warning_budgets(
            user_id, end_date.month, end_date.year
        )

        for b in exceeded:
            budget_alerts.append(
                f"{b['emoji']} {b['category']} budget exceeded: "
                f"PKR {b['spent']:.2f} / PKR {b['limit']:.2f}"
            )
        for b in warnings:
            budget_alerts.append(
                f"{b['emoji']} {b['category']} budget at {b['percentage']:.0f}%: "
                f"PKR {b['spent']:.2f} / PKR {b['limit']:.2f}"
            )

        return DashboardSummary(
            financial_summary=financial_summary,
            category_breakdown=category_breakdown,
            monthly_trends=monthly_trends,
            budget_alerts=budget_alerts if budget_alerts else None,
        )
