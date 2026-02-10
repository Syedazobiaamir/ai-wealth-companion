"""Universal CRUD Agent — handles create, update, delete, list for all entities."""

import re
from typing import Any, Dict
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from src.agents.base import AgentMetadata, BaseAgent
from src.agents.registry import AgentRegistry
from src.agents.skills.finance_crud import extract_amount
from src.mcp.tools.crud_tools import (
    create_category, list_categories, delete_category,
    list_budgets, update_budget, delete_budget,
    list_transactions, update_transaction, delete_transaction,
    update_task, delete_task,
    create_goal, list_goals, update_goal, delete_goal,
    create_wallet, list_wallets, update_wallet, delete_wallet,
)


@AgentRegistry.register_agent
class CrudAgent(BaseAgent):
    """Subagent specializing in CRUD operations for all entities."""

    metadata = AgentMetadata(
        name="crud",
        description="Handles create, update, delete, list operations for categories, budgets, transactions, tasks, goals, wallets.",
        keywords={
            "category", "categories", "budget", "budgets", "goal", "goals",
            "delete", "remove", "update", "change", "rename", "complete", "done",
            "list", "show", "hatao", "mitao", "badlo",
        },
    )

    def can_handle(self, message: str, parsed: Dict[str, Any]) -> float:
        """Check if this is a CRUD operation."""
        lower = message.lower()

        # High priority for explicit CRUD operations
        crud_verbs = ["delete", "remove", "update", "rename", "complete", "done", "hatao", "mitao"]
        create_verbs = ["create", "add", "new", "make", "set", "banao"]
        entity_words = ["category", "categories", "budget", "goal", "goals", "task", "tasks", "wallet", "wallets"]

        has_crud = any(v in lower for v in crud_verbs)
        has_create = any(v in lower for v in create_verbs)
        has_entity = any(e in lower for e in entity_words)

        # Highest priority for goal/task/wallet creation
        if has_create and any(e in lower for e in ["goal", "goals", "task", "tasks"]):
            return 0.98

        if has_crud and has_entity:
            return 0.95

        # Also handle "list goals", "show budgets", etc.
        if any(e in lower for e in entity_words):
            if any(w in lower for w in ["list", "show", "my", "all"]):
                return 0.90

        return super().can_handle(message, parsed)

    async def handle(self, message: str, parsed: Dict[str, Any]) -> Dict[str, Any]:
        """Process CRUD operations."""
        lower = message.lower()

        # Detect entity type
        entity = self._detect_entity(lower)
        # Detect operation
        operation = self._detect_operation(lower)

        if not entity:
            return {
                "response": "I'm not sure what you want to manage. Try:\n"
                           "  • 'show my categories'\n"
                           "  • 'delete budget for food'\n"
                           "  • 'complete task pay bill'\n"
                           "  • 'add 5000 to savings goal'",
                "intent": "crud_help",
                "confidence": 0.8,
            }

        # Route to appropriate handler
        handlers = {
            ("category", "create"): self._create_category,
            ("category", "list"): self._list_categories,
            ("category", "delete"): self._delete_category,
            ("budget", "list"): self._list_budgets,
            ("budget", "update"): self._update_budget,
            ("budget", "delete"): self._delete_budget,
            ("transaction", "list"): self._list_transactions,
            ("transaction", "update"): self._update_transaction,
            ("transaction", "delete"): self._delete_transaction,
            ("task", "update"): self._update_task,
            ("task", "delete"): self._delete_task,
            ("task", "complete"): self._complete_task,
            ("goal", "create"): self._create_goal,
            ("goal", "list"): self._list_goals,
            ("goal", "update"): self._update_goal,
            ("goal", "delete"): self._delete_goal,
            ("wallet", "create"): self._create_wallet,
            ("wallet", "list"): self._list_wallets,
            ("wallet", "update"): self._update_wallet,
            ("wallet", "delete"): self._delete_wallet,
        }

        handler = handlers.get((entity, operation))
        if handler:
            return await handler(message, parsed)

        # Default to list if no operation detected
        list_handler = handlers.get((entity, "list"))
        if list_handler:
            return await list_handler(message, parsed)

        return {
            "response": f"I can help you manage {entity}s. What would you like to do?",
            "intent": f"{entity}_help",
            "confidence": 0.7,
        }

    def _detect_entity(self, text: str) -> str:
        """Detect which entity the user is referring to."""
        if any(w in text for w in ["category", "categories"]):
            return "category"
        if any(w in text for w in ["budget", "budgets"]):
            return "budget"
        if any(w in text for w in ["transaction", "transactions", "expense", "income"]):
            return "transaction"
        if any(w in text for w in ["task", "tasks", "reminder", "reminders", "todo"]):
            return "task"
        if any(w in text for w in ["goal", "goals", "target", "saving"]):
            return "goal"
        if any(w in text for w in ["wallet", "wallets", "account"]):
            return "wallet"
        return None

    def _detect_operation(self, text: str) -> str:
        """Detect the CRUD operation."""
        if any(w in text for w in ["delete", "remove", "hatao", "mitao"]):
            return "delete"
        if any(w in text for w in ["complete", "done", "finish", "mark", "khatam"]):
            return "complete"
        if any(w in text for w in ["update", "change", "rename", "set", "badlo", "modify"]):
            return "update"
        if any(w in text for w in ["create", "add", "new", "banao"]):
            return "create"
        if any(w in text for w in ["list", "show", "get", "my", "all", "dikhao"]):
            return "list"
        return "list"

    def _extract_name(self, text: str, entity: str) -> str:
        """Extract entity name from message."""
        # Remove common words
        words_to_remove = [
            "delete", "remove", "update", "create", "add", "new", "show", "list",
            "the", "a", "an", "my", "for", "from", entity, entity + "s",
            "complete", "done", "finish", "mark", "please", "can", "you",
        ]
        words = text.lower().split()
        remaining = [w for w in words if w not in words_to_remove]
        return " ".join(remaining).strip().title() if remaining else None

    # ============== CATEGORY HANDLERS ==============

    async def _create_category(self, message: str, parsed: Dict[str, Any]) -> Dict[str, Any]:
        name = self._extract_name(message, "category")
        if not name:
            return {"response": "What should I name the category?", "needs_clarification": True}

        cat_type = "income" if "income" in message.lower() else "expense"
        result = await create_category(self.user_id, self.session, name, cat_type)

        return {
            "response": result.get("message", result.get("error")),
            "intent": "create_category",
            "confidence": 0.9,
        }

    async def _list_categories(self, message: str, parsed: Dict[str, Any]) -> Dict[str, Any]:
        result = await list_categories(self.user_id, self.session)
        return {
            "response": result.get("message", result.get("error")),
            "intent": "list_categories",
            "confidence": 0.9,
        }

    async def _delete_category(self, message: str, parsed: Dict[str, Any]) -> Dict[str, Any]:
        name = self._extract_name(message, "category")
        if not name:
            return {"response": "Which category should I delete?", "needs_clarification": True}

        result = await delete_category(self.user_id, self.session, name)
        return {
            "response": result.get("message", result.get("error")),
            "intent": "delete_category",
            "confidence": 0.9,
        }

    # ============== BUDGET HANDLERS ==============

    async def _list_budgets(self, message: str, parsed: Dict[str, Any]) -> Dict[str, Any]:
        result = await list_budgets(self.user_id, self.session)
        return {
            "response": result.get("message", result.get("error")),
            "intent": "list_budgets",
            "confidence": 0.9,
        }

    async def _update_budget(self, message: str, parsed: Dict[str, Any]) -> Dict[str, Any]:
        amount = parsed.get("amount") or extract_amount(message)
        category = parsed.get("category") or self._extract_name(message, "budget")

        if not amount:
            return {"response": "What should the budget amount be?", "needs_clarification": True}
        if not category:
            return {"response": "Which category is this budget for?", "needs_clarification": True}

        result = await update_budget(self.user_id, self.session, category, amount)
        return {
            "response": result.get("message", result.get("error")),
            "intent": "update_budget",
            "confidence": 0.9,
        }

    async def _delete_budget(self, message: str, parsed: Dict[str, Any]) -> Dict[str, Any]:
        category = self._extract_name(message, "budget")
        if not category:
            return {"response": "Which budget should I delete?", "needs_clarification": True}

        result = await delete_budget(self.user_id, self.session, category)
        return {
            "response": result.get("message", result.get("error")),
            "intent": "delete_budget",
            "confidence": 0.9,
        }

    # ============== TRANSACTION HANDLERS ==============

    async def _list_transactions(self, message: str, parsed: Dict[str, Any]) -> Dict[str, Any]:
        txn_type = None
        if "income" in message.lower():
            txn_type = "income"
        elif "expense" in message.lower():
            txn_type = "expense"

        result = await list_transactions(self.user_id, self.session, transaction_type=txn_type)
        return {
            "response": result.get("message", result.get("error")),
            "intent": "list_transactions",
            "confidence": 0.9,
        }

    async def _update_transaction(self, message: str, parsed: Dict[str, Any]) -> Dict[str, Any]:
        last = any(w in message.lower() for w in ["last", "recent", "latest"])
        amount = parsed.get("amount") or extract_amount(message)
        category = parsed.get("category") or self._extract_name(message, "transaction")

        result = await update_transaction(
            self.user_id, self.session,
            last=last,
            amount=amount,
            category=category,
        )
        return {
            "response": result.get("message", result.get("error")),
            "intent": "update_transaction",
            "confidence": 0.9,
        }

    async def _delete_transaction(self, message: str, parsed: Dict[str, Any]) -> Dict[str, Any]:
        last = any(w in message.lower() for w in ["last", "recent", "latest"])
        result = await delete_transaction(self.user_id, self.session, last=last)
        return {
            "response": result.get("message", result.get("error")),
            "intent": "delete_transaction",
            "confidence": 0.9,
        }

    # ============== TASK HANDLERS ==============

    async def _update_task(self, message: str, parsed: Dict[str, Any]) -> Dict[str, Any]:
        task_title = self._extract_name(message, "task")
        if not task_title:
            return {"response": "Which task should I update?", "needs_clarification": True}

        result = await update_task(self.user_id, self.session, task_title)
        return {
            "response": result.get("message", result.get("error")),
            "intent": "update_task",
            "confidence": 0.9,
        }

    async def _complete_task(self, message: str, parsed: Dict[str, Any]) -> Dict[str, Any]:
        task_title = self._extract_name(message, "task")
        if not task_title:
            return {"response": "Which task should I mark as complete?", "needs_clarification": True}

        result = await update_task(self.user_id, self.session, task_title, mark_complete=True)
        return {
            "response": result.get("message", result.get("error")),
            "intent": "complete_task",
            "confidence": 0.9,
        }

    async def _delete_task(self, message: str, parsed: Dict[str, Any]) -> Dict[str, Any]:
        task_title = self._extract_name(message, "task")
        if not task_title:
            return {"response": "Which task should I delete?", "needs_clarification": True}

        result = await delete_task(self.user_id, self.session, task_title)
        return {
            "response": result.get("message", result.get("error")),
            "intent": "delete_task",
            "confidence": 0.9,
        }

    # ============== GOAL HANDLERS ==============

    async def _create_goal(self, message: str, parsed: Dict[str, Any]) -> Dict[str, Any]:
        name = self._extract_name(message, "goal")
        amount = parsed.get("amount") or extract_amount(message)

        if not name:
            return {"response": "What should I name the goal?", "needs_clarification": True}
        if not amount:
            return {"response": f"What's the target amount for '{name}'?", "needs_clarification": True}

        result = await create_goal(self.user_id, self.session, name, amount)
        return {
            "response": result.get("message", result.get("error")),
            "intent": "create_goal",
            "confidence": 0.9,
        }

    async def _list_goals(self, message: str, parsed: Dict[str, Any]) -> Dict[str, Any]:
        result = await list_goals(self.user_id, self.session)
        return {
            "response": result.get("message", result.get("error")),
            "intent": "list_goals",
            "confidence": 0.9,
        }

    async def _update_goal(self, message: str, parsed: Dict[str, Any]) -> Dict[str, Any]:
        name = self._extract_name(message, "goal")
        amount = parsed.get("amount") or extract_amount(message)

        if not name:
            return {"response": "Which goal should I update?", "needs_clarification": True}

        # Check if adding or changing target
        if any(w in message.lower() for w in ["add", "save", "deposit", "jama"]):
            result = await update_goal(self.user_id, self.session, name, add_amount=amount)
        else:
            result = await update_goal(self.user_id, self.session, name, new_target=amount)

        return {
            "response": result.get("message", result.get("error")),
            "intent": "update_goal",
            "confidence": 0.9,
        }

    async def _delete_goal(self, message: str, parsed: Dict[str, Any]) -> Dict[str, Any]:
        name = self._extract_name(message, "goal")
        if not name:
            return {"response": "Which goal should I delete?", "needs_clarification": True}

        result = await delete_goal(self.user_id, self.session, name)
        return {
            "response": result.get("message", result.get("error")),
            "intent": "delete_goal",
            "confidence": 0.9,
        }

    # ============== WALLET HANDLERS ==============

    async def _create_wallet(self, message: str, parsed: Dict[str, Any]) -> Dict[str, Any]:
        name = self._extract_name(message, "wallet")
        if not name:
            return {"response": "What should I name the wallet?", "needs_clarification": True}

        amount = parsed.get("amount") or extract_amount(message) or 0
        wallet_type = "cash"
        for wt in ["bank", "credit", "savings", "investment"]:
            if wt in message.lower():
                wallet_type = wt
                break

        result = await create_wallet(
            self.user_id, self.session,
            name=name,
            wallet_type=wallet_type,
            initial_balance=amount,
        )
        return {
            "response": result.get("message", result.get("error")),
            "intent": "create_wallet",
            "confidence": 0.9,
        }

    async def _list_wallets(self, message: str, parsed: Dict[str, Any]) -> Dict[str, Any]:
        result = await list_wallets(self.user_id, self.session)
        return {
            "response": result.get("message", result.get("error")),
            "intent": "list_wallets",
            "confidence": 0.9,
        }

    async def _update_wallet(self, message: str, parsed: Dict[str, Any]) -> Dict[str, Any]:
        name = self._extract_name(message, "wallet")
        if not name:
            return {"response": "Which wallet should I update?", "needs_clarification": True}

        set_default = any(w in message.lower() for w in ["default", "primary", "main"])
        result = await update_wallet(self.user_id, self.session, name, set_default=set_default)
        return {
            "response": result.get("message", result.get("error")),
            "intent": "update_wallet",
            "confidence": 0.9,
        }

    async def _delete_wallet(self, message: str, parsed: Dict[str, Any]) -> Dict[str, Any]:
        name = self._extract_name(message, "wallet")
        if not name:
            return {"response": "Which wallet should I delete?", "needs_clarification": True}

        result = await delete_wallet(self.user_id, self.session, name)
        return {
            "response": result.get("message", result.get("error")),
            "intent": "delete_wallet",
            "confidence": 0.9,
        }
