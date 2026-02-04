"""Reusable skills composable by agents."""

from src.agents.skills.finance_crud import parse_financial_command, classify_intent, extract_amount
from src.agents.skills.budget_analysis import analyze_budgets
from src.agents.skills.spending_insight import generate_spending_insight
from src.agents.skills.investment_sim import run_investment_simulation
from src.agents.skills.translation import detect_language, translate_response_hint, format_currency_urdu
from src.agents.skills.voice_interpret import process_voice_transcription

from src.agents.base import SkillWrapper
from src.agents.registry import AgentRegistry

__all__ = [
    "parse_financial_command",
    "classify_intent",
    "extract_amount",
    "analyze_budgets",
    "generate_spending_insight",
    "run_investment_simulation",
    "detect_language",
    "translate_response_hint",
    "format_currency_urdu",
    "process_voice_transcription",
]

# ── Register skills with the AgentRegistry ────────────────────────────
AgentRegistry.register_skill(SkillWrapper(
    name="parse_financial_command",
    description="Parse natural language into structured financial intents.",
    fn=parse_financial_command,
    input_schema={"type": "object", "properties": {"message": {"type": "string"}}, "required": ["message"]},
))

AgentRegistry.register_skill(SkillWrapper(
    name="classify_intent",
    description="Classify user message into a financial intent category.",
    fn=classify_intent,
    input_schema={"type": "object", "properties": {"message": {"type": "string"}}, "required": ["message"]},
))

AgentRegistry.register_skill(SkillWrapper(
    name="extract_amount",
    description="Extract a monetary amount from natural language text.",
    fn=extract_amount,
    input_schema={"type": "object", "properties": {"text": {"type": "string"}}, "required": ["text"]},
))

AgentRegistry.register_skill(SkillWrapper(
    name="analyze_budgets",
    description="Analyze budget usage, overspending, and provide coaching.",
    fn=analyze_budgets,
))

AgentRegistry.register_skill(SkillWrapper(
    name="generate_spending_insight",
    description="Generate spending insights including trends and category analysis.",
    fn=generate_spending_insight,
))

AgentRegistry.register_skill(SkillWrapper(
    name="run_investment_simulation",
    description="Run conservative/moderate/aggressive investment projections.",
    fn=run_investment_simulation,
))

AgentRegistry.register_skill(SkillWrapper(
    name="detect_language",
    description="Detect whether text is English, Urdu, or Roman-Urdu.",
    fn=detect_language,
    input_schema={"type": "object", "properties": {"text": {"type": "string"}}, "required": ["text"]},
))

AgentRegistry.register_skill(SkillWrapper(
    name="translate_response_hint",
    description="Generate an Urdu translation hint for a response string.",
    fn=translate_response_hint,
))

AgentRegistry.register_skill(SkillWrapper(
    name="process_voice_transcription",
    description="Normalize and clean a voice transcription for processing.",
    fn=process_voice_transcription,
    input_schema={"type": "object", "properties": {"text": {"type": "string"}}, "required": ["text"]},
))
