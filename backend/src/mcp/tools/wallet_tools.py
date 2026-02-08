"""MCP tools: wallet management — wraps WalletService."""

from decimal import Decimal
from typing import Any, Dict, List, Optional
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from src.models.wallet import WalletCreate, WalletType
from src.services.wallet import WalletService


async def create_wallet(
    user_id: UUID,
    session: AsyncSession,
    name: str,
    wallet_type: str = "cash",
    initial_balance: float = 0.0,
    currency: str = "PKR",
    **kwargs,
) -> Dict[str, Any]:
    """Create a new wallet for the user.

    Args:
        user_id: The user's ID
        session: Database session
        name: Wallet name (e.g., "My Cash", "Bank Account")
        wallet_type: Type of wallet - cash, bank, credit, savings, investment
        initial_balance: Starting balance (default 0)
        currency: Currency code (default PKR)

    Returns:
        Dict with wallet details or error
    """
    # Validate wallet type
    valid_types = ["cash", "bank", "credit", "savings", "investment"]
    wallet_type_lower = wallet_type.lower()
    if wallet_type_lower not in valid_types:
        return {"error": f"Invalid wallet type '{wallet_type}'. Valid types: {', '.join(valid_types)}"}

    # Ensure initial_balance is a valid number
    try:
        balance_value = float(initial_balance) if initial_balance else 0.0
    except (TypeError, ValueError):
        balance_value = 0.0

    try:
        wallet_data = WalletCreate(
            name=name,
            type=WalletType(wallet_type_lower),
            currency=currency,
            initial_balance=Decimal(str(balance_value)),
        )

        service = WalletService(session)
        wallet = await service.create(user_id=user_id, wallet_data=wallet_data)

        return {
            "wallet_id": str(wallet.id),
            "name": wallet.name,
            "type": wallet.type.value,
            "balance": float(wallet.current_balance),
            "currency": wallet.currency,
            "is_default": wallet.is_default,
            "message": f"Wallet '{name}' created successfully! Balance: {currency} {balance_value:,.0f}",
        }
    except Exception as e:
        return {"error": f"Failed to create wallet: {str(e)}"}


async def list_wallets(
    user_id: UUID,
    session: AsyncSession,
    **kwargs,
) -> Dict[str, Any]:
    """List all wallets for the user.

    Args:
        user_id: The user's ID
        session: Database session

    Returns:
        Dict with list of wallets
    """
    try:
        service = WalletService(session)
        wallets = await service.get_all(user_id=user_id)

        if not wallets:
            return {
                "wallets": [],
                "total": 0,
                "message": "You don't have any wallets yet. Say 'create a cash wallet' to get started!",
            }

        wallet_list = []
        total_balance = 0.0
        for w in wallets:
            wallet_list.append({
                "id": str(w.id),
                "name": w.name,
                "type": w.type.value,
                "balance": float(w.current_balance),
                "currency": w.currency,
                "is_default": w.is_default,
            })
            total_balance += float(w.current_balance)

        default_wallet = next((w for w in wallet_list if w["is_default"]), None)
        default_name = default_wallet["name"] if default_wallet else "None"

        return {
            "wallets": wallet_list,
            "total": len(wallet_list),
            "total_balance": total_balance,
            "message": f"You have {len(wallet_list)} wallet(s). Total balance: PKR {total_balance:,.0f}. Default: {default_name}",
        }
    except Exception as e:
        return {"error": f"Failed to list wallets: {str(e)}"}


async def get_wallet_balance(
    user_id: UUID,
    session: AsyncSession,
    **kwargs,
) -> Dict[str, Any]:
    """Get total balance across all wallets.

    Args:
        user_id: The user's ID
        session: Database session

    Returns:
        Dict with total balance
    """
    try:
        service = WalletService(session)
        total = await service.get_total_balance(user_id)
        wallets = await service.get_all(user_id=user_id)

        if not wallets:
            return {
                "total_balance": 0,
                "wallet_count": 0,
                "message": "No wallets found. Create a wallet first!",
            }

        return {
            "total_balance": float(total),
            "wallet_count": len(wallets),
            "message": f"Total balance across {len(wallets)} wallet(s): PKR {total:,.0f}",
        }
    except Exception as e:
        return {"error": f"Failed to get balance: {str(e)}"}
