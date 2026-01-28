"""Wallet API endpoints."""

from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.deps import CurrentUser, get_db
from src.models.wallet import WalletCreate, WalletRead, WalletUpdate
from src.services.wallet import WalletService

router = APIRouter()


@router.get(
    "",
    response_model=List[WalletRead],
    summary="List wallets",
    description="Get all wallets for the current user.",
)
async def list_wallets(
    current_user: CurrentUser,
    include_inactive: bool = Query(False, description="Include inactive wallets"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    session: AsyncSession = Depends(get_db),
) -> List[WalletRead]:
    """Get all wallets for the authenticated user."""
    service = WalletService(session)
    wallets = await service.get_all(
        user_id=current_user.id,
        skip=skip,
        limit=limit,
        include_inactive=include_inactive,
    )
    return [WalletRead.model_validate(w) for w in wallets]


@router.get(
    "/default",
    response_model=WalletRead,
    summary="Get default wallet",
    description="Get the user's default wallet.",
)
async def get_default_wallet(
    current_user: CurrentUser,
    session: AsyncSession = Depends(get_db),
) -> WalletRead:
    """Get the default wallet for the user."""
    service = WalletService(session)
    wallet = await service.get_default(current_user.id)
    if not wallet:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No default wallet found. Create a wallet first.",
        )
    return WalletRead.model_validate(wallet)


@router.get(
    "/balance",
    response_model=dict,
    summary="Get total balance",
    description="Get the total balance across all active wallets.",
)
async def get_total_balance(
    current_user: CurrentUser,
    session: AsyncSession = Depends(get_db),
) -> dict:
    """Get total balance across all wallets."""
    service = WalletService(session)
    total = await service.get_total_balance(current_user.id)
    return {
        "total_balance": total,
        "currency": current_user.preferred_currency or "PKR",
    }


@router.get(
    "/{wallet_id}",
    response_model=WalletRead,
    summary="Get wallet by ID",
    description="Get a specific wallet by its UUID.",
)
async def get_wallet(
    wallet_id: UUID,
    current_user: CurrentUser,
    session: AsyncSession = Depends(get_db),
) -> WalletRead:
    """Get a wallet by ID."""
    service = WalletService(session)
    wallet = await service.get_by_id(wallet_id, current_user.id)
    if not wallet:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Wallet with ID {wallet_id} not found",
        )
    return WalletRead.model_validate(wallet)


@router.post(
    "",
    response_model=WalletRead,
    status_code=status.HTTP_201_CREATED,
    summary="Create wallet",
    description="Create a new wallet for the current user.",
)
async def create_wallet(
    wallet_data: WalletCreate,
    current_user: CurrentUser,
    session: AsyncSession = Depends(get_db),
) -> WalletRead:
    """Create a new wallet."""
    service = WalletService(session)
    wallet = await service.create(current_user.id, wallet_data)
    return WalletRead.model_validate(wallet)


@router.put(
    "/{wallet_id}",
    response_model=WalletRead,
    summary="Update wallet",
    description="Update an existing wallet.",
)
async def update_wallet(
    wallet_id: UUID,
    wallet_data: WalletUpdate,
    current_user: CurrentUser,
    session: AsyncSession = Depends(get_db),
) -> WalletRead:
    """Update a wallet."""
    service = WalletService(session)
    wallet = await service.update(wallet_id, current_user.id, wallet_data)
    if not wallet:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Wallet with ID {wallet_id} not found",
        )
    return WalletRead.model_validate(wallet)


@router.delete(
    "/{wallet_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete wallet",
    description="Soft delete a wallet (deactivate).",
)
async def delete_wallet(
    wallet_id: UUID,
    current_user: CurrentUser,
    session: AsyncSession = Depends(get_db),
) -> None:
    """Soft delete a wallet."""
    service = WalletService(session)
    deleted = await service.delete(wallet_id, current_user.id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Wallet with ID {wallet_id} not found",
        )


@router.post(
    "/{wallet_id}/set-default",
    response_model=WalletRead,
    summary="Set as default wallet",
    description="Set a wallet as the default wallet.",
)
async def set_default_wallet(
    wallet_id: UUID,
    current_user: CurrentUser,
    session: AsyncSession = Depends(get_db),
) -> WalletRead:
    """Set a wallet as default."""
    service = WalletService(session)
    wallet = await service.set_default(wallet_id, current_user.id)
    if not wallet:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Wallet with ID {wallet_id} not found",
        )
    return WalletRead.model_validate(wallet)
