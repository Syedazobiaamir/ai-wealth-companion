"""Specialized subagents for domain-specific tasks."""

from src.agents.subagents.budget_agent import BudgetAgent
from src.agents.subagents.spending_agent import SpendingAgent
from src.agents.subagents.investment_agent import InvestmentAgent
from src.agents.subagents.task_agent import TaskAgent

# Phase V: Event-driven agents
try:
    from src.agents.subagents.analytics_agent import AnalyticsAgent
    from src.agents.subagents.notification_agent import NotificationAgent
    _event_agents_available = True
except ImportError:
    AnalyticsAgent = None
    NotificationAgent = None
    _event_agents_available = False

__all__ = [
    "BudgetAgent",
    "SpendingAgent",
    "InvestmentAgent",
    "TaskAgent",
    # Phase V agents (may not be available if events module not installed)
    "AnalyticsAgent",
    "NotificationAgent",
]
