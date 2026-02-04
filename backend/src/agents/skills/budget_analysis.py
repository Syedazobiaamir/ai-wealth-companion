"""Budget Analysis skill — compares spending vs budgets, detects overspending."""

from typing import Any, Dict, List
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from src.services.ai import AIService


async def analyze_budgets(
    user_id: UUID,
    session: AsyncSession,
) -> Dict[str, Any]:
    """Analyze all budgets and return coaching recommendations."""
    ai_service = AIService(session)
    context = await ai_service.get_user_context(user_id)
    budgets = context.get("data", {}).get("active_budgets", [])

    exceeded = [b for b in budgets if b.get("status") == "exceeded"]
    warning = [b for b in budgets if b.get("status") == "warning"]
    normal = [b for b in budgets if b.get("status") == "normal"]

    recommendations: List[str] = []
    for b in exceeded:
        overspend = b["spent"] - b["limit"]
        recommendations.append(
            f"Cut {b['category']} spending by {overspend:,.0f} to get back on track."
        )
    for b in warning:
        remaining = b["limit"] - b["spent"]
        recommendations.append(
            f"Watch {b['category']} — only {remaining:,.0f} remaining this month."
        )

    if not budgets:
        recommendations.append("You have no budgets set. Consider creating budgets for your top spending categories.")

    return {
        "total_budgets": len(budgets),
        "exceeded": len(exceeded),
        "warning": len(warning),
        "on_track": len(normal),
        "exceeded_budgets": exceeded,
        "warning_budgets": warning,
        "recommendations": recommendations,
        "coaching": (
            "Your budgets are in good shape!" if not exceeded and not warning
            else f"Attention needed: {len(exceeded)} exceeded, {len(warning)} at warning level."
        ),
    }
