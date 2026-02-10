"""Master Orchestrator — routes messages to subagents with safety guardrails."""

import logging
from typing import Any, Dict
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from src.agents.registry import AgentRegistry
from src.agents.skills.finance_crud import parse_financial_command, classify_intent, extract_category, CATEGORY_ALIASES
from src.agents.skills.translation import detect_language, translate_response_hint, format_currency_urdu
from src.services.conversation import ConversationService

logger = logging.getLogger("ai.orchestrator")


def extract_category_from_reply(text: str) -> str:
    """Extract category from a simple reply like 'groceries' or 'food'."""
    # First try direct category extraction
    category = extract_category(text)
    if category:
        return category

    # If no match, use the text itself as category (capitalize first letter)
    cleaned = text.strip().title()
    if len(cleaned) > 0 and len(cleaned) < 50:
        return cleaned
    return None

# Safety guardrails embedded in all responses
FINANCIAL_DISCLAIMER = (
    "Note: I provide information based on your financial data, "
    "not professional financial advice. Consult a licensed advisor "
    "for investment decisions."
)

# Off-topic redirect
OFF_TOPIC_RESPONSE = (
    "I'm your financial assistant — I can help with budgets, transactions, "
    "spending analysis, and investment simulations. "
    "What would you like to know about your finances?"
)

# Greeting keywords
GREETING_KEYWORDS = {
    "hello", "hi", "hey", "good morning", "good evening",
    "salam", "assalam", "aoa",
}


