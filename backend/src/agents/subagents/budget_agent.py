"""Budget Agent — handles budget-related queries and operations."""

from typing import Any, Dict
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from src.agents.base import AgentMetadata, BaseAgent
from src.agents.registry import AgentRegistry
from src.agents.skills.budget_analysis import analyze_budgets
from src.agents.skills.finance_crud import parse_financial_command
from src.mcp.tools.budget_tools import create_budget


@AgentRegistry.register_agent
class BudgetAgent(BaseAgent):
    """Subagent specializing in budget management."""

    metadata = AgentMetadata(
        name="budget",
        description="Manages budgets — creation, analysis, and status queries.",
        keywords={
            "budget", "budgets", "limit", "spending limit", "allocate",
            "bajat", "had", "budget set", "budget status",
        },
    )

    async def handle(self, message: str, parsed: Dict[str, Any]) -> Dict[str, Any]:
        """Process a budget-related request."""
        intent = parsed.get("intent", "query")

        if intent == "create":
            return await self._create_budget(message, parsed)
        elif intent == "analyze":
            return await self._analyze(message)
        else:
            return await self._query_budgets(message)

    async def _create_budget(self, message: str, parsed: Dict[str, Any]) -> Dict[str, Any]:
        amount = parsed.get("amount")
        category = parsed.get("category")

        if not amount or not category:
            return {
                "response": "I need both a category and amount to create a budget. For example: 'Set Food budget to 15,000'",
                "intent": "create_budget",
                "needs_clarification": True,
            }

        result = await create_budget(
            user_id=self.user_id,
            session=self.session,
            category=category,
            amount=amount,
        )

        if "error" in result:
            return {
                "response": f"I couldn't create that budget: {result['error']}",
                "intent": "create_budget",
                "tool_calls": [{"tool": "create_budget", "status": "error", "error": result["error"]}],
            }

        return {
            "response": f"Budget created! {result['message']}",
            "intent": "create_budget",
            "confidence": 0.9,
            "tool_calls": [{"tool": "create_budget", "status": "success", "result": result}],
        }

    async def _analyze(self, message: str) -> Dict[str, Any]:
        result = await analyze_budgets(user_id=self.user_id, session=self.session)

        lines = [result["coaching"], ""]
        if result["exceeded_budgets"]:
            lines.append("Over budget:")
            for b in result["exceeded_budgets"]:
                lines.append(f"  {b['emoji']} {b['category']}: {b['spent']:,.0f} / {b['limit']:,.0f}")
        if result["warning_budgets"]:
            lines.append("\nAt warning level:")
            for b in result["warning_budgets"]:
                lines.append(f"  {b['emoji']} {b['category']}: {b['spent']:,.0f} / {b['limit']:,.0f}")
        if result["recommendations"]:
            lines.append("\nRecommendations:")
            for r in result["recommendations"]:
                lines.append(f"  • {r}")

        return {
            "response": "\n".join(lines),
            "intent": "analyze_budget",
            "confidence": 0.85,
            "entities": {"budgets": result},
        }

    async def _query_budgets(self, message: str) -> Dict[str, Any]:
        result = await analyze_budgets(user_id=self.user_id, session=self.session)

        if result["total_budgets"] == 0:
            return {
                "response": "You don't have any budgets set for this month. Would you like to create one?",
                "intent": "query_budget",
                "confidence": 0.85,
            }

        lines = [f"Budget Status ({result['total_budgets']} budgets):"]
        lines.append(f"  On track: {result['on_track']}")
        if result["exceeded"]:
            lines.append(f"  Exceeded: {result['exceeded']}")
        if result["warning"]:
            lines.append(f"  Warning: {result['warning']}")

        return {
            "response": "\n".join(lines),
            "intent": "query_budget",
            "confidence": 0.85,
            "entities": {"budgets": result},
        }
