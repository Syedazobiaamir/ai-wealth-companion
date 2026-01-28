"""AI service for context and query operations (Phase III ready)."""

from datetime import date, datetime, timedelta
from decimal import Decimal
from typing import Any, Dict, List, Optional
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.budget import Budget
from src.models.category import Category
from src.models.goal import Goal, GoalStatus
from src.models.transaction import Transaction, TransactionType
from src.models.user import User
from src.models.wallet import Wallet
from src.models.insight_cache import InsightCache
from src.models.agent_memory import AgentMemory


class AIService:
    """Service for AI context and query operations."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_user_context(self, user_id: UUID) -> Dict[str, Any]:
        """Get comprehensive user context for AI agents."""
        # Get user profile
        user = await self._get_user(user_id)
        if not user:
            return {"error": "User not found"}

        # Get financial snapshot
        financial_snapshot = await self._get_financial_snapshot(user_id)

        # Get active budgets with status
        active_budgets = await self._get_active_budgets(user_id)

        # Get recent patterns
        recent_patterns = await self._get_recent_patterns(user_id)

        # Get active goals
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
            "meta": {
                "generated_at": datetime.utcnow().isoformat() + "Z",
                "valid_for_seconds": 300,
            },
        }

    async def process_query(
        self,
        user_id: UUID,
        query: str,
        conversation_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Process natural language query (Phase III stub)."""
        # This is a stub for Phase III AI integration
        # For now, return a placeholder response
        return {
            "success": True,
            "data": {
                "answer": f"AI processing is coming in Phase III. Your query: '{query}'",
                "answer_ur": None,
                "data_points": [],
                "suggested_actions": [
                    {
                        "action": "view_dashboard",
                        "label": "View Dashboard",
                        "params": {},
                    }
                ],
                "confidence": 0.0,
            },
            "meta": {
                "processing_time_ms": 0,
                "model_version": "stub_v1",
                "note": "AI processing will be available in Phase III",
            },
        }

    async def generate_insights(
        self,
        user_id: UUID,
        insight_types: List[str],
        force_refresh: bool = False,
    ) -> Dict[str, Any]:
        """Trigger insight generation (Phase III stub)."""
        from uuid import uuid4

        job_id = f"job_{uuid4().hex[:12]}"

        return {
            "success": True,
            "data": {
                "job_id": job_id,
                "status": "queued",
                "insight_types": insight_types,
                "estimated_completion": (
                    datetime.utcnow() + timedelta(minutes=1)
                ).isoformat() + "Z",
                "note": "AI insight generation will be available in Phase III",
            },
        }

    async def get_cached_insights(
        self,
        user_id: UUID,
        insight_type: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Get cached insights for a user."""
        statement = select(InsightCache).where(
            InsightCache.user_id == user_id,
            InsightCache.is_active == True,
        )
        if insight_type:
            statement = statement.where(InsightCache.insight_type == insight_type)
        statement = statement.order_by(InsightCache.created_at.desc()).limit(10)

        result = await self.session.execute(statement)
        insights = result.scalars().all()

        return [
            {
                "id": str(i.id),
                "type": i.insight_type,
                "content": i.content,
                "content_ur": i.content_ur,
                "confidence": i.confidence_score,
                "created_at": i.created_at.isoformat() + "Z",
            }
            for i in insights
        ]

    async def save_agent_memory(
        self,
        user_id: UUID,
        memory_type: str,
        content: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Save agent memory for context continuity."""
        memory = AgentMemory(
            user_id=user_id,
            memory_type=memory_type,
            content=content,
        )
        self.session.add(memory)
        await self.session.flush()
        await self.session.refresh(memory)

        return {
            "success": True,
            "data": {
                "id": str(memory.id),
                "memory_type": memory.memory_type,
                "created_at": memory.created_at.isoformat() + "Z",
            },
        }

    async def _get_user(self, user_id: UUID) -> Optional[User]:
        """Get user by ID."""
        statement = select(User).where(User.id == user_id)
        result = await self.session.execute(statement)
        return result.scalar_one_or_none()

    async def _get_financial_snapshot(self, user_id: UUID) -> Dict[str, Any]:
        """Get current financial snapshot."""
        today = date.today()
        month_start = date(today.year, today.month, 1)

        # Get current balance from wallets
        balance_stmt = select(func.coalesce(func.sum(Wallet.current_balance), 0)).where(
            Wallet.user_id == user_id,
            Wallet.is_active == True,
        )
        balance_result = await self.session.execute(balance_stmt)
        current_balance = float(balance_result.scalar_one())

        # Calculate averages from last 3 months
        three_months_ago = today - timedelta(days=90)

        income_stmt = select(func.coalesce(func.sum(Transaction.amount), 0)).where(
            Transaction.user_id == user_id,
            Transaction.type == TransactionType.income,
            Transaction.transaction_date >= three_months_ago,
            Transaction.is_deleted == False,
        )
        income_result = await self.session.execute(income_stmt)
        total_income = float(income_result.scalar_one())

        expense_stmt = select(func.coalesce(func.sum(Transaction.amount), 0)).where(
            Transaction.user_id == user_id,
            Transaction.type == TransactionType.expense,
            Transaction.transaction_date >= three_months_ago,
            Transaction.is_deleted == False,
        )
        expense_result = await self.session.execute(expense_stmt)
        total_expense = float(expense_result.scalar_one())

        monthly_income_avg = total_income / 3
        monthly_expense_avg = total_expense / 3
        savings_rate = (
            (monthly_income_avg - monthly_expense_avg) / monthly_income_avg * 100
            if monthly_income_avg > 0
            else 0
        )

        return {
            "current_balance": current_balance,
            "monthly_income_avg": round(monthly_income_avg, 2),
            "monthly_expense_avg": round(monthly_expense_avg, 2),
            "savings_rate_avg": round(savings_rate, 1),
        }

    async def _get_active_budgets(self, user_id: UUID) -> List[Dict[str, Any]]:
        """Get active budgets with spending status."""
        today = date.today()
        month_start = date(today.year, today.month, 1)

        # Get budgets with category info
        statement = (
            select(Budget, Category.name, Category.emoji)
            .join(Category, Budget.category_id == Category.id)
            .where(
                Budget.user_id == user_id,
                Budget.month == today.month,
                Budget.year == today.year,
            )
        )
        result = await self.session.execute(statement)
        budgets = result.all()

        budget_list = []
        for row in budgets:
            budget = row.Budget
            # Get spent amount for this category
            spent_stmt = select(func.coalesce(func.sum(Transaction.amount), 0)).where(
                Transaction.user_id == user_id,
                Transaction.category_id == budget.category_id,
                Transaction.type == TransactionType.expense,
                Transaction.transaction_date >= month_start,
                Transaction.transaction_date <= today,
                Transaction.is_deleted == False,
            )
            spent_result = await self.session.execute(spent_stmt)
            spent = float(spent_result.scalar_one())

            percentage = (spent / float(budget.limit_amount) * 100) if budget.limit_amount > 0 else 0

            if percentage >= 100:
                status = "exceeded"
            elif percentage >= 80:
                status = "warning"
            else:
                status = "normal"

            budget_list.append({
                "category": row.name,
                "emoji": row.emoji or "📦",
                "limit": float(budget.limit_amount),
                "spent": spent,
                "status": status,
            })

        return budget_list

    async def _get_active_goals(self, user_id: UUID) -> List[Dict[str, Any]]:
        """Get active goals."""
        statement = (
            select(Goal)
            .where(
                Goal.user_id == user_id,
                Goal.status == GoalStatus.active,
            )
            .order_by(Goal.priority.desc())
            .limit(5)
        )
        result = await self.session.execute(statement)
        goals = result.scalars().all()

        return [
            {
                "name": g.name,
                "emoji": g.emoji,
                "target": float(g.target_amount),
                "current": float(g.current_amount),
                "percentage": round(
                    float(g.current_amount) / float(g.target_amount) * 100, 1
                ) if g.target_amount > 0 else 0,
            }
            for g in goals
        ]

    async def _get_recent_patterns(self, user_id: UUID) -> Dict[str, Any]:
        """Analyze recent spending patterns."""
        today = date.today()
        month_start = date(today.year, today.month, 1)
        prev_month_start = date(today.year, today.month - 1, 1) if today.month > 1 else date(today.year - 1, 12, 1)

        # Get top expense category
        top_cat_stmt = (
            select(Category.name, func.sum(Transaction.amount).label("total"))
            .join(Transaction, Transaction.category_id == Category.id)
            .where(
                Transaction.user_id == user_id,
                Transaction.type == TransactionType.expense,
                Transaction.transaction_date >= month_start,
                Transaction.is_deleted == False,
            )
            .group_by(Category.id, Category.name)
            .order_by(func.sum(Transaction.amount).desc())
            .limit(1)
        )
        top_cat_result = await self.session.execute(top_cat_stmt)
        top_cat = top_cat_result.first()

        # Calculate spending trend
        curr_expense_stmt = select(func.coalesce(func.sum(Transaction.amount), 0)).where(
            Transaction.user_id == user_id,
            Transaction.type == TransactionType.expense,
            Transaction.transaction_date >= month_start,
            Transaction.is_deleted == False,
        )
        curr_result = await self.session.execute(curr_expense_stmt)
        curr_expense = float(curr_result.scalar_one())

        prev_expense_stmt = select(func.coalesce(func.sum(Transaction.amount), 0)).where(
            Transaction.user_id == user_id,
            Transaction.type == TransactionType.expense,
            Transaction.transaction_date >= prev_month_start,
            Transaction.transaction_date < month_start,
            Transaction.is_deleted == False,
        )
        prev_result = await self.session.execute(prev_expense_stmt)
        prev_expense = float(prev_result.scalar_one())

        if prev_expense > 0:
            change = (curr_expense - prev_expense) / prev_expense * 100
            if change > 10:
                trend = "increasing"
            elif change < -10:
                trend = "decreasing"
            else:
                trend = "stable"
        else:
            trend = "stable"

        return {
            "top_expense_category": top_cat.name if top_cat else None,
            "spending_trend": trend,
            "unusual_transactions": [],  # Phase III: ML-based anomaly detection
        }
