"""Investment Agent — handles investment queries and simulations."""

from typing import Any, Dict
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from src.agents.base import AgentMetadata, BaseAgent
from src.agents.registry import AgentRegistry
from src.agents.skills.finance_crud import extract_amount
from src.agents.skills.investment_sim import run_investment_simulation


@AgentRegistry.register_agent
class InvestmentAgent(BaseAgent):
    """Subagent specializing in investment analysis and simulation."""

    metadata = AgentMetadata(
        name="investment",
        description="Runs investment projections and simulations.",
        keywords={
            "invest", "investment", "return", "projection", "simulate",
            "predict", "forecast", "future", "grow", "compound",
            "sarmaya", "munafa",
        },
    )

    async def handle(self, message: str, parsed: Dict[str, Any]) -> Dict[str, Any]:
        """Process an investment-related request."""
        amount = parsed.get("amount") or extract_amount(message)

        if not amount:
            return {
                "response": "How much would you like to simulate investing? Please provide an amount (e.g., 'invest 50,000' or 'can I invest 100k').",
                "intent": "simulate_investment",
                "needs_clarification": True,
            }

        # Extract duration from message
        months = self._extract_months(message)

        result = await run_investment_simulation(
            user_id=self.user_id,
            session=self.session,
            amount=amount,
            months=months,
        )

        response_lines = [result["summary"]]
        response_lines.append(f"\n\u26a0\ufe0f {result['disclaimer']}")

        return {
            "response": "\n".join(response_lines),
            "intent": "simulate_investment",
            "confidence": 0.85,
            "entities": {
                "amount": amount,
                "months": months,
                "projections": result["projections"],
                "feasibility": result["feasibility"],
            },
            "tool_calls": [{"tool": "simulate_investment", "status": "success"}],
        }

    def _extract_months(self, text: str) -> int:
        """Extract investment duration from text. Default 12 months."""
        import re
        lower = text.lower()

        # Check for explicit months
        m = re.search(r'(\d+)\s*month', lower)
        if m:
            return int(m.group(1))

        # Check for years
        y = re.search(r'(\d+)\s*year', lower)
        if y:
            return int(y.group(1)) * 12

        # Common phrases
        if "6 month" in lower or "half year" in lower:
            return 6
        if "2 year" in lower:
            return 24
        if "5 year" in lower:
            return 60

        return 12  # default
