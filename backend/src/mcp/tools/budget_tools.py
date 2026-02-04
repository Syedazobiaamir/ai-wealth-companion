"""MCP tool: create_budget — wraps BudgetService."""

from datetime import date
from typing import Any, Dict, Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.category import Category
from src.services.budget import BudgetService


async def create_budget(
    user_id: UUID,
    session: AsyncSession,
    category: str,
    amount: float,
    month: Optional[int] = None,
    year: Optional[int] = None,
) -> Dict[str, Any]:
    """Create a monthly budget for a category."""
    today = date.today()
    month = month or today.month
    year = year or today.year

    # Resolve category name to ID
    stmt = select(Category).where(Category.name.ilike(f"%{category}%"))
    result = await session.execute(stmt)
    cat = result.scalar_one_or_none()

    if not cat:
        return {"error": f"Category '{category}' not found. Available categories can be viewed via the dashboard."}

    service = BudgetService(session)
    budget = await service.create_budget(
        user_id=user_id,
        category_id=cat.id,
        limit_amount=amount,
        month=month,
        year=year,
    )

    return {
        "budget_id": str(budget.id),
        "category": cat.name,
        "limit": float(budget.limit_amount),
        "month": month,
        "year": year,
        "message": f"Budget created: {cat.name} — {amount:,.0f} for {month}/{year}",
    }
