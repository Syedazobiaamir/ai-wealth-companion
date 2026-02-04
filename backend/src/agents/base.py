"""Base classes for the agent framework — metadata, abstract agent, skill wrapper."""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, Optional, Set
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession


@dataclass
class AgentMetadata:
    """Describes an agent's identity and routing hints."""

    name: str
    description: str
    keywords: Set[str] = field(default_factory=set)
    version: str = "1.0.0"


class BaseAgent(ABC):
    """Abstract base for all subagents."""

    metadata: AgentMetadata  # subclasses must set this as a class attribute

    def __init__(self, session: AsyncSession, user_id: UUID):
        self.session = session
        self.user_id = user_id

    @abstractmethod
    async def handle(self, message: str, parsed: Dict[str, Any]) -> Dict[str, Any]:
        """Process a routed message. Return a response dict."""

    def can_handle(self, message: str, parsed: Dict[str, Any]) -> float:
        """Return a confidence score (0-1) for handling *message*.

        Default implementation: keyword matching against ``metadata.keywords``.
        Subclasses may override for richer logic.
        """
        if not self.metadata.keywords:
            return 0.0
        lower = message.lower()
        matches = sum(1 for kw in self.metadata.keywords if kw in lower)
        if matches == 0:
            return 0.0
        return min(1.0, matches * 0.3)


@dataclass
class SkillWrapper:
    """Wraps a plain function so it can be registered as a skill."""

    name: str
    description: str
    fn: Callable
    input_schema: Optional[Dict[str, Any]] = None
