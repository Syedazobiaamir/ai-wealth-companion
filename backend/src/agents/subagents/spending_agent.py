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
from src.mcp.tools.wallet_tools import create_wallet, list_wallets, get_wallet_balance


@AgentRegistry.register_agent
class SpendingAgent(BaseAgent):
    """Subagent specializing in transactions and spending analysis.

    Also acts as the fallback agent for unclassified messages.
    """

    metadata = AgentMetadata(
        name="spending",
        description="Tracks transactions, manages wallets, analyzes spending patterns, and provides financial summaries.",
        keywords={
            "expense", "spend", "spending", "transaction", "income",
            "add", "record", "summary", "kharcha", "amdani",
            "wallet", "wallets", "account", "balance", "cash", "bank",
            "credit", "savings", "paisa", "paisay", "money",
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
        lower_msg = message.lower()

        # Skip if this is a goal/task/budget/category operation - let CRUD agent handle
        crud_entities = {"goal", "goals", "task", "tasks", "budget", "budgets", "category", "categories"}
        crud_verbs = {"delete", "remove", "update", "complete", "done"}

        # Only forward to CRUD if it's a CRUD operation on these entities
        if any(entity in lower_msg for entity in crud_entities):
            from src.agents.subagents.crud_agent import CrudAgent
            crud_agent = CrudAgent(self.session, self.user_id)
            return await crud_agent.handle(message, parsed)

        # Forward transaction delete/update to CRUD agent
        if "transaction" in lower_msg and any(verb in lower_msg for verb in crud_verbs):
            from src.agents.subagents.crud_agent import CrudAgent
            crud_agent = CrudAgent(self.session, self.user_id)
            return await crud_agent.handle(message, parsed)

        # Check for wallet-related intents first
        wallet_keywords = {"wallet", "wallets", "account", "balance", "paisa", "paisay"}
        create_keywords = {"create", "add", "new", "make", "banao", "open"}
        list_keywords = {"show", "list", "my", "all", "dikhao", "kitna", "kitne"}

        has_wallet = any(kw in lower_msg for kw in wallet_keywords)
        has_create = any(kw in lower_msg for kw in create_keywords)
        has_list = any(kw in lower_msg for kw in list_keywords)

        if has_wallet:
            if has_create:
                return await self._create_wallet(message, parsed)
            elif has_list or "balance" in lower_msg:
                return await self._list_wallets(message)

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

    async def _create_wallet(self, message: str, parsed: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new wallet for the user."""
        lower_msg = message.lower()

        # Extract wallet type from message
        wallet_type = "cash"  # default
        type_map = {
            "bank": "bank",
            "credit": "credit",
            "savings": "savings",
            "investment": "investment",
            "cash": "cash",
        }
        for key, val in type_map.items():
            if key in lower_msg:
                wallet_type = val
                break

        # Extract wallet name or generate one
        name = parsed.get("wallet_name")
        if not name:
            # Generate a default name based on type
            type_names = {
                "cash": "My Cash",
                "bank": "Bank Account",
                "credit": "Credit Card",
                "savings": "Savings Account",
                "investment": "Investment Account",
            }
            name = type_names.get(wallet_type, "My Wallet")

        # Extract initial balance if mentioned
        initial_balance = parsed.get("amount", 0.0)

        result = await create_wallet(
            user_id=self.user_id,
            session=self.session,
            name=name,
            wallet_type=wallet_type,
            initial_balance=initial_balance,
        )

        if "error" in result:
            return {
                "response": f"Couldn't create wallet: {result['error']}",
                "intent": "create_wallet",
                "tool_calls": [{"tool": "create_wallet", "status": "error", "error": result["error"]}],
            }

        return {
            "response": result["message"],
            "intent": "create_wallet",
            "confidence": 0.9,
            "tool_calls": [{"tool": "create_wallet", "status": "success", "result": result}],
        }

    async def _list_wallets(self, message: str) -> Dict[str, Any]:
        """List all wallets and their balances."""
        result = await list_wallets(
            user_id=self.user_id,
            session=self.session,
        )

        if "error" in result:
            return {
                "response": f"Couldn't get wallets: {result['error']}",
                "intent": "list_wallets",
                "tool_calls": [{"tool": "list_wallets", "status": "error", "error": result["error"]}],
            }

        if not result.get("wallets"):
            return {
                "response": result["message"],
                "intent": "list_wallets",
                "confidence": 0.9,
            }

        lines = [result["message"], ""]
        for w in result["wallets"]:
            default_mark = " (default)" if w["is_default"] else ""
            lines.append(f"  • {w['name']}{default_mark}: {w['currency']} {w['balance']:,.0f} ({w['type']})")

        return {
            "response": "\n".join(lines),
            "intent": "list_wallets",
            "confidence": 0.9,
            "tool_calls": [{"tool": "list_wallets", "status": "success", "result": result}],
        }
