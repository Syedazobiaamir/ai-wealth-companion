"""Task Agent — handles task/reminder creation and queries through chat."""

import re
from datetime import date, timedelta
from typing import Any, Dict, Optional

from src.agents.base import AgentMetadata, BaseAgent
from src.agents.registry import AgentRegistry
from src.mcp.tools.task_tools import create_task, list_tasks, get_task_summary


@AgentRegistry.register_agent
class TaskAgent(BaseAgent):
    """Subagent specializing in task management and reminders."""

    metadata = AgentMetadata(
        name="task",
        description="Creates and manages tasks, reminders, and to-dos.",
        keywords={
            "task", "tasks", "todo", "remind", "reminder",
            "bill", "bills", "due", "pay", "overdue",
            "kaam", "yaad",
        },
    )

    async def handle(self, message: str, parsed: Dict[str, Any]) -> Dict[str, Any]:
        """Route by inferred intent: create, list overdue, or list all."""
        lower = message.lower()

        if self._is_create_intent(lower):
            return await self._create_task(message, lower)
        elif "overdue" in lower or "late" in lower or "missed" in lower:
            return await self._list_overdue()
        elif "summary" in lower or "status" in lower or "how many" in lower:
            return await self._task_summary()
        else:
            return await self._list_tasks()

    # ── intent detection helpers ─────────────────────────────────────

    @staticmethod
    def _is_create_intent(lower: str) -> bool:
        create_signals = [
            "remind", "add task", "create task", "new task",
            "set reminder", "need to", "don't forget", "schedule",
        ]
        return any(s in lower for s in create_signals)

    # ── handlers ─────────────────────────────────────────────────────

    async def _create_task(self, message: str, lower: str) -> Dict[str, Any]:
        title = self._extract_task_title(message, lower)
        if not title:
            return {
                "response": "What should I remind you about? For example: 'Remind me to pay rent tomorrow'",
                "intent": "create_task",
                "needs_clarification": True,
            }

        due = self._extract_due_date(lower)
        category = self._infer_category(lower)
        priority = self._infer_priority(lower)

        result = await create_task(
            user_id=self.user_id,
            session=self.session,
            title=title,
            priority=priority,
            category=category,
            due_date=due.isoformat() if due else None,
        )

        return {
            "response": result["message"],
            "intent": "create_task",
            "confidence": 0.9,
            "entities": result,
            "tool_calls": [{"tool": "create_task", "status": "success", "result": result}],
        }

    async def _list_overdue(self) -> Dict[str, Any]:
        result = await list_tasks(
            user_id=self.user_id, session=self.session, status="overdue"
        )

        if result["count"] == 0:
            return {
                "response": "Great news — you have no overdue tasks!",
                "intent": "list_tasks",
                "confidence": 0.9,
            }

        lines = [f"You have {result['count']} overdue task(s):"]
        for t in result["tasks"]:
            due = f" (due {t['due_date']})" if t["due_date"] else ""
            lines.append(f"  \u2022 {t['title']}{due}")

        return {
            "response": "\n".join(lines),
            "intent": "list_tasks",
            "confidence": 0.9,
            "entities": result,
        }

    async def _list_tasks(self) -> Dict[str, Any]:
        result = await list_tasks(
            user_id=self.user_id, session=self.session, status="active"
        )

        if result["count"] == 0:
            return {
                "response": "You don't have any active tasks. Want me to create one?",
                "intent": "list_tasks",
                "confidence": 0.9,
            }

        lines = [f"Your active tasks ({result['count']}):"]
        for t in result["tasks"]:
            due = f" (due {t['due_date']})" if t["due_date"] else ""
            pri = f" [{t['priority']}]" if t["priority"] != "medium" else ""
            lines.append(f"  \u2022 {t['title']}{due}{pri}")

        return {
            "response": "\n".join(lines),
            "intent": "list_tasks",
            "confidence": 0.9,
            "entities": result,
        }

    async def _task_summary(self) -> Dict[str, Any]:
        result = await get_task_summary(
            user_id=self.user_id, session=self.session,
        )

        lines = [
            f"Task Summary:",
            f"  Active: {result['active_tasks']}",
            f"  Completed: {result['completed_tasks']}",
            f"  Overdue: {result['overdue_count']}",
            f"  Due soon: {result['due_soon_count']}",
        ]

        if result["overdue_tasks"]:
            lines.append("\nOverdue:")
            for t in result["overdue_tasks"]:
                lines.append(f"  \u2022 {t['title']} (due {t['due_date']})")

        return {
            "response": "\n".join(lines),
            "intent": "task_summary",
            "confidence": 0.9,
            "entities": result,
        }

    # ── NLP extraction helpers ───────────────────────────────────────

    @staticmethod
    def _extract_task_title(original: str, lower: str) -> Optional[str]:
        """Pull the task title out of the message."""
        # "remind me to <title>" / "add task <title>"
        patterns = [
            r"remind\s+(?:me\s+)?to\s+(.+?)(?:\s+(?:tomorrow|today|next|on|by)\b|$)",
            r"(?:add|create|new)\s+task\s*[:\-]?\s*(.+?)(?:\s+(?:tomorrow|today|next|on|by)\b|$)",
            r"(?:need to|don't forget to|schedule)\s+(.+?)(?:\s+(?:tomorrow|today|next|on|by)\b|$)",
        ]
        for pat in patterns:
            m = re.search(pat, lower)
            if m:
                title = m.group(1).strip().rstrip(".,!?")
                if title:
                    # Use original casing for the title
                    start = lower.index(title)
                    return original[start : start + len(title)].strip()
        # Fallback: strip known prefixes and use the rest
        fallback = re.sub(
            r"^(remind\s+me\s+to|add\s+task|create\s+task|new\s+task|set\s+reminder)\s*[:\-]?\s*",
            "",
            lower,
        ).strip()
        if fallback and len(fallback) > 2:
            start = lower.index(fallback)
            return original[start : start + len(fallback)].strip().rstrip(".,!?")
        return None

    @staticmethod
    def _extract_due_date(lower: str) -> Optional[date]:
        """Extract due date from message text."""
        today = date.today()

        if "today" in lower:
            return today
        if "tomorrow" in lower:
            return today + timedelta(days=1)
        if "next week" in lower:
            return today + timedelta(weeks=1)
        if "next month" in lower:
            return today + timedelta(days=30)

        # day-of-week: "on monday", "by friday"
        days = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
        for i, day in enumerate(days):
            if day in lower:
                current_weekday = today.weekday()
                delta = (i - current_weekday) % 7
                if delta == 0:
                    delta = 7  # next occurrence
                return today + timedelta(days=delta)

        # Explicit date: "on 2026-02-15"
        m = re.search(r"(\d{4}-\d{2}-\d{2})", lower)
        if m:
            try:
                return date.fromisoformat(m.group(1))
            except ValueError:
                pass

        return None

    @staticmethod
    def _infer_category(lower: str) -> str:
        """Guess the task category from keywords."""
        if any(w in lower for w in ("bill", "pay", "rent", "utility", "electric", "gas", "water")):
            return "bills"
        if any(w in lower for w in ("save", "saving", "deposit")):
            return "savings"
        if any(w in lower for w in ("invest", "portfolio")):
            return "investment"
        if any(w in lower for w in ("budget", "review", "check")):
            return "review"
        return "other"

    @staticmethod
    def _infer_priority(lower: str) -> str:
        """Guess priority from keywords."""
        if any(w in lower for w in ("urgent", "important", "asap", "critical")):
            return "high"
        if any(w in lower for w in ("low priority", "whenever", "no rush")):
            return "low"
        return "medium"
