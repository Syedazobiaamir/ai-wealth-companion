"""Spending Insight skill — smart summaries with category breakdown."""

from typing import Any, Dict
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from src.mcp.tools.spending_analysis import analyze_spending
from src.mcp.tools.financial_summary import get_financial_summary


async def generate_spending_insight(
    user_id: UUID,
    session: AsyncSession,
    period: str = "month",
    category: str = None,
) -> Dict[str, Any]:
    """Generate a comprehensive spending insight."""
    summary = await get_financial_summary(user_id=user_id, session=session, period=period)
    analysis = await analyze_spending(user_id=user_id, session=session, period=period, category=category)

    income = summary.get("income", 0)
    expenses = summary.get("expenses", 0)
    savings_rate = summary.get("savings_rate", 0)
    trend = summary.get("trend", "stable")
    categories = analysis.get("categories", [])

    insights = []
    if savings_rate < 10:
        insights.append("Your savings rate is critically low. Consider cutting non-essential expenses.")
    elif savings_rate < 20:
        insights.append("Your savings rate is below the recommended 20%. Small reductions can help.")
    else:
        insights.append(f"Good savings rate at {savings_rate:.0f}%. Keep it up!")

    if trend == "increasing":
        insights.append("Your spending is trending upward. Review recent transactions for unnecessary expenses.")
    elif trend == "decreasing":
        insights.append("Great — your spending is trending downward!")

    top_cat = categories[0] if categories else None
    if top_cat:
        insights.append(f"Your top expense category is {top_cat.get('category', 'Unknown')}.")

    return {
        "income": income,
        "expenses": expenses,
        "savings_rate": savings_rate,
        "trend": trend,
        "top_categories": categories[:5],
        "insights": insights,
        "period": period,
    }
