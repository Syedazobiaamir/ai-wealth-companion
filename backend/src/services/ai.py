"""AI service — orchestrates agent pipeline, insights, health scores."""

from datetime import date, datetime, timedelta
from decimal import Decimal
from typing import Any, Dict, List, Optional
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.budget import Budget
from src.models.category import Category
from src.models.goal import Goal, GoalStatus
from src.models.insight_cache import InsightCache, InsightType, InsightSeverity
from src.models.agent_memory import AgentMemory
from src.models.transaction import Transaction, TransactionType
from src.models.user import User
from src.models.wallet import Wallet


class AIService:
    """Service for AI context, agent pipeline, insights, and health scores."""

    def __init__(self, session: AsyncSession):
        self.session = session

    # ── Agent pipeline ───────────────────────────────────────────────

    async def process_chat(
        self,
        user_id: UUID,
        message: str,
        conversation_id: UUID,
        language: str = "en",
        use_openai: bool = True,
    ) -> Dict[str, Any]:
        """Process a chat message through the AI agent pipeline.

        Args:
            user_id: The user's ID
            message: The chat message to process
            conversation_id: The conversation ID
            language: Preferred language (en, ur, ur-roman)
            use_openai: If True, use OpenAI Agents SDK; if False, use MasterOrchestrator

        Returns:
            Response dict with message, intent, entities, tool_calls, etc.
        """
        import os

        # Use OpenAI wrapper if API key is available and use_openai is True
        if use_openai and os.getenv("OPENAI_API_KEY"):
            from src.agents.openai_wrapper import OpenAIAgentWrapper

            wrapper = OpenAIAgentWrapper(
                session=self.session,
                user_id=user_id,
                conversation_id=conversation_id,
                language=language,
            )
            return await wrapper.process(message)

        # Fallback to MasterOrchestrator
        from src.agents.master import MasterOrchestrator

        orchestrator = MasterOrchestrator(
            session=self.session,
            user_id=user_id,
            conversation_id=conversation_id,
            language=language,
        )
        return await orchestrator.process(message)

    # ── Insights ─────────────────────────────────────────────────────

    async def get_insights(
        self,
        user_id: UUID,
        limit: int = 5,
        insight_type: Optional[str] = None,
        severity: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Get active insights, generating fresh ones if needed."""
        # Check for fresh insights first
        stmt = select(InsightCache).where(
            InsightCache.user_id == user_id,
        )
        if insight_type:
            stmt = stmt.where(InsightCache.insight_type == insight_type)
        if severity:
            stmt = stmt.where(InsightCache.severity == severity)
        stmt = stmt.order_by(InsightCache.created_at.desc()).limit(limit)
        result = await self.session.execute(stmt)
        insights = list(result.scalars().all())

        # If no insights exist, generate them
        if not insights:
            await self._generate_budget_insights(user_id)
            result = await self.session.execute(stmt)
            insights = list(result.scalars().all())

        return [
            {
                "id": str(i.id),
                "type": i.insight_type.value if hasattr(i.insight_type, 'value') else i.insight_type,
                "severity": i.severity.value if hasattr(i.severity, 'value') else i.severity,
                "title": i.title,
                "content": i.content,
                "content_ur": i.content_ur,
                "action_suggestion": i.extra_data.get("action_suggestion") if i.extra_data else None,
                "data": i.extra_data,
                "confidence": float(i.confidence_score) if hasattr(i, 'confidence_score') and i.confidence_score else 0.8,
                "created_at": i.created_at.isoformat() + "Z",
            }
            for i in insights
        ]

    async def _generate_budget_insights(self, user_id: UUID) -> None:
        """Generate insights from budget status."""
        today = date.today()
        month_start = date(today.year, today.month, 1)

        stmt = (
            select(Budget, Category.name, Category.emoji)
            .join(Category, Budget.category_id == Category.id)
            .where(
                Budget.user_id == user_id,
                Budget.month == today.month,
                Budget.year == today.year,
            )
        )
        result = await self.session.execute(stmt)
        rows = result.all()

        for row in rows:
            budget = row.Budget
            spent_stmt = select(func.coalesce(func.sum(Transaction.amount), 0)).where(
                Transaction.user_id == user_id,
                Transaction.category_id == budget.category_id,
                Transaction.type == TransactionType.expense,
                Transaction.transaction_date >= month_start,
                Transaction.is_deleted == False,
            )
            spent_result = await self.session.execute(spent_stmt)
            spent = float(spent_result.scalar_one())
            limit_amt = float(budget.limit_amount)
            pct = (spent / limit_amt * 100) if limit_amt > 0 else 0

            if pct >= 100:
                insight = InsightCache(
                    user_id=user_id,
                    insight_type=InsightType.budget_recommendation,
                    insight_key=f"budget_exceeded_{budget.id}",
                    title=f"{row.emoji or '📦'} {row.name} Over Budget",
                    content=f"Your {row.name} spending is {pct:.0f}% of budget ({spent:,.0f} / {limit_amt:,.0f}). Consider reducing spending in this category.",
                    severity=InsightSeverity.alert,
                    related_category_id=budget.category_id,
                    related_amount=Decimal(str(spent)),
                    extra_data={
                        "category": row.name,
                        "budget": limit_amt,
                        "spent": spent,
                        "percentage": round(pct),
                        "action_suggestion": f"Reduce {row.name} spending by {spent - limit_amt:,.0f}",
                    },
                    valid_from=datetime.utcnow(),
                    valid_until=datetime.utcnow() + timedelta(days=7),
                )
                self.session.add(insight)
            elif pct >= 80:
                insight = InsightCache(
                    user_id=user_id,
                    insight_type=InsightType.budget_recommendation,
                    insight_key=f"budget_warning_{budget.id}",
                    title=f"{row.emoji or '📦'} {row.name} Budget Warning",
                    content=f"Your {row.name} spending is at {pct:.0f}% of budget. You have {limit_amt - spent:,.0f} remaining.",
                    severity=InsightSeverity.warning,
                    related_category_id=budget.category_id,
                    extra_data={
                        "category": row.name,
                        "budget": limit_amt,
                        "spent": spent,
                        "percentage": round(pct),
                        "action_suggestion": f"Watch {row.name} spending — only {limit_amt - spent:,.0f} remaining",
                    },
                    valid_from=datetime.utcnow(),
                    valid_until=datetime.utcnow() + timedelta(days=7),
                )
                self.session.add(insight)

        await self.session.flush()

    # ── Health Score ─────────────────────────────────────────────────

    async def get_health_score(
        self,
        user_id: UUID,
        month: Optional[int] = None,
        year: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Calculate financial health score (0-100)."""
        today = date.today()
        m = month or today.month
        y = year or today.year
        month_start = date(y, m, 1)
        if m == 12:
            month_end = date(y + 1, 1, 1) - timedelta(days=1)
        else:
            month_end = date(y, m + 1, 1) - timedelta(days=1)

        # Budget adherence (40%)
        budget_adherence = await self._calc_budget_adherence(user_id, m, y, month_start, month_end)

        # Savings rate (30%)
        savings_data = await self._calc_savings_rate(user_id, month_start, month_end)
        savings_rate = savings_data["rate"]

        # Spending consistency (20%)
        consistency = await self._calc_spending_consistency(user_id, month_start, month_end)

        # Goal progress (10%)
        goal_progress = await self._calc_goal_progress(user_id)

        overall = int(
            0.4 * budget_adherence["score"]
            + 0.3 * savings_data["score"]
            + 0.2 * consistency["score"]
            + 0.1 * goal_progress["score"]
        )

        if overall >= 80:
            grade = "Excellent"
        elif overall >= 60:
            grade = "Good"
        elif overall >= 40:
            grade = "Fair"
        else:
            grade = "Needs Improvement"

        recommendations = []
        if budget_adherence["score"] < 70:
            recommendations.append(f"Reduce spending in over-budget categories to improve adherence ({budget_adherence['detail']}).")
        if savings_data["score"] < 70:
            recommendations.append(f"Your savings rate is {savings_rate:.0f}%. Aim for at least 20%.")
        if goal_progress["score"] < 50:
            recommendations.append("Consider increasing contributions toward your financial goals.")

        return {
            "overall_score": overall,
            "grade": grade,
            "components": {
                "budget_adherence": {"score": budget_adherence["score"], "weight": 0.4, "detail": budget_adherence["detail"]},
                "savings_rate": {"score": savings_data["score"], "weight": 0.3, "detail": savings_data["detail"]},
                "spending_consistency": {"score": consistency["score"], "weight": 0.2, "detail": consistency["detail"]},
                "goal_progress": {"score": goal_progress["score"], "weight": 0.1, "detail": goal_progress["detail"]},
            },
            "recommendations": recommendations,
            "month": m,
            "year": y,
            "trend": "stable",
        }

    async def _calc_budget_adherence(self, user_id, month, year, start, end):
        stmt = select(Budget).where(Budget.user_id == user_id, Budget.month == month, Budget.year == year)
        result = await self.session.execute(stmt)
        budgets = list(result.scalars().all())
        if not budgets:
            return {"score": 50, "detail": "No budgets set"}
        within = 0
        for b in budgets:
            spent_stmt = select(func.coalesce(func.sum(Transaction.amount), 0)).where(
                Transaction.user_id == user_id, Transaction.category_id == b.category_id,
                Transaction.type == TransactionType.expense,
                Transaction.transaction_date >= start, Transaction.transaction_date <= end,
                Transaction.is_deleted == False,
            )
            r = await self.session.execute(spent_stmt)
            if float(r.scalar_one()) <= float(b.limit_amount):
                within += 1
        score = int(within / len(budgets) * 100)
        return {"score": score, "detail": f"{within} of {len(budgets)} budgets within limit"}

    async def _calc_savings_rate(self, user_id, start, end):
        inc_stmt = select(func.coalesce(func.sum(Transaction.amount), 0)).where(
            Transaction.user_id == user_id, Transaction.type == TransactionType.income,
            Transaction.transaction_date >= start, Transaction.transaction_date <= end, Transaction.is_deleted == False,
        )
        exp_stmt = select(func.coalesce(func.sum(Transaction.amount), 0)).where(
            Transaction.user_id == user_id, Transaction.type == TransactionType.expense,
            Transaction.transaction_date >= start, Transaction.transaction_date <= end, Transaction.is_deleted == False,
        )
        inc = float((await self.session.execute(inc_stmt)).scalar_one())
        exp = float((await self.session.execute(exp_stmt)).scalar_one())
        rate = ((inc - exp) / inc * 100) if inc > 0 else 0
        score = min(100, max(0, int(rate * 5)))  # 20% savings = 100
        return {"score": score, "rate": rate, "detail": f"Saving {rate:.0f}% of income"}

    async def _calc_spending_consistency(self, user_id, start, end):
        # Simplified: fewer large variance days = better
        stmt = (
            select(Transaction.transaction_date, func.sum(Transaction.amount))
            .where(
                Transaction.user_id == user_id, Transaction.type == TransactionType.expense,
                Transaction.transaction_date >= start, Transaction.transaction_date <= end,
                Transaction.is_deleted == False,
            )
            .group_by(Transaction.transaction_date)
        )
        result = await self.session.execute(stmt)
        daily = [float(r[1]) for r in result.all()]
        if len(daily) < 2:
            return {"score": 70, "detail": "Not enough data"}
        import statistics
        mean = statistics.mean(daily)
        stdev = statistics.stdev(daily)
        cv = stdev / mean if mean > 0 else 0
        score = max(0, min(100, int(100 - cv * 50)))
        if cv < 0.5:
            detail = "Low daily variation"
        elif cv < 1.0:
            detail = "Moderate daily variation"
        else:
            detail = "High daily variation"
        return {"score": score, "detail": detail}

    async def _calc_goal_progress(self, user_id):
        stmt = select(Goal).where(Goal.user_id == user_id, Goal.status == GoalStatus.active)
        result = await self.session.execute(stmt)
        goals = list(result.scalars().all())
        if not goals:
            return {"score": 50, "detail": "No active goals"}
        avg_pct = sum(
            float(g.current_amount) / float(g.target_amount) * 100 if g.target_amount > 0 else 0
            for g in goals
        ) / len(goals)
        score = min(100, int(avg_pct))
        on_track = sum(1 for g in goals if float(g.current_amount) / float(g.target_amount) >= 0.5 if g.target_amount > 0)
        return {"score": score, "detail": f"{on_track} goals on track"}

    # ── Legacy methods (kept for backward compat) ────────────────────

    async def get_user_context(self, user_id: UUID) -> Dict[str, Any]:
        """Get comprehensive user context for AI agents."""
        user = await self._get_user(user_id)
        if not user:
            return {"error": "User not found"}
        financial_snapshot = await self._get_financial_snapshot(user_id)
        active_budgets = await self._get_active_budgets(user_id)
        recent_patterns = await self._get_recent_patterns(user_id)
        active_goals = await self._get_active_goals(user_id)
        return {
            "success": True,
            "data": {
                "user_profile": {
                    "display_name": user.display_name or "User",
                    "preferred_currency": user.preferred_currency or "PKR",
                    "locale": user.preferred_locale or "en",
                    "member_since": user.created_at.strftime("%Y-%m-%d"),
                },
                "financial_snapshot": financial_snapshot,
                "active_budgets": active_budgets,
                "active_goals": active_goals,
                "recent_patterns": recent_patterns,
            },
            "meta": {"generated_at": datetime.utcnow().isoformat() + "Z", "valid_for_seconds": 300},
        }

    async def process_query(self, user_id, query, conversation_id=None):
        return await self.process_chat(user_id, query, conversation_id or UUID(int=0), "en")

    async def generate_insights(self, user_id, insight_types, force_refresh=False):
        from uuid import uuid4
        job_id = f"job_{uuid4().hex[:12]}"
        if force_refresh:
            await self._generate_budget_insights(user_id)
        return {"success": True, "data": {"job_id": job_id, "status": "completed", "insight_types": insight_types}}

    async def get_cached_insights(self, user_id, insight_type=None):
        return await self.get_insights(user_id, insight_type=insight_type)

    async def save_agent_memory(self, user_id, memory_type, content):
        memory = AgentMemory(user_id=user_id, memory_type=memory_type, content=str(content))
        self.session.add(memory)
        await self.session.flush()
        await self.session.refresh(memory)
        return {"success": True, "data": {"id": str(memory.id), "memory_type": memory.memory_type, "created_at": memory.created_at.isoformat() + "Z"}}

    async def _get_user(self, user_id):
        return (await self.session.execute(select(User).where(User.id == user_id))).scalar_one_or_none()

    async def _get_financial_snapshot(self, user_id):
        today = date.today()
        three_months_ago = today - timedelta(days=90)
        balance_stmt = select(func.coalesce(func.sum(Wallet.current_balance), 0)).where(Wallet.user_id == user_id, Wallet.is_active == True)
        balance = float((await self.session.execute(balance_stmt)).scalar_one())
        inc_stmt = select(func.coalesce(func.sum(Transaction.amount), 0)).where(Transaction.user_id == user_id, Transaction.type == TransactionType.income, Transaction.transaction_date >= three_months_ago, Transaction.is_deleted == False)
        total_inc = float((await self.session.execute(inc_stmt)).scalar_one())
        exp_stmt = select(func.coalesce(func.sum(Transaction.amount), 0)).where(Transaction.user_id == user_id, Transaction.type == TransactionType.expense, Transaction.transaction_date >= three_months_ago, Transaction.is_deleted == False)
        total_exp = float((await self.session.execute(exp_stmt)).scalar_one())
        mi, me = total_inc / 3, total_exp / 3
        sr = (mi - me) / mi * 100 if mi > 0 else 0
        return {"current_balance": balance, "monthly_income_avg": round(mi, 2), "monthly_expense_avg": round(me, 2), "savings_rate_avg": round(sr, 1)}

    async def _get_active_budgets(self, user_id):
        today = date.today()
        month_start = date(today.year, today.month, 1)
        stmt = select(Budget, Category.name, Category.emoji).join(Category, Budget.category_id == Category.id).where(Budget.user_id == user_id, Budget.month == today.month, Budget.year == today.year)
        rows = (await self.session.execute(stmt)).all()
        result = []
        for row in rows:
            b = row.Budget
            spent_stmt = select(func.coalesce(func.sum(Transaction.amount), 0)).where(Transaction.user_id == user_id, Transaction.category_id == b.category_id, Transaction.type == TransactionType.expense, Transaction.transaction_date >= month_start, Transaction.transaction_date <= today, Transaction.is_deleted == False)
            spent = float((await self.session.execute(spent_stmt)).scalar_one())
            pct = (spent / float(b.limit_amount) * 100) if b.limit_amount > 0 else 0
            status = "exceeded" if pct >= 100 else "warning" if pct >= 80 else "normal"
            result.append({"category": row.name, "emoji": row.emoji or "📦", "limit": float(b.limit_amount), "spent": spent, "status": status})
        return result

    async def _get_active_goals(self, user_id):
        stmt = select(Goal).where(Goal.user_id == user_id, Goal.status == GoalStatus.active).order_by(Goal.priority.desc()).limit(5)
        goals = (await self.session.execute(stmt)).scalars().all()
        return [{"name": g.name, "emoji": g.emoji, "target": float(g.target_amount), "current": float(g.current_amount), "percentage": round(float(g.current_amount) / float(g.target_amount) * 100, 1) if g.target_amount > 0 else 0} for g in goals]

    async def _get_recent_patterns(self, user_id):
        today = date.today()
        month_start = date(today.year, today.month, 1)
        prev_month_start = date(today.year, today.month - 1, 1) if today.month > 1 else date(today.year - 1, 12, 1)
        top_cat_stmt = select(Category.name, func.sum(Transaction.amount).label("total")).join(Transaction, Transaction.category_id == Category.id).where(Transaction.user_id == user_id, Transaction.type == TransactionType.expense, Transaction.transaction_date >= month_start, Transaction.is_deleted == False).group_by(Category.id, Category.name).order_by(func.sum(Transaction.amount).desc()).limit(1)
        top_cat = (await self.session.execute(top_cat_stmt)).first()
        curr_stmt = select(func.coalesce(func.sum(Transaction.amount), 0)).where(Transaction.user_id == user_id, Transaction.type == TransactionType.expense, Transaction.transaction_date >= month_start, Transaction.is_deleted == False)
        curr = float((await self.session.execute(curr_stmt)).scalar_one())
        prev_stmt = select(func.coalesce(func.sum(Transaction.amount), 0)).where(Transaction.user_id == user_id, Transaction.type == TransactionType.expense, Transaction.transaction_date >= prev_month_start, Transaction.transaction_date < month_start, Transaction.is_deleted == False)
        prev = float((await self.session.execute(prev_stmt)).scalar_one())
        change = (curr - prev) / prev * 100 if prev > 0 else 0
        trend = "increasing" if change > 10 else "decreasing" if change < -10 else "stable"
        return {"top_expense_category": top_cat.name if top_cat else None, "spending_trend": trend, "unusual_transactions": []}
