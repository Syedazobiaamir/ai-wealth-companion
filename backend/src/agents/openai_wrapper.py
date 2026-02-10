"""AI Agent Wrapper for AI Wealth Companion.

Supports both OpenAI and Google Gemini APIs with tool calling.
Priority: GEMINI_API_KEY > OPENAI_API_KEY > MasterOrchestrator fallback
"""

import json
import logging
import os
from typing import Any, Dict, List, Optional
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from src.agents.master import MasterOrchestrator
from src.agents.skills.translation import detect_language
from src.services.conversation import ConversationService

logger = logging.getLogger("ai.agent_wrapper")


# System prompt for the AI Wealth Companion
SYSTEM_PROMPT = """You are an AI Financial Assistant for the AI Wealth Companion app.
You help users manage their finances through natural conversation.

Your capabilities:
- Record income and expenses (e.g., "spent 500 on groceries", "received salary 85000")
- Query spending and financial summaries (e.g., "show my spending this month")
- Create and monitor budgets (e.g., "set food budget to 15000")
- Simulate investments (e.g., "what if I invest 50000 for 12 months?")
- Manage tasks and reminders (e.g., "remind me to pay rent on the 5th")
- Check financial health score

Language Support:
- Respond in the same language the user uses
- Support English, Urdu script, and Roman Urdu
- Common Urdu terms: kharcha (expense), kamai (income), bajat (budget)

Guidelines:
- Be helpful and conversational
- Use the available tools to perform actions
- Always confirm actions with specific details
- For investments, include the standard financial disclaimer
- Keep responses concise but informative
"""

# Financial disclaimer for investment-related responses
FINANCIAL_DISCLAIMER = (
    "Note: I provide information based on your financial data, "
    "not professional financial advice. Consult a licensed advisor "
    "for investment decisions."
)

