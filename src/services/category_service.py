"""Category service for managing categories."""
from typing import List, Optional

from src.models import Category
from src.repositories.base import CategoryRepository


# Default categories with emojis per constitution
DEFAULT_CATEGORIES = [
    Category(name="Food", emoji="🍔"),
    Category(name="Rent", emoji="🏠"),
    Category(name="Utilities", emoji="💡"),
    Category(name="Salary", emoji="💵"),
    Category(name="Investment", emoji="💎"),
]


class CategoryService:
    """Business logic for category operations."""

    def __init__(self, category_repo: CategoryRepository):
        self._repo = category_repo

    def load_default_categories(self) -> List[Category]:
        """
        Load default categories into the repository.

        Returns:
            List of created categories
        """
        created = []
        for cat in DEFAULT_CATEGORIES:
            if not self._repo.exists(cat.name):
                self._repo.create(cat)
                created.append(cat)
        return created

    def get_all_categories(self) -> List[Category]:
        """Get all categories."""
        return self._repo.get_all()

    def get_category(self, name: str) -> Optional[Category]:
        """Get category by name."""
        return self._repo.get_by_name(name)

    def category_exists(self, name: str) -> bool:
        """Check if category exists."""
        return self._repo.exists(name)
