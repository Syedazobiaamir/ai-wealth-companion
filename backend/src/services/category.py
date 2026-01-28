"""Category service for business logic."""

from typing import List, Optional
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from src.models.category import Category, CategoryRead
from src.repositories.category import CategoryRepository


class CategoryService:
    """Service for category operations."""

    def __init__(self, session: AsyncSession):
        self.repository = CategoryRepository(session)

    async def get_all(self) -> List[CategoryRead]:
        """Get all categories ordered by name."""
        categories = await self.repository.get_all_ordered()
        return [CategoryRead.model_validate(c) for c in categories]

    async def get_by_id(self, category_id: UUID) -> Optional[CategoryRead]:
        """Get a category by ID."""
        category = await self.repository.get(category_id)
        if not category:
            return None
        return CategoryRead.model_validate(category)

    async def get_by_name(self, name: str) -> Optional[CategoryRead]:
        """Get a category by name."""
        category = await self.repository.get_by_name(name)
        if not category:
            return None
        return CategoryRead.model_validate(category)

    async def search(self, query: str) -> List[CategoryRead]:
        """Search categories by name."""
        categories = await self.repository.search(query)
        return [CategoryRead.model_validate(c) for c in categories]

    async def exists(self, category_id: UUID) -> bool:
        """Check if a category exists."""
        category = await self.repository.get(category_id)
        return category is not None