class MasterOrchestrator:
    """Routes messages to appropriate subagent with safety and language handling."""

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
        self.conversation_service = ConversationService(session)

        # Auto-discover and instantiate all registered agents
        AgentRegistry.auto_discover()
        self.agents = AgentRegistry.create_agents(session, user_id)

    async def _get_pending_context(self) -> Dict[str, Any]:
        """Check recent messages for pending context (e.g., waiting for category)."""
        messages = await self.conversation_service.get_context_messages(self.conversation_id)
        if len(messages) < 2:
            return {}

        # Look at the last assistant message
        for i in range(len(messages) - 1, -1, -1):
            msg = messages[i]
            if msg["role"] == "assistant":
                content = msg["content"].lower()
                # Check if bot was asking for category
                if "what category" in content or "which category" in content:
                    # Find the previous user message with amount
                    for j in range(i - 1, -1, -1):
                        if messages[j]["role"] == "user":
                            prev_parsed = parse_financial_command(messages[j]["content"])
                            if prev_parsed.get("amount"):
                                return {
                                    "pending_intent": "create_transaction",
                                    "amount": prev_parsed["amount"],
                                    "transaction_type": prev_parsed.get("transaction_type", "expense"),
                                    "date": prev_parsed.get("date"),
                                }
                            break
                break
        return {}

    async def process(self, message: str) -> Dict[str, Any]:
        """Process a user message through routing, execution, and safety."""
        logger.info(
            "Processing message user=%s conv=%s lang=%s",
            self.user_id, self.conversation_id, self.language,
        )

        # Detect language
        detected_lang = detect_language(message)
        effective_lang = detected_lang if detected_lang != "en" else self.language

        # Check for pending context from previous messages
        pending = await self._get_pending_context()

        # Parse the financial command
        parsed = parse_financial_command(message)
        intent = parsed["intent"]
        confidence = parsed["confidence"]

        # Merge pending context if available
        if pending.get("pending_intent") == "create_transaction":
            # User might be providing just the category
            if not parsed.get("amount") and pending.get("amount"):
                parsed["amount"] = pending["amount"]
                parsed["transaction_type"] = pending.get("transaction_type", "expense")
                parsed["date"] = pending.get("date")
                parsed["intent"] = "create"
                intent = "create"
                confidence = 0.9
                # Try to extract category from current message
                if not parsed.get("category"):
                    parsed["category"] = extract_category_from_reply(message)
                logger.info("Merged pending context: amount=%s", parsed["amount"])

        logger.info("Parsed intent=%s confidence=%.2f lang=%s", intent, confidence, detected_lang)

        # Safety: check if off-topic
        if self._is_off_topic(message, intent, confidence):
            logger.info("Off-topic message detected, redirecting")
            return self._build_response(
                OFF_TOPIC_RESPONSE, "off_topic", 0.9, effective_lang
            )

        # Handle greetings
        if self._is_greeting(message):
            greeting = (
                "Hello! I'm your AI financial assistant. I can help you:\n"
                "  \u2022 Track income & expenses\n"
                "  \u2022 Manage budgets\n"
                "  \u2022 Analyze spending patterns\n"
                "  \u2022 Simulate investments\n"
                "  \u2022 Manage tasks & reminders\n\n"
                "What would you like to do?"
            )
            return self._build_response(greeting, "greeting", 0.95, effective_lang)

        # Clarification needed?
        if confidence < 0.7 and not parsed.get("amount") and not parsed.get("category"):
            logger.info("Low confidence (%.2f), asking for clarification", confidence)
            clarification = (
                f'I\'m not sure what you mean by "{message}". Could you be more specific?\n\n'
                "Try:\n"
                "  \u2022 'Show my expenses this month'\n"
                "  \u2022 'Add 500 groceries expense'\n"
                "  \u2022 'How are my budgets?'\n"
                "  \u2022 'Can I invest 50,000?'\n"
                "  \u2022 'Remind me to pay rent tomorrow'"
            )
            return self._build_response(clarification, "clarification", confidence, effective_lang)

        # Route to appropriate subagent via registry
        agent, route_name = AgentRegistry.route(message, parsed, self.agents)
        logger.info("Routing to %s agent", route_name)

        try:
            result = await agent.handle(message, parsed)
        except Exception as e:
            logger.error("Agent %s failed: %s", route_name, str(e), exc_info=True)
            return self._build_response(
                "I encountered an issue processing your request. Please try again.",
                "error", 0.0, effective_lang,
            )

        # Add safety disclaimer for investment responses
        response = result.get("response", "")
        if route_name == "investment":
            if FINANCIAL_DISCLAIMER not in response:
                response += f"\n\n{FINANCIAL_DISCLAIMER}"

        # Build final response with language support
        return self._build_response(
            response,
            result.get("intent", intent),
            result.get("confidence", confidence),
            effective_lang,
            entities=result.get("entities"),
            tool_calls=result.get("tool_calls"),
        )

    def _is_off_topic(self, message: str, intent: str, confidence: float) -> bool:
        """Check if message is completely unrelated to finance."""
        lower = message.lower()
        off_topic_signals = [
            "weather", "joke", "song", "recipe", "movie",
            "game", "sport", "politics", "code", "program",
        ]
        if any(s in lower for s in off_topic_signals):
            # But if it also has financial context, allow it
            financial_signals = [
                "money", "spend", "spent", "budget", "expense", "income",
                "save", "invest", "balance", "transaction", "paisa",
                "task", "remind", "bill", "due", "transport", "food",
                "groceries", "shopping", "salary", "rent", "utility",
            ]
            if not any(f in lower for f in financial_signals):
                return True
        return False

    def _is_greeting(self, message: str) -> bool:
        """Check if message is a greeting."""
        words = set(message.lower().split())
        return bool(words & GREETING_KEYWORDS) and len(words) <= 5

    def _build_response(
        self,
        response: str,
        intent: str,
        confidence: float,
        language: str,
        entities: Dict[str, Any] = None,
        tool_calls: list = None,
    ) -> Dict[str, Any]:
        """Build standardized response with optional Urdu translation."""
        result = {
            "response": response,
            "response_ur": None,
            "intent": intent,
            "confidence": confidence,
            "language_detected": language,
            "entities": entities,
            "tool_calls": tool_calls,
        }

        # Add Urdu hint if language is Urdu
        if language in ("ur", "ur-roman"):
            ur_hint = translate_response_hint(response, language)
            if ur_hint:
                result["response_ur"] = ur_hint

        return result
