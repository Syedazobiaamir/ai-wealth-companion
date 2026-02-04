"""MCP tool: get_financial_summary — wraps DashboardService."""

from typing import Any, Dict
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from src.services.dashboard import DashboardService


async def get_financial_summary(
    user_id: UUID,
    session: AsyncSession,
    period: str = "month",
) -> Dict[str, Any]:
    """Get user's financial overview for the given period."""
    service = DashboardService(session)
    summary = await service.get_summary(user_id=user_id, period=period)
    data = summary.get("data", {})
    totals = data.get("totals", {})
    comparison = data.get("comparison", {})
    top_cats = data.get("top_categories", [])

    return {
        "income": totals.get("income", 0),
        "expenses": totals.get("expenses", 0),
        "net": totals.get("net", 0),
        "savings_rate": totals.get("savings_rate", 0),
        "trend": comparison.get("trend", "stable"),
        "income_change_pct": comparison.get("income_change", 0),
        "expense_change_pct": comparison.get("expense_change", 0),
        "top_categories": [
            {
                "name": c["category"]["name"],
                "amount": c["amount"],
                "percentage": c["percentage"],
            }
            for c in top_cats
        ],
        "period": period,
    }
