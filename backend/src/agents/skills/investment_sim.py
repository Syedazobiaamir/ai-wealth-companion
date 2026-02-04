"""Investment Simulation skill — parse queries and run projections."""

from typing import Any, Dict, Optional
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from src.mcp.tools.investment_tools import simulate_investment


async def run_investment_simulation(
    user_id: UUID,
    session: AsyncSession,
    amount: float,
    months: int = 12,
) -> Dict[str, Any]:
    """Run investment simulation and format results with disclaimer."""
    result = await simulate_investment(
        user_id=user_id, session=session, amount=amount, months=months
    )

    projections = result.get("projections", {})
    feasibility = result.get("feasibility", {})

    # Format human-readable summary
    lines = [f"Investment Simulation: {amount:,.0f} over {months} months\n"]
    for level, data in projections.items():
        lines.append(
            f"  {level.capitalize()} ({data['return_rate']*100:.0f}% annual): "
            f"{data['projected_value']:,.0f} (+{data['monthly_gain']:,.0f}/mo)"
        )

    lines.append(f"\nFeasibility: {feasibility.get('verdict', 'N/A')}")
    lines.append(f"Monthly savings available: {feasibility.get('monthly_savings_available', 0):,.0f}")
    lines.append(f"Monthly savings needed: {feasibility.get('monthly_savings_needed', 0):,.0f}")

    return {
        "summary": "\n".join(lines),
        "projections": projections,
        "feasibility": feasibility,
        "disclaimer": result.get("disclaimer", ""),
    }
