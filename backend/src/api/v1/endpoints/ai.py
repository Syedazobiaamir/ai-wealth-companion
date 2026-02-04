"""AI API endpoints for Phase III conversational assistant."""

from typing import Any, Dict, List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel
from slowapi import Limiter
from slowapi.util import get_remote_address
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.deps import CurrentUser, get_db
from src.core.config import get_settings
from src.models.message import MessageRole, InputMethod
from src.services.ai import AIService
from src.services.conversation import ConversationService

router = APIRouter()
settings = get_settings()
limiter = Limiter(key_func=get_remote_address)


# ── Request schemas ──────────────────────────────────────────────────

class ChatRequest(BaseModel):
    """POST /ai/chat request."""
    message: str
    conversation_id: Optional[str] = None
    language: Optional[str] = None
    input_method: str = "text"
    use_openai: bool = True  # Use OpenAI Agents SDK (set to False to use fallback)


class QueryRequest(BaseModel):
    """Legacy query request (backward compat)."""
    query: str
    context: Optional[Dict[str, Any]] = None


class InsightGenerateRequest(BaseModel):
    """Request schema for insight generation."""
    insight_types: List[str]
    force_refresh: bool = False


class AgentMemoryRequest(BaseModel):
    """Request schema for saving agent memory."""
    memory_type: str
    content: Dict[str, Any]


class LanguageRequest(BaseModel):
    """POST /ai/language request."""
    language: str


class InvestmentRequest(BaseModel):
    """POST /ai/simulate-investment request."""
    investment_amount: float
    time_horizon_months: int
    currency: str = "PKR"


# ── Chat endpoint (Phase III primary) ────────────────────────────────

@router.post(
    "/chat",
    response_model=Dict[str, Any],
    summary="Send message to AI assistant",
    description="Send a natural language message and receive an AI response.",
)
@limiter.limit("30/minute")
async def chat(
    request: Request,
    body: ChatRequest,
    current_user: CurrentUser,
    session: AsyncSession = Depends(get_db),
) -> Dict[str, Any]:
    """Process chat message through the agent pipeline."""
    conv_service = ConversationService(session)
    ai_service = AIService(session)

    # Parse conversation_id
    conv_id = None
    if body.conversation_id:
        try:
            conv_id = UUID(body.conversation_id)
        except ValueError:
            pass

    # Get or create conversation
    conversation = await conv_service.get_or_create_conversation(
        user_id=current_user.id,
        conversation_id=conv_id,
        language=body.language or "en",
    )

    # Store user message
    input_method = InputMethod.voice if body.input_method == "voice" else InputMethod.text
    await conv_service.add_message(
        conversation_id=conversation.id,
        role=MessageRole.user,
        content=body.message,
        input_method=input_method,
    )

    # Process through agent pipeline (OpenAI Agents SDK or fallback)
    import time
    start = time.time()
    result = await ai_service.process_chat(
        user_id=current_user.id,
        message=body.message,
        conversation_id=conversation.id,
        language=body.language or conversation.language,
        use_openai=body.use_openai,
    )
    elapsed_ms = int((time.time() - start) * 1000)

    # Store assistant response
    assistant_msg = await conv_service.add_message(
        conversation_id=conversation.id,
        role=MessageRole.assistant,
        content=result.get("response", ""),
        content_ur=result.get("response_ur"),
        intent=result.get("intent"),
        entities=result.get("entities"),
        tool_calls=result.get("tool_calls"),
        confidence=result.get("confidence"),
        processing_time_ms=elapsed_ms,
    )

    return {
        "conversation_id": str(conversation.id),
        "message_id": str(assistant_msg.id),
        "response": result.get("response", ""),
        "response_ur": result.get("response_ur"),
        "intent": result.get("intent"),
        "entities": result.get("entities"),
        "tool_calls": result.get("tool_calls"),
        "confidence": result.get("confidence", 0),
        "language_detected": result.get("language_detected", "en"),
    }


# ── Conversation endpoints ───────────────────────────────────────────

@router.get(
    "/conversations",
    response_model=Dict[str, Any],
    summary="List user conversations",
)
async def list_conversations(
    current_user: CurrentUser,
    limit: int = 20,
    offset: int = 0,
    active_only: bool = True,
    session: AsyncSession = Depends(get_db),
) -> Dict[str, Any]:
    service = ConversationService(session)
    return await service.list_conversations(
        user_id=current_user.id,
        active_only=active_only,
        limit=limit,
        offset=offset,
    )


