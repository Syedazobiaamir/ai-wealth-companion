"""Conversation repository for chat session data access."""

from datetime import datetime
from typing import List, Optional
from uuid import UUID

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.conversation import Conversation
from src.models.message import Message, MessageRole


class ConversationRepository:
    """Data access for conversations and messages."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_conversation(
        self, user_id: UUID, language: str = "en", title: Optional[str] = None
    ) -> Conversation:
        conversation = Conversation(
            user_id=user_id, language=language, title=title
        )
        self.session.add(conversation)
        await self.session.flush()
        await self.session.refresh(conversation)
        return conversation

    async def get_conversation(
        self, conversation_id: UUID, user_id: UUID
    ) -> Optional[Conversation]:
        stmt = select(Conversation).where(
            Conversation.id == conversation_id,
            Conversation.user_id == user_id,
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_conversations(
        self,
        user_id: UUID,
        active_only: bool = True,
        limit: int = 20,
        offset: int = 0,
    ) -> List[Conversation]:
        stmt = select(Conversation).where(Conversation.user_id == user_id)
        if active_only:
            stmt = stmt.where(Conversation.is_active == True)
        stmt = stmt.order_by(Conversation.updated_at.desc())
        stmt = stmt.offset(offset).limit(limit)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def count_conversations(
        self, user_id: UUID, active_only: bool = True
    ) -> int:
        from sqlalchemy import func

        stmt = select(func.count()).select_from(Conversation).where(
            Conversation.user_id == user_id
        )
        if active_only:
            stmt = stmt.where(Conversation.is_active == True)
        result = await self.session.execute(stmt)
        return result.scalar_one()

    async def mark_inactive(self, conversation_id: UUID) -> None:
        stmt = (
            update(Conversation)
            .where(Conversation.id == conversation_id)
            .values(is_active=False, updated_at=datetime.utcnow())
        )
        await self.session.execute(stmt)

    async def add_message(
        self,
        conversation_id: UUID,
        role: MessageRole,
        content: str,
        **kwargs,
    ) -> Message:
        message = Message(
            conversation_id=conversation_id,
            role=role,
            content=content,
            **kwargs,
        )
        self.session.add(message)
        # Update conversation message count and timestamp
        stmt = (
            update(Conversation)
            .where(Conversation.id == conversation_id)
            .values(
                message_count=Conversation.message_count + 1,
                updated_at=datetime.utcnow(),
            )
        )
        await self.session.execute(stmt)
        await self.session.flush()
        await self.session.refresh(message)
        return message

    async def get_messages(
        self,
        conversation_id: UUID,
        limit: int = 50,
        before_id: Optional[UUID] = None,
    ) -> List[Message]:
        stmt = select(Message).where(
            Message.conversation_id == conversation_id
        )
        if before_id:
            before_msg = await self.session.get(Message, before_id)
            if before_msg:
                stmt = stmt.where(Message.created_at < before_msg.created_at)
        stmt = stmt.order_by(Message.created_at.asc()).limit(limit)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_recent_messages(
        self, conversation_id: UUID, limit: int = 20
    ) -> List[Message]:
        """Get the most recent N messages for context window."""
        stmt = (
            select(Message)
            .where(Message.conversation_id == conversation_id)
            .order_by(Message.created_at.desc())
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        messages = list(result.scalars().all())
        messages.reverse()
        return messages
