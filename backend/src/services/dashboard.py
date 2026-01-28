"""Dashboard service for aggregated financial data."""

from datetime import date, datetime, timedelta
from decimal import Decimal
from typing import Any, Dict, List, Optional
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.budget import Budget
from src.models.category import Category
from src.models.transaction import Transaction, TransactionType
from src.models.wallet import Wallet
from src.models.goal import Goal, GoalStatus


class DashboardService:
    """Service for dashboard aggregation operations."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_summary(
        self,
        user_id: UUID,
        period: str = "month",
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
    ) -> Dict[str, Any]:
        """Get dashboard summary with totals and comparisons."""
        # Determine date range
        if start_date and end_date:
            current_start = start_date
            current_end = end_date
        elif period == "week":
            today = date.today()
            current_start = today - timedelta(days=today.weekday())
            current_end = today
        elif period == "year":
            today = date.today()
            current_start = date(today.year, 1, 1)
            current_end = today
        else:  # month (default)
            today = date.today()
            current_start = date(today.year, today.month, 1)
            current_end = today

        # Calculate previous period for comparison
        period_days = (current_end - current_start).days + 1
        prev_start = current_start - timedelta(days=period_days)
        prev_end = current_start - timedelta(days=1)

        # Get current period totals
        current_income = await self._get_period_total(
            user_id, current_start, current_end, TransactionType.income
        )
        current_expenses = await self._get_period_total(
            user_id, current_start, current_end, TransactionType.expense
        )

        # Get previous period totals for comparison
        prev_income = await self._get_period_total(
            user_id, prev_start, prev_end, TransactionType.income
        )
        prev_expenses = await self._get_period_total(
            user_id, prev_start, prev_end, TransactionType.expense
        )

        # Calculate changes
        income_change = self._calc_percentage_change(prev_income, current_income)
        expense_change = self._calc_percentage_change(prev_expenses, current_expenses)

        net = current_income - current_expenses
        savings_rate = (net / current_income * 100) if current_income > 0 else 0

        # Determine trend
        if expense_change < -5:
            trend = "improving"
        elif expense_change > 5:
            trend = "worsening"
        else:
            trend = "stable"

        # Get top categories
        top_categories = await self._get_top_categories(
            user_id, current_start, current_end, limit=5
        )

        # Get recent transactions
        recent_transactions = await self._get_recent_transactions(
            user_id, limit=5
        )

        # Get budget summary
        budget_summary = await self._get_budget_summary(
            user_id, current_end.month, current_end.year
        )

        return {
            "success": True,
            "data": {
                "totals": {
                    "income": float(current_income),
                    "expenses": float(current_expenses),
                    "net": float(net),
                    "savings_rate": round(savings_rate, 1),
                },
                "comparison": {
                    "income_change": round(income_change, 1),
                    "expense_change": round(expense_change, 1),
                    "trend": trend,
                },
                "top_categories": top_categories,
                "recent_transactions": recent_transactions,
                "budgets_summary": budget_summary,
            },
            "meta": {
                "period": {
                    "start": current_start.isoformat(),
                    "end": current_end.isoformat(),
                    "type": period,
                },
                "cache_until": (
                    datetime.utcnow() + timedelta(minutes=5)
                ).isoformat() + "Z",
            },
        }

    async def get_spending_by_category(
        self,
        user_id: UUID,
        month: Optional[int] = None,
        year: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Get data for category breakdown pie chart."""
        today = date.today()
        month = month or today.month
        year = year or today.year

        start_date = date(year, month, 1)
        if month == 12:
            end_date = date(year + 1, 1, 1) - timedelta(days=1)
        else:
            end_date = date(year, month + 1, 1) - timedelta(days=1)

        # Query spending by category
        statement = (
            select(
                Category.name,
                Category.color,
                func.sum(Transaction.amount).label("total"),
            )
            .join(Transaction, Transaction.category_id == Category.id)
            .where(
                Transaction.user_id == user_id,
                Transaction.type == TransactionType.expense,
                Transaction.transaction_date >= start_date,
                Transaction.transaction_date <= end_date,
                Transaction.is_deleted == False,
            )
            .group_by(Category.id, Category.name, Category.color)
            .order_by(func.sum(Transaction.amount).desc())
        )
        result = await self.session.execute(statement)
        rows = result.all()

        labels = []
        data = []
        colors = []
        total = Decimal("0")

        for row in rows:
            labels.append(row.name)
            data.append(float(row.total))
            colors.append(row.color or "#888888")
            total += row.total

        return {
            "success": True,
            "data": {
                "chart_type": "pie",
                "labels": labels,
                "datasets": [
                    {
                        "data": data,
                        "colors": colors,
                    }
                ],
                "total": float(total),
            },
            "meta": {
                "period": f"{year}-{month:02d}",
            },
        }

    async def get_spending_trend(
        self,
        user_id: UUID,
        months: int = 6,
    ) -> Dict[str, Any]:
        """Get data for spending trend line chart."""
        today = date.today()
        labels = []
        income_data = []
        expense_data = []

        for i in range(months - 1, -1, -1):
            # Calculate month/year
            month_offset = (today.month - 1 - i) % 12 + 1
            year_offset = today.year - ((today.month - 1 - i) // 12 + (1 if i >= today.month else 0))

            if month_offset <= 0:
                month_offset += 12
                year_offset -= 1

            start_date = date(year_offset, month_offset, 1)
            if month_offset == 12:
                end_date = date(year_offset + 1, 1, 1) - timedelta(days=1)
            else:
                end_date = date(year_offset, month_offset + 1, 1) - timedelta(days=1)

            # Get month name
            labels.append(start_date.strftime("%b"))

            # Get totals
            income = await self._get_period_total(
                user_id, start_date, end_date, TransactionType.income
            )
            expense = await self._get_period_total(
                user_id, start_date, end_date, TransactionType.expense
            )

            income_data.append(float(income))
            expense_data.append(float(expense))

        return {
            "success": True,
            "data": {
                "chart_type": "line",
                "labels": labels,
                "datasets": [
                    {
                        "label": "Income",
                        "data": income_data,
                        "color": "#4CAF50",
                    },
                    {
                        "label": "Expenses",
                        "data": expense_data,
                        "color": "#FF6B6B",
                    },
                ],
            },
        }

    async def _get_period_total(
        self,
        user_id: UUID,
        start_date: date,
        end_date: date,
        transaction_type: TransactionType,
    ) -> Decimal:
        """Get total for a period and transaction type."""
        statement = select(func.coalesce(func.sum(Transaction.amount), 0)).where(
            Transaction.user_id == user_id,
            Transaction.type == transaction_type,
            Transaction.transaction_date >= start_date,
            Transaction.transaction_date <= end_date,
            Transaction.is_deleted == False,
        )
        result = await self.session.execute(statement)
        return result.scalar_one()

    async def _get_top_categories(
        self,
        user_id: UUID,
        start_date: date,
        end_date: date,
        limit: int = 5,
    ) -> List[Dict[str, Any]]:
        """Get top spending categories."""
        # Get total spending first
        total = await self._get_period_total(
            user_id, start_date, end_date, TransactionType.expense
        )

        statement = (
            select(
                Category.name,
                Category.emoji,
                func.sum(Transaction.amount).label("amount"),
            )
            .join(Transaction, Transaction.category_id == Category.id)
            .where(
                Transaction.user_id == user_id,
                Transaction.type == TransactionType.expense,
                Transaction.transaction_date >= start_date,
                Transaction.transaction_date <= end_date,
                Transaction.is_deleted == False,
            )
            .group_by(Category.id, Category.name, Category.emoji)
            .order_by(func.sum(Transaction.amount).desc())
            .limit(limit)
        )
        result = await self.session.execute(statement)
        rows = result.all()

        return [
            {
                "category": {
                    "name": row.name,
                    "emoji": row.emoji or "📦",
                },
                "amount": float(row.amount),
                "percentage": round(float(row.amount) / float(total) * 100, 1) if total > 0 else 0,
            }
            for row in rows
        ]

    async def _get_recent_transactions(
        self,
        user_id: UUID,
        limit: int = 5,
    ) -> List[Dict[str, Any]]:
        """Get recent transactions."""
        statement = (
            select(Transaction, Category.emoji)
            .join(Category, Transaction.category_id == Category.id)
            .where(
                Transaction.user_id == user_id,
                Transaction.is_deleted == False,
            )
            .order_by(Transaction.transaction_date.desc(), Transaction.created_at.desc())
            .limit(limit)
        )
        result = await self.session.execute(statement)
        rows = result.all()

        return [
            {
                "id": str(row.Transaction.id),
                "description": row.Transaction.note or "",
                "amount": float(row.Transaction.amount),
                "type": row.Transaction.type.value,
                "category_emoji": row.emoji or "📦",
                "transaction_date": row.Transaction.transaction_date.isoformat(),
            }
            for row in rows
        ]

    async def _get_budget_summary(
        self,
        user_id: UUID,
        month: int,
        year: int,
    ) -> Dict[str, Any]:
        """Get budget summary counts."""
        from src.repositories.budget import BudgetRepository

        repo = BudgetRepository(self.session)

        # Count budgets by status
        exceeded = await repo.get_exceeded_budgets(month, year)
        warnings = await repo.get_warning_budgets(month, year)

        # Get total budget count
        budgets = await repo.get_budgets_for_period(month, year)

        return {
            "total_budgets": len(budgets),
            "on_track": len(budgets) - len(exceeded) - len(warnings),
            "warning": len(warnings),
            "exceeded": len(exceeded),
        }

    def _calc_percentage_change(
        self,
        previous: Decimal,
        current: Decimal,
    ) -> float:
        """Calculate percentage change."""
        if previous == 0:
            return 100.0 if current > 0 else 0.0
        return float((current - previous) / previous * 100)
