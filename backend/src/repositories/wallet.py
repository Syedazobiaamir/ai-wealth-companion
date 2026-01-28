"""Wallet repository for database operations."""

from typing import List, Optional
from uuid import UUID

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.wallet import Wallet, WalletCreate, WalletUpdate
from src.repositories.base import BaseRepository


class WalletRepository(BaseRepository[Wallet, WalletCreate, WalletUpdate]):
    """Repository for wallet database operations."""

    def __init__(self, session: AsyncSession):
        super().__init__(Wallet, session)

    async def get_by_user(
        self,
        user_id: UUID,
        skip: int = 0,
        limit: int = 100,
        include_inactive: bool = False,
    ) -> List[Wallet]:
        """Get all wallets for a user."""
        statement = select(Wallet).where(Wallet.user_id == user_id)
        if not include_inactive:
            statement = statement.where(Wallet.is_active == True)
        statement = statement.offset(skip).limit(limit)
        result = await self.session.execute(statement)
        return list(result.scalars().all())

    async def get_by_id_and_user(
        self,
        wallet_id: UUID,
        user_id: UUID,
    ) -> Optional[Wallet]:
        """Get a wallet by ID for a specific user."""
        statement = select(Wallet).where(
            Wallet.id == wallet_id,
            Wallet.user_id == user_id,
        )
        result = await self.session.execute(statement)
        return result.scalar_one_or_none()

    async def get_default(self, user_id: UUID) -> Optional[Wallet]:
        """Get the default wallet for a user."""
        statement = select(Wallet).where(
            Wallet.user_id == user_id,
            Wallet.is_default == True,
            Wallet.is_active == True,
        )
        result = await self.session.execute(statement)
        return result.scalar_one_or_none()

    async def create_with_user(
        self,
        user_id: UUID,
        wallet_data: WalletCreate,
        is_default: bool = False,
    ) -> Wallet:
        """Create a wallet for a user."""
        wallet = Wallet(
            user_id=user_id,
            name=wallet_data.name,
            type=wallet_data.type,
            currency=wallet_data.currency,
            initial_balance=wallet_data.initial_balance,
            current_balance=wallet_data.initial_balance,
            color=wallet_data.color,
            icon=wallet_data.icon,
            is_default=is_default,
        )
        self.session.add(wallet)
        await self.session.flush()
        await self.session.refresh(wallet)
        return wallet

    async def clear_default(self, user_id: UUID) -> None:
        """Clear default status for all user wallets."""
        statement = (
            update(Wallet)
            .where(Wallet.user_id == user_id, Wallet.is_default == True)
            .values(is_default=False)
        )
        await self.session.execute(statement)
        await self.session.flush()

    async def set_default(
        self,
        wallet_id: UUID,
        user_id: UUID,
    ) -> Optional[Wallet]:
        """Set a wallet as default."""
        await self.clear_default(user_id)
        statement = (
            update(Wallet)
            .where(Wallet.id == wallet_id, Wallet.user_id == user_id)
            .values(is_default=True)
        )
        await self.session.execute(statement)
        await self.session.flush()
        return await self.get_by_id_and_user(wallet_id, user_id)

    async def update_balance(
        self,
        wallet_id: UUID,
        amount_change: float,
    ) -> Optional[Wallet]:
        """Update wallet balance by a delta amount."""
        wallet = await self.get(wallet_id)
        if not wallet:
            return None
        wallet.current_balance = wallet.current_balance + amount_change
        self.session.add(wallet)
        await self.session.flush()
        await self.session.refresh(wallet)
        return wallet

    async def get_total_balance(self, user_id: UUID) -> float:
        """Get total balance across all active wallets."""
        from sqlalchemy import func

        statement = select(func.sum(Wallet.current_balance)).where(
            Wallet.user_id == user_id,
            Wallet.is_active == True,
        )
        result = await self.session.execute(statement)
        total = result.scalar_one_or_none()
        return float(total) if total else 0.0

    async def count_by_user(self, user_id: UUID) -> int:
        """Count active wallets for a user."""
        from sqlalchemy import func

        statement = select(func.count()).select_from(Wallet).where(
            Wallet.user_id == user_id,
            Wallet.is_active == True,
        )
        result = await self.session.execute(statement)
        return result.scalar_one()