# Tool definitions shared between OpenAI and Gemini
TOOL_DEFINITIONS = [
    # ============== TRANSACTION TOOLS ==============
    {
        "name": "add_transaction",
        "description": "Record an income or expense transaction",
        "parameters": {
            "type": "object",
            "properties": {
                "amount": {"type": "number", "description": "The transaction amount in PKR"},
                "category": {"type": "string", "description": "Category like Food, Transport, Shopping, Salary, etc."},
                "transaction_type": {"type": "string", "enum": ["expense", "income"], "description": "Whether this is an expense or income"},
                "description": {"type": "string", "description": "Optional description of the transaction"}
            },
            "required": ["amount", "category", "transaction_type"]
        }
    },
    {
        "name": "list_transactions",
        "description": "List recent transactions with optional filters",
        "parameters": {
            "type": "object",
            "properties": {
                "transaction_type": {"type": "string", "enum": ["expense", "income", "all"], "description": "Filter by transaction type"},
                "limit": {"type": "integer", "description": "Number of transactions to show (default 10)"}
            },
            "required": []
        }
    },
    {
        "name": "update_transaction",
        "description": "Update a transaction's amount, category, or description",
        "parameters": {
            "type": "object",
            "properties": {
                "transaction_id": {"type": "string", "description": "Transaction ID or 'last' for most recent"},
                "amount": {"type": "number", "description": "New amount"},
                "category": {"type": "string", "description": "New category"},
                "description": {"type": "string", "description": "New description"}
            },
            "required": ["transaction_id"]
        }
    },
    {
        "name": "delete_transaction",
        "description": "Delete a transaction",
        "parameters": {
            "type": "object",
            "properties": {
                "transaction_id": {"type": "string", "description": "Transaction ID or 'last' for most recent"}
            },
            "required": ["transaction_id"]
        }
    },
    # ============== WALLET TOOLS ==============
    {
        "name": "create_wallet",
        "description": "Create a new wallet/account",
        "parameters": {
            "type": "object",
            "properties": {
                "name": {"type": "string", "description": "Wallet name (e.g., 'Cash', 'Bank Account', 'Savings')"},
                "initial_balance": {"type": "number", "description": "Starting balance in PKR"},
                "wallet_type": {"type": "string", "enum": ["cash", "bank", "credit", "savings", "investment"], "description": "Type of wallet"}
            },
            "required": ["name"]
        }
    },
    {
        "name": "list_wallets",
        "description": "List all wallets and their balances",
        "parameters": {
            "type": "object",
            "properties": {},
            "required": []
        }
    },
    {
        "name": "update_wallet",
        "description": "Update wallet name, balance, or set as default",
        "parameters": {
            "type": "object",
            "properties": {
                "name": {"type": "string", "description": "Current wallet name"},
                "new_name": {"type": "string", "description": "New wallet name"},
                "balance": {"type": "number", "description": "New balance"},
                "set_default": {"type": "boolean", "description": "Set as default wallet"}
            },
            "required": ["name"]
        }
    },
    {
        "name": "delete_wallet",
        "description": "Delete a wallet",
        "parameters": {
            "type": "object",
            "properties": {
                "name": {"type": "string", "description": "Wallet name to delete"}
            },
            "required": ["name"]
        }
    },
    # ============== GOAL TOOLS ==============
    {
        "name": "create_goal",
        "description": "Create a savings goal",
        "parameters": {
            "type": "object",
            "properties": {
                "name": {"type": "string", "description": "Goal name (e.g., 'Emergency Fund', 'Vacation', 'New Phone')"},
                "target_amount": {"type": "number", "description": "Target amount to save in PKR"},
                "deadline": {"type": "string", "description": "Target date (e.g., '2026-12-31')"}
            },
            "required": ["name", "target_amount"]
        }
    },
    {
        "name": "list_goals",
        "description": "List all savings goals and their progress",
        "parameters": {
            "type": "object",
            "properties": {
                "status": {"type": "string", "enum": ["active", "completed", "all"], "description": "Filter by goal status"}
            },
            "required": []
        }
    },
    {
        "name": "update_goal",
        "description": "Add money to a goal or update its target",
        "parameters": {
            "type": "object",
            "properties": {
                "name": {"type": "string", "description": "Goal name"},
                "add_amount": {"type": "number", "description": "Amount to add to current savings"},
                "new_target": {"type": "number", "description": "New target amount"}
            },
            "required": ["name"]
        }
    },
    {
        "name": "delete_goal",
        "description": "Delete a savings goal",
        "parameters": {
            "type": "object",
            "properties": {
                "name": {"type": "string", "description": "Goal name to delete"}
            },
            "required": ["name"]
        }
    },
    # ============== BUDGET TOOLS ==============
    {
        "name": "create_budget",
        "description": "Create a monthly budget for a spending category",
        "parameters": {
            "type": "object",
            "properties": {
                "category": {"type": "string", "description": "Budget category like Food, Transport, Entertainment"},
                "amount": {"type": "number", "description": "Monthly budget limit in PKR"}
            },
            "required": ["category", "amount"]
        }
    },
    {
        "name": "list_budgets",
        "description": "List all budgets with spent vs limit",
        "parameters": {
            "type": "object",
            "properties": {},
            "required": []
        }
    },
    {
        "name": "update_budget",
        "description": "Update a budget limit",
        "parameters": {
            "type": "object",
            "properties": {
                "category": {"type": "string", "description": "Budget category"},
                "amount": {"type": "number", "description": "New budget limit in PKR"}
            },
            "required": ["category", "amount"]
        }
    },
    {
        "name": "delete_budget",
        "description": "Delete a budget",
        "parameters": {
            "type": "object",
            "properties": {
                "category": {"type": "string", "description": "Budget category to delete"}
            },
            "required": ["category"]
        }
    },
    # ============== TASK TOOLS ==============
    {
        "name": "create_task",
        "description": "Create a financial task or reminder",
        "parameters": {
            "type": "object",
            "properties": {
                "title": {"type": "string", "description": "Task title/description"},
                "due_date": {"type": "string", "description": "Due date (e.g., 'tomorrow', 'next Friday', '2026-02-10')"},
                "priority": {"type": "string", "enum": ["high", "medium", "low"], "description": "Task priority level"},
                "category": {"type": "string", "enum": ["bills", "savings", "investment", "review", "other"], "description": "Task category"}
            },
            "required": ["title"]
        }
    },
    {
        "name": "list_tasks",
        "description": "List tasks by status",
        "parameters": {
            "type": "object",
            "properties": {
                "status": {"type": "string", "enum": ["active", "overdue", "completed", "all"], "description": "Filter by task status"}
            },
            "required": []
        }
    },
    {
        "name": "complete_task",
        "description": "Mark a task as completed",
        "parameters": {
            "type": "object",
            "properties": {
                "title": {"type": "string", "description": "Task title to complete"}
            },
            "required": ["title"]
        }
    },
    {
        "name": "delete_task",
        "description": "Delete a task",
        "parameters": {
            "type": "object",
            "properties": {
                "title": {"type": "string", "description": "Task title to delete"}
            },
            "required": ["title"]
        }
    },
    # ============== ANALYSIS & TIPS TOOLS ==============
    {
        "name": "get_financial_summary",
        "description": "Get financial summary including income, expenses, and savings rate",
        "parameters": {
            "type": "object",
            "properties": {
                "period": {"type": "string", "enum": ["day", "week", "month", "year"], "description": "Time period for the summary"}
            },
            "required": []
        }
    },
    {
        "name": "get_health_score",
        "description": "Calculate and return the user's financial health score (0-100)",
        "parameters": {
            "type": "object",
            "properties": {},
            "required": []
        }
    },
    {
        "name": "get_financial_tips",
        "description": "Get personalized financial tips and advice based on spending patterns",
        "parameters": {
            "type": "object",
            "properties": {
                "focus": {"type": "string", "enum": ["saving", "budgeting", "investing", "debt", "general"], "description": "Area to focus tips on"}
            },
            "required": []
        }
    },
    {
        "name": "simulate_investment",
        "description": "Run investment projections at different risk levels",
        "parameters": {
            "type": "object",
            "properties": {
                "amount": {"type": "number", "description": "Investment amount in PKR"},
                "months": {"type": "integer", "description": "Investment duration in months"}
            },
            "required": ["amount", "months"]
        }
    }
]


