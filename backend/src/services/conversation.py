"""Conversation service for chat session management."""

from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional
from uuid import UUID

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.conversation import Conversation
from src.models.message import Message, MessageRole, InputMethod
from src.repositories.conversation import ConversationRepository


class ConversationService:
    """Business logic for conversation management."""

    CONTEXT_WINDOW = 20  # Number of recent messages to include

    def __init__(self, session: AsyncSession):
        self.session = session
        self.repo = ConversationRepository(session)

    async def create_conversation(
        self, user_id: UUID, language: str = "en"
    ) -> Conversation:
        return await self.repo.create_conversation(
            user_id=user_id, language=language
        )

    async def get_or_create_conversation(
        self,
        user_id: UUID,
        conversation_id: Optional[UUID] = None,
        language: str = "en",
    ) -> Conversation:
        if conversation_id:
            conv = await self.repo.get_conversation(conversation_id, user_id)
            if conv and conv.is_active:
                return conv
        return await self.repo.create_conversation(
            user_id=user_id, language=language
        )

    async def get_conversation(
        self, conversation_id: UUID, user_id: UUID
    ) -> Optional[Conversation]:
        return await self.repo.get_conversation(conversation_id, user_id)

    async def list_conversations(
        self,
        user_id: UUID,
        active_only: bool = True,
        limit: int = 20,
        offset: int = 0,
    ) -> Dict[str, Any]:
        conversations = await self.repo.list_conversations(
            user_id, active_only, limit, offset
        )
        total = await self.repo.count_conversations(user_id, active_only)
        return {
            "conversations": [
                {
                    "id": str(c.id),
                    "title": c.title or "New Chat",
                    "language": c.language,
                    "message_count": c.message_count,
                    "is_active": c.is_active,
                    "created_at": c.created_at.isoformat() + "Z",
                    "updated_at": c.updated_at.isoformat() + "Z",
                }
                for c in conversations
            ],
            "total": total,
        }

    async def add_message(
        self,
        conversation_id: UUID,
        role: MessageRole,
        content: str,
        content_ur: Optional[str] = None,
        intent: Optional[str] = None,
        entities: Optional[Dict[str, Any]] = None,
        tool_calls: Optional[List[Dict[str, Any]]] = None,
        confidence: Optional[float] = None,
        input_method: InputMethod = InputMethod.text,
        processing_time_ms: Optional[int] = None,
    ) -> Message:
        return await self.repo.add_message(
            conversation_id=conversation_id,
            role=role,
            content=content,
            content_ur=content_ur,
            intent=intent,
            entities=entities,
            tool_calls=tool_calls,
            confidence=confidence,
            input_method=input_method,
            processing_time_ms=processing_time_ms,
        )

    async def get_messages(
        self,
        conversation_id: UUID,
        limit: int = 50,
        before_id: Optional[UUID] = None,
    ) -> Dict[str, Any]:
        messages = await self.repo.get_messages(
            conversation_id, limit + 1, before_id
        )
        has_more = len(messages) > limit
        if has_more:
            messages = messages[:limit]
        return {
            "messages": [
                {
                    "id": str(m.id),
                    "role": m.role.value,
                    "content": m.content,
                    "content_ur": m.content_ur,
                    "intent": m.intent,
                    "entities": m.entities,
                    "tool_calls": m.tool_calls,
                    "confidence": m.confidence,
                    "input_method": m.input_method.value,
                    "processing_time_ms": m.processing_time_ms,
                    "created_at": m.created_at.isoformat() + "Z",
                }
                for m in messages
            ],
            "has_more": has_more,
        }

    async def get_context_messages(
        self, conversation_id: UUID
    ) -> List[Dict[str, str]]:
        """Get recent messages formatted for agent context window."""
        messages = await self.repo.get_recent_messages(
            conversation_id, self.CONTEXT_WINDOW
        )
        return [
            {"role": m.role.value, "content": m.content} for m in messages
        ]

    async def close_conversation(self, conversation_id: UUID) -> None:
        await self.repo.mark_inactive(conversation_id)

    async def cleanup_idle_conversations(
        self, idle_minutes: int = 30
    ) -> int:
        """Close conversations idle for more than idle_minutes. Returns count closed."""
        cutoff = datetime.utcnow() - timedelta(minutes=idle_minutes)
        stmt = (
            update(Conversation)
            .where(
                Conversation.is_active == True,
                Conversation.updated_at < cutoff,
            )
            .values(is_active=False)
        )
        result = await self.session.execute(stmt)
        return result.rowcount
