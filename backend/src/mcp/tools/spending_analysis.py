"""MCP tool: analyze_spending — wraps SummaryService."""

from typing import Any, Dict, Optional
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from src.services.summary import SummaryService


async def analyze_spending(
    user_id: UUID,
    session: AsyncSession,
    period: str = "month",
    category: Optional[str] = None,
) -> Dict[str, Any]:
    """Analyze spending patterns with trends and comparisons."""
    service = SummaryService(session)
    financial = await service.get_financial_summary(user_id=user_id)
    categories = await service.get_category_breakdown(user_id=user_id)
    trends = await service.get_monthly_trends(user_id=user_id)

    fin_data = financial.get("data", {})
    cat_data = categories.get("data", [])
    trend_data = trends.get("data", [])

    # Filter by category if specified
    if category:
        cat_data = [
            c for c in cat_data
            if category.lower() in c.get("category", "").lower()
        ]

    return {
        "total_income": fin_data.get("total_income", 0),
        "total_expenses": fin_data.get("total_expenses", 0),
        "net": fin_data.get("net", 0),
        "savings_rate": fin_data.get("savings_rate", 0),
        "categories": cat_data[:10],
        "monthly_trends": trend_data[-6:] if trend_data else [],
        "period": period,
        "analysis_note": (
            f"Focused on '{category}' category." if category
            else "Full spending analysis across all categories."
        ),
    }
