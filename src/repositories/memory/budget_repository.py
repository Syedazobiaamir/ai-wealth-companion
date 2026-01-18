"""In-memory implementation of BudgetRepository."""
from typing import Dict, List, Optional

from src.models import Budget
from src.repositories.base import BudgetRepository


class InMemoryBudgetRepository(BudgetRepository):
    """In-memory storage for budgets using a dictionary keyed by category."""

    def __init__(self):
        self._budgets: Dict[str, Budget] = {}

    def set(self, budget: Budget) -> Budget:
        """
        Set or update budget for a category.

        Args:
            budget: Budget to set

        Returns:
            The set budget
        """
        key = budget.category.lower()
        self._budgets[key] = budget
        return budget

    def get_by_category(self, category: str) -> Optional[Budget]:
        """Get budget by category name (case-insensitive)."""
        return self._budgets.get(category.lower())

    def get_all(self) -> List[Budget]:
        """Get all budgets."""
        return list(self._budgets.values())

    def clear(self) -> None:
        """Clear all budgets (for testing)."""
        self._budgets.clear()
