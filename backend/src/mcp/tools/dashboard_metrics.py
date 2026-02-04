"""MCP tool: generate_dashboard_metrics — data for AI insight cards."""

from typing import Any, Dict
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from src.services.dashboard import DashboardService
from src.services.ai import AIService


async def generate_dashboard_metrics(
    user_id: UUID,
    session: AsyncSession,
) -> Dict[str, Any]:
    """Get dashboard data including alerts and recommendations."""
    dashboard = DashboardService(session)
    ai = AIService(session)

    summary = await dashboard.get_summary(user_id=user_id, period="month")
    context = await ai.get_user_context(user_id)

    data = summary.get("data", {})
    budgets = data.get("budgets_summary", {})
    ctx = context.get("data", {})
    active_budgets = ctx.get("active_budgets", [])
    patterns = ctx.get("recent_patterns", {})

    # Generate alerts from budget status
    alerts = []
    for b in active_budgets:
        if b.get("status") == "exceeded":
            alerts.append({
                "type": "budget_exceeded",
                "severity": "alert",
                "message": f"{b['emoji']} {b['category']} budget exceeded: {b['spent']:,.0f} / {b['limit']:,.0f}",
            })
        elif b.get("status") == "warning":
            alerts.append({
                "type": "budget_warning",
                "severity": "warning",
                "message": f"{b['emoji']} {b['category']} budget at warning level: {b['spent']:,.0f} / {b['limit']:,.0f}",
            })

    # Generate recommendations
    recommendations = []
    totals = data.get("totals", {})
    if totals.get("savings_rate", 0) < 20:
        recommendations.append("Your savings rate is below 20%. Consider reducing discretionary spending.")
    if budgets.get("exceeded", 0) > 0:
        recommendations.append(f"{budgets['exceeded']} budget(s) exceeded. Review spending in those categories.")
    trend = patterns.get("spending_trend", "stable")
    if trend == "increasing":
        recommendations.append("Your spending is trending upward compared to last month.")

    return {
        "summary": totals,
        "budgets": budgets,
        "alerts": alerts,
        "recommendations": recommendations,
        "spending_trend": trend,
        "top_category": patterns.get("top_expense_category"),
    }
