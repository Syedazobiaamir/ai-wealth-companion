"""Spending Agent — handles transaction queries and spending analysis."""

from typing import Any, Dict
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from src.agents.base import AgentMetadata, BaseAgent
from src.agents.registry import AgentRegistry
from src.agents.skills.finance_crud import parse_financial_command
from src.agents.skills.spending_insight import generate_spending_insight
from src.mcp.tools.transaction_tools import add_transaction
from src.mcp.tools.financial_summary import get_financial_summary


@AgentRegistry.register_agent
class SpendingAgent(BaseAgent):
    """Subagent specializing in transactions and spending analysis.

    Also acts as the fallback agent for unclassified messages.
    """

    metadata = AgentMetadata(
        name="spending",
        description="Tracks transactions, analyzes spending patterns, and provides financial summaries.",
        keywords={
            "expense", "spend", "spending", "transaction", "income",
            "add", "record", "summary", "kharcha", "amdani",
        },
    )

    def can_handle(self, message: str, parsed: Dict[str, Any]) -> float:
        """Keyword matching with a fallback floor of 0.1 so this agent
        always has a minimum score (general-purpose fallback)."""
        score = super().can_handle(message, parsed)
        return max(score, 0.1)

    async def handle(self, message: str, parsed: Dict[str, Any]) -> Dict[str, Any]:
        """Process a spending-related request."""
        intent = parsed.get("intent", "query")

        if intent == "create":
            return await self._add_transaction(message, parsed)
        elif intent == "analyze":
            return await self._analyze_spending(message)
        else:
            return await self._query_summary(message)

    async def _add_transaction(self, message: str, parsed: Dict[str, Any]) -> Dict[str, Any]:
        amount = parsed.get("amount")
        category = parsed.get("category")
        txn_type = parsed.get("transaction_type", "expense")

        if not amount:
            return {
                "response": "I need an amount to record a transaction. For example: 'Spent 500 on groceries'",
                "intent": "create_transaction",
                "needs_clarification": True,
            }

        if not category:
            return {
                "response": f"What category should I use for this {amount:,.0f} {txn_type}? (e.g., Food, Transport, Shopping)",
                "intent": "create_transaction",
                "needs_clarification": True,
            }

        result = await add_transaction(
            user_id=self.user_id,
            session=self.session,
            type=txn_type,
            amount=amount,
            category=category,
            note=message[:200],
            date_str=parsed.get("date"),
        )

        if "error" in result:
            return {
                "response": f"I couldn't record that: {result['error']}",
                "intent": "create_transaction",
                "tool_calls": [{"tool": "add_transaction", "status": "error", "error": result["error"]}],
            }

        return {
            "response": f"Recorded! {result['message']}",
            "intent": "create_transaction",
            "confidence": 0.9,
            "tool_calls": [{"tool": "add_transaction", "status": "success", "result": result}],
        }

    async def _analyze_spending(self, message: str) -> Dict[str, Any]:
        result = await generate_spending_insight(
            user_id=self.user_id, session=self.session
        )

        lines = [f"Spending Analysis (This Month):"]
        lines.append(f"  Income: {result['income']:,.0f}")
        lines.append(f"  Expenses: {result['expenses']:,.0f}")
        lines.append(f"  Savings Rate: {result['savings_rate']:.0f}%")
        lines.append(f"  Trend: {result['trend']}")

        if result["top_categories"]:
            lines.append("\nTop Categories:")
            for c in result["top_categories"][:5]:
                name = c.get("category", "Unknown")
                amt = c.get("total", c.get("amount", 0))
                lines.append(f"  • {name}: {amt:,.0f}")

        if result["insights"]:
            lines.append("\nInsights:")
            for i in result["insights"]:
                lines.append(f"  • {i}")

        return {
            "response": "\n".join(lines),
            "intent": "analyze_spending",
            "confidence": 0.85,
            "entities": result,
        }

    async def _query_summary(self, message: str) -> Dict[str, Any]:
        result = await get_financial_summary(
            user_id=self.user_id, session=self.session
        )

        lines = [f"Financial Summary (This Month):"]
        lines.append(f"  Income: {result.get('income', 0):,.0f}")
        lines.append(f"  Expenses: {result.get('expenses', 0):,.0f}")
        lines.append(f"  Net: {result.get('net', 0):,.0f}")
        lines.append(f"  Savings Rate: {result.get('savings_rate', 0):.0f}%")

        if result.get("top_categories"):
            lines.append("\nTop Spending:")
            for c in result["top_categories"][:3]:
                lines.append(f"  • {c['name']}: {c['amount']:,.0f} ({c['percentage']}%)")

        return {
            "response": "\n".join(lines),
            "intent": "query_summary",
            "confidence": 0.85,
            "entities": result,
        }
