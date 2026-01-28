"""Wallet service for business logic."""

from datetime import datetime
from typing import List, Optional
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from src.models.wallet import Wallet, WalletCreate, WalletUpdate
from src.repositories.wallet import WalletRepository


class WalletService:
    """Service for wallet operations."""

    def __init__(self, session: AsyncSession):
        self.repo = WalletRepository(session)

    async def get_all(
        self,
        user_id: UUID,
        skip: int = 0,
        limit: int = 100,
        include_inactive: bool = False,
    ) -> List[Wallet]:
        """Get all wallets for a user."""
        return await self.repo.get_by_user(
            user_id, skip, limit, include_inactive
        )

    async def get_by_id(
        self,
        wallet_id: UUID,
        user_id: UUID,
    ) -> Optional[Wallet]:
        """Get a wallet by ID for a user."""
        return await self.repo.get_by_id_and_user(wallet_id, user_id)

    async def get_default(self, user_id: UUID) -> Optional[Wallet]:
        """Get user's default wallet."""
        return await self.repo.get_default(user_id)

    async def create(
        self,
        user_id: UUID,
        wallet_data: WalletCreate,
    ) -> Wallet:
        """Create a new wallet."""
        # Check if this is the user's first wallet
        wallet_count = await self.repo.count_by_user(user_id)
        is_default = wallet_count == 0

        return await self.repo.create_with_user(
            user_id, wallet_data, is_default
        )

    async def update(
        self,
        wallet_id: UUID,
        user_id: UUID,
        wallet_data: WalletUpdate,
    ) -> Optional[Wallet]:
        """Update a wallet."""
        wallet = await self.repo.get_by_id_and_user(wallet_id, user_id)
        if not wallet:
            return None

        update_data = wallet_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(wallet, field, value)
        wallet.updated_at = datetime.utcnow()

        # If setting as default, clear other defaults
        if wallet_data.is_default:
            await self.repo.clear_default(user_id)
            wallet.is_default = True

        return await self.repo.update(wallet_id, wallet_data)

    async def delete(
        self,
        wallet_id: UUID,
        user_id: UUID,
    ) -> bool:
        """Soft delete a wallet (deactivate)."""
        wallet = await self.repo.get_by_id_and_user(wallet_id, user_id)
        if not wallet:
            return False

        wallet.is_active = False
        wallet.updated_at = datetime.utcnow()
        return True

    async def set_default(
        self,
        wallet_id: UUID,
        user_id: UUID,
    ) -> Optional[Wallet]:
        """Set a wallet as the default."""
        wallet = await self.repo.get_by_id_and_user(wallet_id, user_id)
        if not wallet:
            return None

        return await self.repo.set_default(wallet_id, user_id)

    async def get_total_balance(self, user_id: UUID) -> float:
        """Get total balance across all wallets."""
        return await self.repo.get_total_balance(user_id)

    async def update_balance(
        self,
        wallet_id: UUID,
        amount_change: float,
    ) -> Optional[Wallet]:
        """Update wallet balance."""
        return await self.repo.update_balance(wallet_id, amount_change)
