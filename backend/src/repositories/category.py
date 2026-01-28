"""Category repository for data access."""

from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.category import Category, CategoryBase
from src.repositories.base import BaseRepository


class CategoryRepository(BaseRepository[Category, CategoryBase, CategoryBase]):
    """Repository for category operations."""

    def __init__(self, session: AsyncSession):
        super().__init__(Category, session)

    async def get_by_name(self, name: str) -> Optional[Category]:
        """Get category by name."""
        statement = select(Category).where(Category.name == name)
        result = await self.session.execute(statement)
        return result.scalar_one_or_none()

    async def get_all_ordered(self) -> List[Category]:
        """Get all categories ordered by name."""
        statement = select(Category).order_by(Category.name)
        result = await self.session.execute(statement)
        return list(result.scalars().all())

    async def search(self, query: str) -> List[Category]:
        """Search categories by name."""
        statement = select(Category).where(
            Category.name.ilike(f"%{query}%")
        ).order_by(Category.name)
        result = await self.session.execute(statement)
        return list(result.scalars().all())
