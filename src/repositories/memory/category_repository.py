"""In-memory implementation of CategoryRepository."""
from typing import Dict, List, Optional

from src.models import Category
from src.repositories.base import CategoryRepository


class InMemoryCategoryRepository(CategoryRepository):
    """In-memory storage for categories using a dictionary."""

    def __init__(self):
        self._categories: Dict[str, Category] = {}

    def create(self, category: Category) -> Category:
        """
        Create a new category.

        Args:
            category: Category to create

        Returns:
            The created category

        Raises:
            ValueError: If category name already exists (case-insensitive)
        """
        key = category.name.lower()
        if key in self._categories:
            raise ValueError(f"Category '{category.name}' already exists")
        self._categories[key] = category
        return category

    def get_by_name(self, name: str) -> Optional[Category]:
        """Get category by name (case-insensitive)."""
        return self._categories.get(name.lower())

    def get_all(self) -> List[Category]:
        """Get all categories."""
        return list(self._categories.values())

    def exists(self, name: str) -> bool:
        """Check if category exists (case-insensitive)."""
        return name.lower() in self._categories

    def clear(self) -> None:
        """Clear all categories (for testing)."""
        self._categories.clear()
