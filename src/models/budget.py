"""Budget models for spending limits and status tracking."""
from dataclasses import dataclass


@dataclass
class Budget:
    """
    Represents a spending limit for a category.

    Attributes:
        category: Linked category name (must reference existing Category)
        limit: Monthly spending limit (must be > 0)
    """
    category: str
    limit: float

    def __hash__(self):
        return hash(self.category)


@dataclass
class BudgetStatus:
    """
    Computed budget status for a category.

    Attributes:
        category: Category name
        limit: Budget limit amount
        spent: Total expense amount in category (current session)
        remaining: limit - spent (can be negative if exceeded)
        percentage: (spent / limit) * 100
        exceeded: True if spent > limit
    """
    category: str
    limit: float
    spent: float
    remaining: float
    percentage: float
    exceeded: bool
