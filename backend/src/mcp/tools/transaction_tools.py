"""MCP tool: add_transaction — wraps TransactionService."""

from datetime import date
from decimal import Decimal
from typing import Any, Dict, Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.category import Category
from src.models.wallet import Wallet
from src.models.transaction import TransactionCreate, TransactionType
from src.services.transaction import TransactionService


async def add_transaction(
    user_id: UUID,
    session: AsyncSession,
    type: str,
    amount: float,
    category: str,
    note: Optional[str] = None,
    date_str: Optional[str] = None,
    **kwargs,
) -> Dict[str, Any]:
    """Record a financial transaction."""
    # Resolve category
    stmt = select(Category).where(Category.name.ilike(f"%{category}%"))
    result = await session.execute(stmt)
    cat = result.scalar_one_or_none()
    if not cat:
        return {"error": f"Category '{category}' not found."}

    # Get default wallet
    wallet_stmt = select(Wallet).where(
        Wallet.user_id == user_id,
        Wallet.is_default == True,
        Wallet.is_active == True,
    )
    wallet_result = await session.execute(wallet_stmt)
    wallet = wallet_result.scalar_one_or_none()
    if not wallet:
        # Fallback: get any active wallet
        fallback_stmt = select(Wallet).where(
            Wallet.user_id == user_id, Wallet.is_active == True
        ).limit(1)
        wallet_result = await session.execute(fallback_stmt)
        wallet = wallet_result.scalar_one_or_none()
        if not wallet:
            return {"error": "No active wallet found. Create a wallet first."}

    txn_date = date.today()
    if date_str:
        try:
            txn_date = date.fromisoformat(date_str)
        except ValueError:
            pass

    # Create TransactionCreate object
    txn_type = TransactionType.income if type.lower() == "income" else TransactionType.expense
    txn_data = TransactionCreate(
        type=txn_type,
        amount=Decimal(str(amount)),
        category_id=cat.id,
        wallet_id=wallet.id,
        transaction_date=txn_date,
        note=note or "",
    )

    service = TransactionService(session)
    txn = await service.create(user_id=user_id, data=txn_data)

    return {
        "transaction_id": str(txn.id),
        "type": type,
        "amount": float(txn.amount),
        "category": cat.name,
        "wallet": wallet.name,
        "date": txn_date.isoformat(),
        "message": f"{type.capitalize()} recorded: {cat.name} — {amount:,.0f}",
    }
