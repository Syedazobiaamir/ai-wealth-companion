"""Summary models for financial aggregations."""

from datetime import date
from decimal import Decimal
from typing import List, Optional

from sqlmodel import SQLModel


class FinancialSummary(SQLModel):
    """Aggregated financial totals for a period."""

    total_income: Decimal
    total_expense: Decimal
    net_balance: Decimal
    period_start: date
    period_end: date


class CategorySummary(SQLModel):
    """Spending summary by category."""

    category_id: str
    category_name: str
    category_emoji: str
    total_amount: Decimal
    transaction_count: int
    percentage_of_total: Decimal


class MonthlyTrend(SQLModel):
    """Monthly spending/income trend data point."""

    month: int
    year: int
    total_income: Decimal
    total_expense: Decimal
    net: Decimal


class DashboardSummary(SQLModel):
    """Complete dashboard summary data."""

    financial_summary: FinancialSummary
    category_breakdown: List[CategorySummary]
    monthly_trends: Optional[List[MonthlyTrend]] = None
    budget_alerts: Optional[List[str]] = None