@router.get(
    "/conversations/{conversation_id}/messages",
    response_model=Dict[str, Any],
    summary="Get messages in a conversation",
)
async def get_messages(
    conversation_id: str,
    current_user: CurrentUser,
    limit: int = 50,
    before: Optional[str] = None,
    session: AsyncSession = Depends(get_db),
) -> Dict[str, Any]:
    try:
        conv_uuid = UUID(conversation_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid conversation ID")

    service = ConversationService(session)
    conv = await service.get_conversation(conv_uuid, current_user.id)
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")

    before_uuid = None
    if before:
        try:
            before_uuid = UUID(before)
        except ValueError:
            pass

    return await service.get_messages(conv_uuid, limit, before_uuid)


# ── Insights endpoint ────────────────────────────────────────────────

@router.get(
    "/insights",
    response_model=Dict[str, Any],
    summary="Get AI-generated financial insights",
)
async def get_insights(
    current_user: CurrentUser,
    limit: int = 5,
    type: Optional[str] = None,
    severity: Optional[str] = None,
    session: AsyncSession = Depends(get_db),
) -> Dict[str, Any]:
    service = AIService(session)
    insights = await service.get_insights(
        user_id=current_user.id, limit=limit,
        insight_type=type, severity=severity,
    )
    return {"insights": insights}


# ── Health score endpoint ────────────────────────────────────────────

@router.get(
    "/health-score",
    response_model=Dict[str, Any],
    summary="Get financial health score",
)
async def get_health_score(
    current_user: CurrentUser,
    month: Optional[int] = None,
    year: Optional[int] = None,
    session: AsyncSession = Depends(get_db),
) -> Dict[str, Any]:
    service = AIService(session)
    return await service.get_health_score(
        user_id=current_user.id, month=month, year=year
    )


# ── Investment simulation ────────────────────────────────────────────

@router.post(
    "/simulate-investment",
    response_model=Dict[str, Any],
    summary="Run investment simulation",
)
async def simulate_investment(
    body: InvestmentRequest,
    current_user: CurrentUser,
    session: AsyncSession = Depends(get_db),
) -> Dict[str, Any]:
    from src.mcp.tools.investment_tools import simulate_investment as sim_tool
    result = await sim_tool(
        user_id=current_user.id,
        session=session,
        amount=body.investment_amount,
        months=body.time_horizon_months,
    )
    return result


# ── Language preference ──────────────────────────────────────────────

@router.post(
    "/language",
    response_model=Dict[str, Any],
    summary="Set AI language preference",
)
async def set_language(
    body: LanguageRequest,
    current_user: CurrentUser,
    session: AsyncSession = Depends(get_db),
) -> Dict[str, Any]:
    if body.language not in ("en", "ur"):
        raise HTTPException(status_code=400, detail="Supported languages: en, ur")
    # Persist preference in the database
    from sqlalchemy import select
    from src.models.user import User
    result = await session.execute(select(User).where(User.id == current_user.id))
    user = result.scalars().first()
    if user:
        user.preferred_locale = body.language
        session.add(user)
        await session.commit()
    return {"language": body.language, "message": f"Language preference updated to {'Urdu' if body.language == 'ur' else 'English'}"}


# ── Legacy endpoints (backward compatibility) ────────────────────────

@router.get(
    "/context",
    response_model=Dict[str, Any],
    summary="Get AI context",
)
async def get_ai_context(
    current_user: CurrentUser,
    session: AsyncSession = Depends(get_db),
) -> Dict[str, Any]:
    service = AIService(session)
    return await service.get_user_context(current_user.id)


@router.post(
    "/query",
    response_model=Dict[str, Any],
    summary="Execute AI query (legacy)",
)
@limiter.limit(settings.ai_rate_limit)
async def execute_query(
    request: Request,
    query_request: QueryRequest,
    current_user: CurrentUser,
    session: AsyncSession = Depends(get_db),
) -> Dict[str, Any]:
    service = AIService(session)
    conversation_id = query_request.context.get("conversation_id") if query_request.context else None
    return await service.process_query(
        user_id=current_user.id,
        query=query_request.query,
        conversation_id=conversation_id,
    )


@router.post("/insights/generate", response_model=Dict[str, Any], summary="Generate insights")
async def generate_insights(
    request: InsightGenerateRequest,
    current_user: CurrentUser,
    session: AsyncSession = Depends(get_db),
) -> Dict[str, Any]:
    service = AIService(session)
    return await service.generate_insights(
        user_id=current_user.id,
        insight_types=request.insight_types,
        force_refresh=request.force_refresh,
    )


@router.post("/memory", response_model=Dict[str, Any], summary="Save agent memory")
async def save_agent_memory(
    request: AgentMemoryRequest,
    current_user: CurrentUser,
    session: AsyncSession = Depends(get_db),
) -> Dict[str, Any]:
    service = AIService(session)
    return await service.save_agent_memory(
        user_id=current_user.id,
        memory_type=request.memory_type,
        content=request.content,
    )
