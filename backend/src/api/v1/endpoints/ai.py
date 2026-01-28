"""AI-ready API endpoints for Phase III integration."""

from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel
from slowapi import Limiter
from slowapi.util import get_remote_address
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.deps import CurrentUser, get_db
from src.core.config import get_settings
from src.services.ai import AIService

router = APIRouter()
settings = get_settings()
limiter = Limiter(key_func=get_remote_address)


class QueryRequest(BaseModel):
    """Request schema for AI query."""

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


@router.get(
    "/context",
    response_model=Dict[str, Any],
    summary="Get AI context",
    description="Get user context for AI agents.",
)
async def get_ai_context(
    current_user: CurrentUser,
    session: AsyncSession = Depends(get_db),
) -> Dict[str, Any]:
    """Get comprehensive user context for AI agents."""
    service = AIService(session)
    return await service.get_user_context(current_user.id)


@router.post(
    "/query",
    response_model=Dict[str, Any],
    summary="Execute AI query",
    description="Execute natural language query (Phase III ready).",
)
@limiter.limit(settings.ai_rate_limit)
async def execute_query(
    request: Request,
    query_request: QueryRequest,
    current_user: CurrentUser,
    session: AsyncSession = Depends(get_db),
) -> Dict[str, Any]:
    """Process natural language query."""
    service = AIService(session)
    conversation_id = query_request.context.get("conversation_id") if query_request.context else None
    return await service.process_query(
        user_id=current_user.id,
        query=query_request.query,
        conversation_id=conversation_id,
    )


@router.post(
    "/insights/generate",
    response_model=Dict[str, Any],
    summary="Generate insights",
    description="Trigger insight generation (Phase III ready).",
)
async def generate_insights(
    request: InsightGenerateRequest,
    current_user: CurrentUser,
    session: AsyncSession = Depends(get_db),
) -> Dict[str, Any]:
    """Trigger insight generation job."""
    service = AIService(session)
    return await service.generate_insights(
        user_id=current_user.id,
        insight_types=request.insight_types,
        force_refresh=request.force_refresh,
    )


@router.get(
    "/insights",
    response_model=Dict[str, Any],
    summary="Get cached insights",
    description="Get cached AI insights for the user.",
)
async def get_insights(
    current_user: CurrentUser,
    insight_type: Optional[str] = None,
    session: AsyncSession = Depends(get_db),
) -> Dict[str, Any]:
    """Get cached insights."""
    service = AIService(session)
    insights = await service.get_cached_insights(
        user_id=current_user.id,
        insight_type=insight_type,
    )
    return {
        "success": True,
        "data": insights,
    }


@router.post(
    "/memory",
    response_model=Dict[str, Any],
    summary="Save agent memory",
    description="Save context memory for AI agent continuity.",
)
async def save_agent_memory(
    request: AgentMemoryRequest,
    current_user: CurrentUser,
    session: AsyncSession = Depends(get_db),
) -> Dict[str, Any]:
    """Save agent memory for context continuity."""
    service = AIService(session)
    return await service.save_agent_memory(
        user_id=current_user.id,
        memory_type=request.memory_type,
        content=request.content,
    )
