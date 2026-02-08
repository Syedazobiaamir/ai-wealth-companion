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
        "name": "get_budget_status",
        "description": "Check the status of budgets - spent vs limit",
        "parameters": {
            "type": "object",
            "properties": {
                "category": {"type": "string", "description": "Specific category to check, or leave empty for all"}
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
    },
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
        "description": "List tasks by status (active, overdue, completed)",
        "parameters": {
            "type": "object",
            "properties": {
                "status": {"type": "string", "enum": ["active", "overdue", "completed", "all"], "description": "Filter by task status"}
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

        if gemini_key:
            try:
                from google import genai
                self.client = genai.Client(api_key=gemini_key)
                self.provider = "gemini"
                logger.info("Using Gemini API")
            except Exception as e:
                logger.warning("Failed to initialize Gemini: %s", str(e))

        if not self.provider and openai_key:
            try:
                from openai import AsyncOpenAI
                self.client = AsyncOpenAI(api_key=openai_key)
                self.provider = "openai"
                logger.info("Using OpenAI API")
            except Exception as e:
                logger.warning("Failed to initialize OpenAI: %s", str(e))

        if not self.provider:
            logger.warning("No API key configured, using MasterOrchestrator fallback")

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
            logger.info("No AI provider, using MasterOrchestrator")
            return await self.orchestrator.process(message)

        try:
            if self.provider == "gemini":
                return await self._call_gemini(message, effective_lang)
            else:
                return await self._call_openai(message, effective_lang)
        except Exception as e:
            logger.error("%s API error: %s, falling back to orchestrator", self.provider, str(e))
            return await self.orchestrator.process(message)

    async def _call_gemini(self, message: str, language: str) -> Dict[str, Any]:
        """Make Gemini API call with tool calling."""
        import asyncio
        from google.genai import types

        tool_calls_made = []

        # Build contents with conversation history
        contents = []

        try:
            history = await self.conversation_service.get_context_messages(
                self.conversation_id
            )
            # Add history messages
            for msg in history:
                role = "user" if msg["role"] == "user" else "model"
                contents.append(
                    types.Content(
                        role=role,
                        parts=[types.Part(text=msg["content"])]
                    )
                )
        except Exception as e:
            logger.warning("Failed to load conversation history: %s", str(e))

        # Add current message
        contents.append(
            types.Content(
                role="user",
                parts=[types.Part(text=message)]
            )
        )

        # Generate config with system instruction and tools
        config = types.GenerateContentConfig(
            system_instruction=SYSTEM_PROMPT,
            tools=self._get_gemini_tools(),
        )

        # Make async call
        def sync_generate():
            return self.client.models.generate_content(
                model="gemini-2.0-flash",
                contents=contents,
                config=config,
            )

        response = await asyncio.to_thread(sync_generate)

        # Process response - handle function calls in a loop
        max_iterations = 5
        iteration = 0

        while iteration < max_iterations:
            iteration += 1

            # Check if we have a response with parts
            if not response.candidates or not response.candidates[0].content.parts:
                break

            # Check for function calls
            has_function_call = False
            for part in response.candidates[0].content.parts:
                if part.function_call:
                    has_function_call = True
                    function_call = part.function_call
                    function_name = function_call.name
                    arguments = dict(function_call.args) if function_call.args else {}

                    logger.info("Gemini tool call: %s with args %s", function_name, arguments)

                    # Execute tool
                    tool_result = await self._execute_tool(function_name, arguments)
                    tool_calls_made.append({
                        "name": function_name,
                        "arguments": arguments,
                        "result": tool_result
                    })

                    # Add assistant response and function result to contents
                    contents.append(response.candidates[0].content)
                    contents.append(
                        types.Content(
                            role="user",
                            parts=[
                                types.Part(
                                    function_response=types.FunctionResponse(
                                        name=function_name,
                                        response=tool_result
                                    )
                                )
                            ]
                        )
                    )

                    # Get next response
                    response = await asyncio.to_thread(sync_generate)
                    break  # Process one function call at a time

            if not has_function_call:
                break

        # Extract text response
        response_text = ""
        if response.candidates and response.candidates[0].content.parts:
            for part in response.candidates[0].content.parts:
                if part.text:
                    response_text += part.text

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
        # Use MasterOrchestrator to handle the actual execution
        if function_name == "add_transaction":
            tx_type = arguments.get("transaction_type", "expense")
            amount = arguments.get("amount", 0)
            category = arguments.get("category", "Other")
            msg = f"{'spent' if tx_type == 'expense' else 'received'} {amount} on {category}"
            result = await self.orchestrator.process(msg)
            return {"success": True, "message": result.get("response", "Transaction recorded")}

        elif function_name == "get_financial_summary":
            period = arguments.get("period", "month")
            result = await self.orchestrator.process(f"show my spending for this {period}")
            return {"success": True, "summary": result.get("response", "")}

        elif function_name == "create_budget":
            category = arguments.get("category", "")
            amount = arguments.get("amount", 0)
            result = await self.orchestrator.process(f"set {category} budget to {amount}")
            return {"success": True, "message": result.get("response", "Budget created")}

        elif function_name == "get_budget_status":
            category = arguments.get("category", "")
            msg = f"how is my {category} budget?" if category else "show my budgets"
            result = await self.orchestrator.process(msg)
            return {"success": True, "status": result.get("response", "")}

        elif function_name == "simulate_investment":
            amount = arguments.get("amount", 0)
            months = arguments.get("months", 12)
            result = await self.orchestrator.process(f"what if I invest {amount} for {months} months")
            return {"success": True, "projection": result.get("response", "")}

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
            msg = "show my overdue tasks" if status == "overdue" else "show my tasks"
            result = await self.orchestrator.process(msg)
            return {"success": True, "tasks": result.get("response", "")}

        elif function_name == "get_health_score":
            result = await self.orchestrator.process("what is my financial health score")
            return {"success": True, "score": result.get("response", "")}

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
