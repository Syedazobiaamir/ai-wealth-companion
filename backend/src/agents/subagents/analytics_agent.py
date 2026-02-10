"""
Phase V: Analytics Agent for Event-Driven Processing
AI Wealth Companion Cloud-Native System

This agent processes financial events and generates AI-powered insights
by subscribing to transaction and budget events via Dapr pub/sub.
"""

import logging
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Any, Dict, List, Optional
from uuid import UUID

from src.events import (
    EventHandler,
    TransactionCreatedEvent,
    TransactionUpdatedEvent,
    BudgetExceededEvent,
    AIInsightGeneratedEvent,
    EventType,
    event_handler,
    publish_event,
)

logger = logging.getLogger(__name__)


class AnalyticsAgent(EventHandler):
    """
    Analytics agent that processes financial events and generates insights.

    Subscribes to:
    - transactions: Analyzes spending patterns, detects anomalies
    - budget-alerts: Processes budget threshold warnings

    Publishes to:
    - ai-insights: Generated insights and recommendations
    - budget-alerts: Budget exceeded warnings
    """

    event_type = EventType.TRANSACTION_CREATED
    use_idempotency = True
    processing_timeout = 30.0

    # Configuration
    SPENDING_ANALYSIS_WINDOW_DAYS = 30
    BUDGET_WARNING_THRESHOLD = 0.80  # 80%
    BUDGET_CRITICAL_THRESHOLD = 0.95  # 95%
    ANOMALY_DEVIATION_THRESHOLD = 2.0  # Standard deviations

    def __init__(self):
        super().__init__()
        # In-memory cache for quick lookups (production would use Redis)
        self._spending_cache: Dict[str, Dict[str, Decimal]] = {}
        self._budget_cache: Dict[str, Dict[str, Any]] = {}

    async def handle(self, event: TransactionCreatedEvent) -> None:
        """
        Handle a transaction.created event.

        Performs:
        1. Spending pattern analysis
        2. Budget threshold checking
        3. Anomaly detection
        4. Insight generation
        """
        logger.info(f"Analytics agent processing event {event.id}")

        user_id = event.data.user_id
        transaction_data = event.data

        # Update spending cache
        await self._update_spending_cache(user_id, transaction_data)

        # Check budget thresholds
        await self._check_budget_thresholds(user_id, transaction_data)

        # Detect spending anomalies
        await self._detect_anomalies(user_id, transaction_data)

        # Generate periodic insights (daily summary)
        await self._generate_periodic_insights(user_id)

    async def _update_spending_cache(
        self,
        user_id: UUID,
        transaction: Any,
    ) -> None:
        """Update the spending cache with new transaction data."""
        user_key = str(user_id)
        category_key = str(transaction.category_id) if transaction.category_id else "uncategorized"

        if user_key not in self._spending_cache:
            self._spending_cache[user_key] = {}

        if category_key not in self._spending_cache[user_key]:
            self._spending_cache[user_key][category_key] = Decimal("0")

        if transaction.transaction_type == "expense":
            self._spending_cache[user_key][category_key] += transaction.amount

        logger.debug(
            f"Updated spending cache for user {user_id}, "
            f"category {category_key}: {self._spending_cache[user_key][category_key]}"
        )

    async def _check_budget_thresholds(
        self,
        user_id: UUID,
        transaction: Any,
    ) -> None:
        """
        Check if the transaction causes budget threshold breach.

        Publishes budget.exceeded or budget.warning events as needed.
        """
        if transaction.transaction_type != "expense":
            return

        category_id = transaction.category_id
        if not category_id:
            return

        # Get budget for this category (in production, query from database)
        budget = await self._get_budget_for_category(user_id, category_id)
        if not budget:
            return

        # Calculate current spending
        spent = await self._get_category_spending(user_id, category_id)
        percentage_used = float(spent / budget["amount"] * 100) if budget["amount"] > 0 else 0

        # Determine severity and publish event if threshold exceeded
        if percentage_used >= 100:
            await self._publish_budget_exceeded(
                user_id, budget, spent, percentage_used, "exceeded"
            )
        elif percentage_used >= self.BUDGET_CRITICAL_THRESHOLD * 100:
            await self._publish_budget_exceeded(
                user_id, budget, spent, percentage_used, "critical"
            )
        elif percentage_used >= self.BUDGET_WARNING_THRESHOLD * 100:
            await self._publish_budget_exceeded(
                user_id, budget, spent, percentage_used, "warning"
            )

    async def _get_budget_for_category(
        self,
        user_id: UUID,
        category_id: UUID,
    ) -> Optional[Dict[str, Any]]:
        """Get budget for a specific category (mock implementation)."""
        # In production, this would query the database
        user_key = str(user_id)
        category_key = str(category_id)

        if user_key in self._budget_cache:
            return self._budget_cache[user_key].get(category_key)

        return None

    async def _get_category_spending(
        self,
        user_id: UUID,
        category_id: UUID,
    ) -> Decimal:
        """Get current spending for a category."""
        user_key = str(user_id)
        category_key = str(category_id)

        if user_key in self._spending_cache:
            return self._spending_cache[user_key].get(category_key, Decimal("0"))

        return Decimal("0")

    async def _publish_budget_exceeded(
        self,
        user_id: UUID,
        budget: Dict[str, Any],
        spent: Decimal,
        percentage_used: float,
        severity: str,
    ) -> None:
        """Publish a budget exceeded/warning event."""
        try:
            from src.events import BudgetExceededEvent, BudgetExceededData

            event = BudgetExceededEvent(
                subject=str(user_id),
                severity=severity,
                data=BudgetExceededData(
                    budget_id=budget["id"],
                    user_id=user_id,
                    category_id=budget.get("category_id"),
                    category_name=budget.get("category_name"),
                    budget_amount=budget["amount"],
                    spent_amount=spent,
                    exceeded_by=spent - budget["amount"] if spent > budget["amount"] else Decimal("0"),
                    percentage_used=percentage_used,
                    period_start=budget.get("start_date", datetime.utcnow()),
                    period_end=budget.get("end_date", datetime.utcnow() + timedelta(days=30)),
                ),
            )

            await publish_event(event, "budget-alerts")
            logger.info(f"Published budget.{severity} event for user {user_id}")

        except Exception as e:
            logger.error(f"Failed to publish budget event: {e}")

    async def _detect_anomalies(
        self,
        user_id: UUID,
        transaction: Any,
    ) -> None:
        """
        Detect spending anomalies using statistical analysis.

        Publishes AI insight events for unusual transactions.
        """
        if transaction.transaction_type != "expense":
            return

        # Get historical average for this category
        category_id = transaction.category_id
        avg_amount = await self._get_category_average(user_id, category_id)

        if avg_amount and avg_amount > 0:
            deviation = float(transaction.amount) / float(avg_amount)

            if deviation > self.ANOMALY_DEVIATION_THRESHOLD:
                await self._publish_anomaly_insight(
                    user_id, transaction, deviation, avg_amount
                )

    async def _get_category_average(
        self,
        user_id: UUID,
        category_id: Optional[UUID],
    ) -> Optional[Decimal]:
        """Get average transaction amount for a category (mock)."""
        # In production, this would calculate from historical data
        return Decimal("50.00")  # Mock average

    async def _publish_anomaly_insight(
        self,
        user_id: UUID,
        transaction: Any,
        deviation: float,
        avg_amount: Decimal,
    ) -> None:
        """Publish an anomaly detection insight."""
        try:
            insight = AIInsightGeneratedEvent.create_spending_pattern_insight(
                user_id=user_id,
                title="Unusual Transaction Detected",
                content=(
                    f"Your recent transaction of ${transaction.amount:.2f} "
                    f"is {deviation:.1f}x higher than your average of ${avg_amount:.2f} "
                    f"in this category."
                ),
                recommendations=[
                    "Review if this was an intentional purchase",
                    "Consider if this affects your monthly budget",
                    "Check for subscription renewals or unexpected charges",
                ],
                confidence=0.85,
            )

            await publish_event(insight, "ai-insights")
            logger.info(f"Published anomaly insight for user {user_id}")

        except Exception as e:
            logger.error(f"Failed to publish anomaly insight: {e}")

    async def _generate_periodic_insights(self, user_id: UUID) -> None:
        """Generate periodic spending insights (called opportunistically)."""
        # This would typically be triggered by a scheduled job
        # For now, we skip frequent insight generation
        pass

    def set_budget(
        self,
        user_id: UUID,
        category_id: UUID,
        amount: Decimal,
        category_name: str = None,
    ) -> None:
        """Set a budget for testing/initialization purposes."""
        from uuid import uuid4

        user_key = str(user_id)
        category_key = str(category_id)

        if user_key not in self._budget_cache:
            self._budget_cache[user_key] = {}

        self._budget_cache[user_key][category_key] = {
            "id": uuid4(),
            "category_id": category_id,
            "category_name": category_name or "Category",
            "amount": amount,
            "start_date": datetime.utcnow(),
            "end_date": datetime.utcnow() + timedelta(days=30),
        }


# Register the analytics agent as event handler
@event_handler("transactions", TransactionCreatedEvent)
async def handle_transaction_created(event: TransactionCreatedEvent) -> None:
    """Handle transaction.created events."""
    agent = AnalyticsAgent()
    await agent.handle(event)


@event_handler("transactions", TransactionUpdatedEvent)
async def handle_transaction_updated(event: TransactionUpdatedEvent) -> None:
    """Handle transaction.updated events."""
    agent = AnalyticsAgent()
    # Reuse the same handler logic for updates
    await agent.handle(event)