class OpenAIAgentWrapper:
    """Wraps OpenAI or Gemini API for the AI Wealth Companion chatbot.

    This wrapper:
    1. Checks for GEMINI_API_KEY first, then OPENAI_API_KEY
    2. Defines tools that map to existing MCP/service functions
    3. Processes messages through the chat API with tool calling
    4. Falls back to MasterOrchestrator for actual tool execution
    """

    def __init__(
        self,
        session: AsyncSession,
        user_id: UUID,
        conversation_id: UUID,
        language: str = "en",
    ):
        self.session = session
        self.user_id = user_id
        self.conversation_id = conversation_id
        self.language = language
        self.provider = None
        self.client = None

        # Check for Gemini first (user's preference)
        gemini_key = os.getenv("GEMINI_API_KEY")
        openai_key = os.getenv("OPENAI_API_KEY")

        logger.info("API keys found: GEMINI=%s, OPENAI=%s", bool(gemini_key), bool(openai_key))

        if gemini_key:
            # Use google-genai package (new SDK)
            logger.info("Attempting Gemini initialization...")
            try:
                from google import genai
                logger.info("google.genai imported successfully")
                self.gemini_client = genai.Client(api_key=gemini_key)
                logger.info("Gemini Client created successfully")
                self.provider = "gemini"
                logger.info("Gemini initialized - provider set to 'gemini'")
            except ImportError as ie:
                logger.error("IMPORT ERROR - google-genai not installed: %s", str(ie))
            except Exception as e:
                logger.error("INIT ERROR - Gemini failed: %s (type: %s)", str(e), type(e).__name__)
        else:
            logger.info("No GEMINI_API_KEY found in environment")

        if not self.provider and openai_key:
            try:
                from openai import AsyncOpenAI
                self.client = AsyncOpenAI(api_key=openai_key)
                self.provider = "openai"
                logger.info("Using OpenAI API")
            except Exception as e:
                logger.warning("Failed to initialize OpenAI: %s", str(e))

        if not self.provider:
            logger.warning("No AI provider configured, using MasterOrchestrator fallback")
            # Store debug info
            self.debug_info = {
                "gemini_key_present": bool(gemini_key),
                "openai_key_present": bool(openai_key),
            }

        # Initialize MasterOrchestrator for tool execution
        self.orchestrator = MasterOrchestrator(
            session=session,
            user_id=user_id,
            conversation_id=conversation_id,
            language=language,
        )

        # Initialize conversation service for history loading
        self.conversation_service = ConversationService(session)

    def _get_gemini_tools(self) -> List[Dict[str, Any]]:
        """Convert tool definitions to Gemini format."""
        from google.genai import types

        function_declarations = []
        for tool in TOOL_DEFINITIONS:
            function_declarations.append(
                types.FunctionDeclaration(
                    name=tool["name"],
                    description=tool["description"],
                    parameters=tool["parameters"]
                )
            )
        return [types.Tool(function_declarations=function_declarations)]

    def _get_openai_tools(self) -> List[Dict[str, Any]]:
        """Convert tool definitions to OpenAI format."""
        return [
            {
                "type": "function",
                "function": {
                    "name": tool["name"],
                    "description": tool["description"],
                    "parameters": tool["parameters"]
                }
            }
            for tool in TOOL_DEFINITIONS
        ]

    async def process(self, message: str) -> Dict[str, Any]:
        """Process a user message through the configured AI provider.

        Priority: Gemini > OpenAI > MasterOrchestrator fallback

        Args:
            message: The user's message

        Returns:
            Response dict with response text, intent, confidence, etc.
        """
        # Detect language
        detected_lang = detect_language(message)
        effective_lang = detected_lang if detected_lang != "en" else self.language

        # Fallback to MasterOrchestrator if no provider configured
        if not self.provider:
            logger.info("No AI provider set, using MasterOrchestrator fallback")
            result = await self.orchestrator.process(message)
            result["provider"] = "rule-based"
            result["_debug"] = getattr(self, 'debug_info', {})
            return result

        try:
            if self.provider == "gemini":
                return await self._call_gemini(message, effective_lang)
            else:
                return await self._call_openai(message, effective_lang)
        except Exception as e:
            logger.error("%s API error: %s, falling back to orchestrator", self.provider, str(e))
            return await self.orchestrator.process(message)

    async def _call_gemini(self, message: str, language: str) -> Dict[str, Any]:
        """Make Gemini API call using google-genai SDK."""
        import asyncio

        tool_calls_made = []

        # Build conversation with history
        contents = []
        try:
            history = await self.conversation_service.get_context_messages(
                self.conversation_id
            )
            for msg in history:
                role = "user" if msg["role"] == "user" else "model"
                contents.append({"role": role, "parts": [{"text": msg["content"]}]})
        except Exception as e:
            logger.warning("Failed to load conversation history: %s", str(e))

        # Add system instruction as first user message if no history
        if not contents:
            contents.append({"role": "user", "parts": [{"text": SYSTEM_PROMPT}]})
            contents.append({"role": "model", "parts": [{"text": "I understand. I'm your AI financial assistant ready to help!"}]})

        # Add current message
        contents.append({"role": "user", "parts": [{"text": message}]})

        def sync_generate():
            return self.gemini_client.models.generate_content(
                model="gemini-2.5-flash-lite",
                contents=contents
            )

        response = await asyncio.to_thread(sync_generate)

        # Extract text response
        response_text = response.text if hasattr(response, 'text') else str(response)

        # Check if the user's message requires data access (queries or actions)
        # We need to route to orchestrator for any financial operation
        lower_message = message.lower()

        # Keywords that indicate we need to fetch/modify user data
        action_keywords = ["record", "add", "create", "spent", "received", "earned", "paid"]
        query_keywords = ["show", "list", "how many", "how much", "what is", "what are",
                         "display", "get", "fetch", "my budget", "my transaction",
                         "my expense", "my income", "my spending", "my balance",
                         "budget status", "financial", "summary", "total", "health score"]

        needs_data_access = (
            any(word in lower_message for word in action_keywords) or
            any(word in lower_message for word in query_keywords)
        )

        if needs_data_access:
            # Let the orchestrator handle the actual data operation
            orchestrator_result = await self.orchestrator.process(message)
            tool_calls_made = orchestrator_result.get("tool_calls", [])
            # Use orchestrator's response which has actual data
            response_text = orchestrator_result.get("response", response_text)

        return {
            "response": response_text,
            "response_ur": None,
            "intent": "gemini_chat",
            "confidence": 0.95,
            "language_detected": language,
            "entities": None,
            "tool_calls": tool_calls_made,
            "provider": "gemini",
        }

    async def _call_openai(self, message: str, language: str) -> Dict[str, Any]:
        """Make the actual OpenAI API call with tool calling."""
        # Load conversation history for context
        messages = [{"role": "system", "content": SYSTEM_PROMPT}]

        try:
            history = await self.conversation_service.get_context_messages(
                self.conversation_id
            )
            # Add history messages (excluding the current one which will be added)
            for msg in history:
                if msg["role"] in ("user", "assistant"):
                    messages.append({"role": msg["role"], "content": msg["content"]})
        except Exception as e:
            logger.warning("Failed to load conversation history: %s", str(e))

        # Add current message
        messages.append({"role": "user", "content": message})

        # First call - may return tool calls
        response = await self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            tools=self._get_openai_tools(),
            tool_choice="auto",
        )

        assistant_message = response.choices[0].message
        tool_calls_made = []

        # Handle tool calls if any
        if assistant_message.tool_calls:
            messages.append(assistant_message)

            for tool_call in assistant_message.tool_calls:
                function_name = tool_call.function.name
                arguments = json.loads(tool_call.function.arguments)

                logger.info("OpenAI tool call: %s with args %s", function_name, arguments)

                # Execute tool via MasterOrchestrator
                tool_result = await self._execute_tool(function_name, arguments)
                tool_calls_made.append({
                    "name": function_name,
                    "arguments": arguments,
                    "result": tool_result
                })

                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": json.dumps(tool_result)
                })

            # Second call - get final response after tool execution
            final_response = await self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages,
            )
            response_text = final_response.choices[0].message.content
        else:
            response_text = assistant_message.content

        # Add financial disclaimer if needed
        if any(tc.get("name") == "simulate_investment" for tc in tool_calls_made):
            if FINANCIAL_DISCLAIMER not in response_text:
                response_text += f"\n\n{FINANCIAL_DISCLAIMER}"

        return {
            "response": response_text,
            "response_ur": None,
            "intent": self._infer_intent(tool_calls_made),
            "confidence": 0.95 if tool_calls_made else 0.85,
            "language_detected": language,
            "entities": self._extract_entities(tool_calls_made),
            "tool_calls": tool_calls_made,
            "provider": "openai",
        }

    async def _execute_tool(self, function_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a tool by delegating to the appropriate service.

        This maps AI function calls to our existing MCP tools/services.
        """
        # ============== TRANSACTION TOOLS ==============
        if function_name == "add_transaction":
            tx_type = arguments.get("transaction_type", "expense")
            amount = arguments.get("amount", 0)
            category = arguments.get("category", "Other")
            desc = arguments.get("description", "")
            msg = f"{'spent' if tx_type == 'expense' else 'received'} {amount} on {category}"
            if desc:
                msg += f" for {desc}"
            result = await self.orchestrator.process(msg)
            return {"success": True, "message": result.get("response", "Transaction recorded")}

        elif function_name == "list_transactions":
            tx_type = arguments.get("transaction_type", "all")
            limit = arguments.get("limit", 10)
            msg = f"show my last {limit} {tx_type if tx_type != 'all' else ''} transactions"
            result = await self.orchestrator.process(msg)
            return {"success": True, "transactions": result.get("response", "")}

        elif function_name == "update_transaction":
            tx_id = arguments.get("transaction_id", "last")
            amount = arguments.get("amount")
            category = arguments.get("category")
            msg = f"update {'last' if tx_id == 'last' else ''} transaction"
            if amount:
                msg += f" amount to {amount}"
            if category:
                msg += f" category to {category}"
            result = await self.orchestrator.process(msg)
            return {"success": True, "message": result.get("response", "Transaction updated")}

        elif function_name == "delete_transaction":
            tx_id = arguments.get("transaction_id", "last")
            msg = f"delete {'last' if tx_id == 'last' else ''} transaction"
            result = await self.orchestrator.process(msg)
            return {"success": True, "message": result.get("response", "Transaction deleted")}

        # ============== WALLET TOOLS ==============
        elif function_name == "create_wallet":
            name = arguments.get("name", "")
            balance = arguments.get("initial_balance", 0)
            wallet_type = arguments.get("wallet_type", "cash")
            msg = f"create {wallet_type} wallet {name} with balance {balance}"
            result = await self.orchestrator.process(msg)
            return {"success": True, "message": result.get("response", "Wallet created")}

        elif function_name == "list_wallets":
            result = await self.orchestrator.process("show my wallets")
            return {"success": True, "wallets": result.get("response", "")}

        elif function_name == "update_wallet":
            name = arguments.get("name", "")
            new_name = arguments.get("new_name")
            balance = arguments.get("balance")
            set_default = arguments.get("set_default", False)
            if set_default:
                msg = f"set {name} wallet as default"
            elif new_name:
                msg = f"rename wallet {name} to {new_name}"
            elif balance:
                msg = f"update wallet {name} balance to {balance}"
            else:
                msg = f"update wallet {name}"
            result = await self.orchestrator.process(msg)
            return {"success": True, "message": result.get("response", "Wallet updated")}

        elif function_name == "delete_wallet":
            name = arguments.get("name", "")
            result = await self.orchestrator.process(f"delete wallet {name}")
            return {"success": True, "message": result.get("response", "Wallet deleted")}

        # ============== GOAL TOOLS ==============
        elif function_name == "create_goal":
            name = arguments.get("name", "")
            target = arguments.get("target_amount", 0)
            deadline = arguments.get("deadline", "")
            msg = f"create goal {name} for {target}"
            if deadline:
                msg += f" by {deadline}"
            result = await self.orchestrator.process(msg)
            return {"success": True, "message": result.get("response", "Goal created")}

        elif function_name == "list_goals":
            status = arguments.get("status", "active")
            msg = f"show my {status if status != 'all' else ''} goals"
            result = await self.orchestrator.process(msg)
            return {"success": True, "goals": result.get("response", "")}

        elif function_name == "update_goal":
            name = arguments.get("name", "")
            add_amount = arguments.get("add_amount")
            new_target = arguments.get("new_target")
            if add_amount:
                msg = f"add {add_amount} to goal {name}"
            elif new_target:
                msg = f"update goal {name} target to {new_target}"
            else:
                msg = f"update goal {name}"
            result = await self.orchestrator.process(msg)
            return {"success": True, "message": result.get("response", "Goal updated")}

        elif function_name == "delete_goal":
            name = arguments.get("name", "")
            result = await self.orchestrator.process(f"delete goal {name}")
            return {"success": True, "message": result.get("response", "Goal deleted")}

        # ============== BUDGET TOOLS ==============
        elif function_name == "create_budget":
            category = arguments.get("category", "")
            amount = arguments.get("amount", 0)
            result = await self.orchestrator.process(f"set {category} budget to {amount}")
            return {"success": True, "message": result.get("response", "Budget created")}

        elif function_name == "list_budgets":
            result = await self.orchestrator.process("show my budgets")
            return {"success": True, "budgets": result.get("response", "")}

        elif function_name == "update_budget":
            category = arguments.get("category", "")
            amount = arguments.get("amount", 0)
            result = await self.orchestrator.process(f"update {category} budget to {amount}")
            return {"success": True, "message": result.get("response", "Budget updated")}

        elif function_name == "delete_budget":
            category = arguments.get("category", "")
            result = await self.orchestrator.process(f"delete budget for {category}")
            return {"success": True, "message": result.get("response", "Budget deleted")}

        # ============== TASK TOOLS ==============
        elif function_name == "create_task":
            title = arguments.get("title", "")
            due_date = arguments.get("due_date", "")
            priority = arguments.get("priority", "medium")
            msg = f"remind me to {title}"
            if due_date:
                msg += f" {due_date}"
            if priority == "high":
                msg = f"urgent: {msg}"
            result = await self.orchestrator.process(msg)
            return {"success": True, "message": result.get("response", "Task created")}

        elif function_name == "list_tasks":
            status = arguments.get("status", "active")
            msg = f"show my {status if status != 'all' else ''} tasks"
            result = await self.orchestrator.process(msg)
            return {"success": True, "tasks": result.get("response", "")}

        elif function_name == "complete_task":
            title = arguments.get("title", "")
            result = await self.orchestrator.process(f"complete task {title}")
            return {"success": True, "message": result.get("response", "Task completed")}

        elif function_name == "delete_task":
            title = arguments.get("title", "")
            result = await self.orchestrator.process(f"delete task {title}")
            return {"success": True, "message": result.get("response", "Task deleted")}

        # ============== ANALYSIS & TIPS TOOLS ==============
        elif function_name == "get_financial_summary":
            period = arguments.get("period", "month")
            result = await self.orchestrator.process(f"show my spending for this {period}")
            return {"success": True, "summary": result.get("response", "")}

        elif function_name == "get_health_score":
            result = await self.orchestrator.process("what is my financial health score")
            return {"success": True, "score": result.get("response", "")}

        elif function_name == "get_financial_tips":
            focus = arguments.get("focus", "general")
            result = await self.orchestrator.process(f"give me {focus} financial tips")
            return {"success": True, "tips": result.get("response", "")}

        elif function_name == "simulate_investment":
            amount = arguments.get("amount", 0)
            months = arguments.get("months", 12)
            result = await self.orchestrator.process(f"what if I invest {amount} for {months} months")
            return {"success": True, "projection": result.get("response", "")}

        else:
            return {"success": False, "error": f"Unknown function: {function_name}"}

    def _infer_intent(self, tool_calls: List[Dict]) -> str:
        """Infer the intent from tool calls."""
        if not tool_calls:
            return "general"

        name = tool_calls[0].get("name", "")
        intent_map = {
            "add_transaction": "record_transaction",
            "get_financial_summary": "query_spending",
            "create_budget": "create_budget",
            "get_budget_status": "query_budget",
            "simulate_investment": "investment_simulation",
            "create_task": "create_task",
            "list_tasks": "query_tasks",
            "get_health_score": "health_check",
        }
        return intent_map.get(name, "general")

    def _extract_entities(self, tool_calls: List[Dict]) -> Optional[Dict[str, Any]]:
        """Extract entities from tool call arguments."""
        if not tool_calls:
            return None

        entities = {}
        for tc in tool_calls:
            args = tc.get("arguments", {})
            for key, value in args.items():
                entities[key] = value
        return entities if entities else None
