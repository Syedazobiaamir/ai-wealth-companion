"""Abstract repository interfaces for data access."""
from abc import ABC, abstractmethod
from typing import List, Optional
from datetime import date

from src.models import Transaction, Category, Budget


class TransactionRepository(ABC):
    """Interface for transaction data access."""

    @abstractmethod
    def create(self, transaction: Transaction) -> Transaction:
        """Create a new transaction. Returns transaction with generated ID."""
        pass

    @abstractmethod
    def get_by_id(self, id: int) -> Optional[Transaction]:
        """Get transaction by ID. Returns None if not found."""
        pass

    @abstractmethod
    def get_all(self) -> List[Transaction]:
        """Get all transactions."""
        pass

    @abstractmethod
    def update(self, id: int, updates: dict) -> Optional[Transaction]:
        """Update transaction fields. Returns updated transaction or None if not found."""
        pass

    @abstractmethod
    def delete(self, id: int) -> bool:
        """Delete transaction by ID. Returns True if deleted, False if not found."""
        pass

    @abstractmethod
    def filter_by_category(self, category: str) -> List[Transaction]:
        """Get transactions filtered by category name."""
        pass

    @abstractmethod
    def filter_by_date_range(self, start: date, end: date) -> List[Transaction]:
        """Get transactions within date range (inclusive)."""
        pass

    @abstractmethod
    def sort_by_amount(self, ascending: bool = True) -> List[Transaction]:
        """Get all transactions sorted by amount."""
        pass

    @abstractmethod
    def get_next_id(self) -> int:
        """Get the next available transaction ID."""
        pass


class CategoryRepository(ABC):
    """Interface for category data access."""

    @abstractmethod
    def create(self, category: Category) -> Category:
        """Create a new category. Raises error if name exists."""
        pass

    @abstractmethod
    def get_by_name(self, name: str) -> Optional[Category]:
        """Get category by name. Returns None if not found."""
        pass

    @abstractmethod
    def get_all(self) -> List[Category]:
        """Get all categories."""
        pass

    @abstractmethod
    def exists(self, name: str) -> bool:
        """Check if category exists (case-insensitive)."""
        pass


class BudgetRepository(ABC):
    """Interface for budget data access."""

    @abstractmethod
    def set(self, budget: Budget) -> Budget:
        """Set or update budget for a category."""
        pass

    @abstractmethod
    def get_by_category(self, category: str) -> Optional[Budget]:
        """Get budget by category name. Returns None if not set."""
        pass

    @abstractmethod
    def get_all(self) -> List[Budget]:
        """Get all budgets."""
        pass
