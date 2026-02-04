"""MCP tool: simulate_investment — predictive investment projections."""

import math
from typing import Any, Dict
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from src.services.ai import AIService


DISCLAIMER = (
    "This is an educational simulation only. Past performance does not "
    "guarantee future results. Consult a licensed financial advisor before "
    "making investment decisions."
)


async def simulate_investment(
    user_id: UUID,
    session: AsyncSession,
    amount: float,
    months: int,
) -> Dict[str, Any]:
    """Run investment projection at 3 risk levels."""
    rates = {
        "conservative": 0.05,
        "moderate": 0.08,
        "aggressive": 0.12,
    }

    projections = {}
    for label, annual_rate in rates.items():
        monthly_rate = annual_rate / 12
        projected = amount * math.pow(1 + monthly_rate, months)
        projections[label] = {
            "return_rate": annual_rate,
            "projected_value": round(projected, 2),
            "monthly_gain": round((projected - amount) / months, 2),
        }

    # Feasibility check against user's current finances
    ai_service = AIService(session)
    context = await ai_service.get_user_context(user_id)
    snapshot = context.get("data", {}).get("financial_snapshot", {})
    monthly_income = snapshot.get("monthly_income_avg", 0)
    monthly_expense = snapshot.get("monthly_expense_avg", 0)
    monthly_savings = monthly_income - monthly_expense

    feasibility_score = min(1.0, monthly_savings / amount) if amount > 0 else 0

    if feasibility_score >= 0.8:
        verdict = "Highly feasible based on current savings pattern."
    elif feasibility_score >= 0.5:
        verdict = "Feasible with moderate adjustment to current spending."
    elif feasibility_score >= 0.2:
        verdict = "Challenging — requires significant spending reduction."
    else:
        verdict = "Not currently feasible. Consider a smaller amount or longer timeline."

    return {
        "investment_amount": amount,
        "time_horizon_months": months,
        "projections": projections,
        "feasibility": {
            "score": round(feasibility_score, 2),
            "monthly_savings_available": round(monthly_savings, 2),
            "monthly_savings_needed": round(amount / months, 2) if months > 0 else amount,
            "verdict": verdict,
        },
        "disclaimer": DISCLAIMER,
    }
