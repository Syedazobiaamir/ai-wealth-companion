"""Agent & Skill registry — auto-discovery, factory, and routing."""

from __future__ import annotations

import importlib
import logging
import pkgutil
from typing import Any, Dict, List, Optional, Tuple, Type
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from src.agents.base import BaseAgent, SkillWrapper

logger = logging.getLogger("ai.registry")


class AgentRegistry:
    """Central registry for subagents and skills."""

    _agent_classes: List[Type[BaseAgent]] = []
    _skills: Dict[str, SkillWrapper] = {}

    # ── decorators / registration ────────────────────────────────────

    @classmethod
    def register_agent(cls, agent_cls: Type[BaseAgent]) -> Type[BaseAgent]:
        """Class decorator — registers a BaseAgent subclass."""
        if agent_cls not in cls._agent_classes:
            cls._agent_classes.append(agent_cls)
            logger.debug("Registered agent: %s", agent_cls.metadata.name)
        return agent_cls

    @classmethod
    def register_skill(cls, wrapper: SkillWrapper) -> None:
        """Register a SkillWrapper."""
        cls._skills[wrapper.name] = wrapper
        logger.debug("Registered skill: %s", wrapper.name)

    # ── factory ──────────────────────────────────────────────────────

    @classmethod
    def create_agents(cls, session: AsyncSession, user_id: UUID) -> List[BaseAgent]:
        """Instantiate all registered agents for a given session/user."""
        return [agent_cls(session, user_id) for agent_cls in cls._agent_classes]

    # ── routing ──────────────────────────────────────────────────────

    @classmethod
    def route(
        cls,
        message: str,
        parsed: Dict[str, Any],
        agents: List[BaseAgent],
    ) -> Tuple[BaseAgent, str]:
        """Pick the best agent by ``can_handle`` score. Fallback: first agent
        whose metadata.name is ``"spending"`` (the general-purpose agent)."""

        best_agent: Optional[BaseAgent] = None
        best_score: float = -1.0
        fallback: Optional[BaseAgent] = None

        for agent in agents:
            score = agent.can_handle(message, parsed)
            if agent.metadata.name == "spending":
                fallback = agent
            if score > best_score:
                best_score = score
                best_agent = agent

        if best_agent is None or best_score <= 0:
            if fallback is not None:
                return fallback, fallback.metadata.name
            # Last resort: first registered agent
            return agents[0], agents[0].metadata.name

        return best_agent, best_agent.metadata.name

    # ── discovery ────────────────────────────────────────────────────

    @classmethod
    def auto_discover(cls) -> None:
        """Import every module under ``src.agents.subagents`` to trigger
        ``@register_agent`` decorators."""
        package_name = "src.agents.subagents"
        try:
            package = importlib.import_module(package_name)
        except ModuleNotFoundError:
            logger.warning("Could not import %s for auto-discovery", package_name)
            return

        for _importer, module_name, _is_pkg in pkgutil.iter_modules(package.__path__):
            full_name = f"{package_name}.{module_name}"
            try:
                importlib.import_module(full_name)
                logger.debug("Auto-discovered %s", full_name)
            except Exception:
                logger.warning("Failed to import %s", full_name, exc_info=True)

    # ── introspection ────────────────────────────────────────────────

    @classmethod
    def get_agent_classes(cls) -> List[Type[BaseAgent]]:
        return list(cls._agent_classes)

    @classmethod
    def get_skills(cls) -> Dict[str, SkillWrapper]:
        return dict(cls._skills)
