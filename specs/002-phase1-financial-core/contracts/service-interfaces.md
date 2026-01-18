# Service Interfaces: Phase I Financial Core

**Feature**: 002-phase1-financial-core
**Date**: 2026-01-18

## Overview

This document defines the internal service interfaces for Phase I. Since Phase I is CLI-only with no external API, these are Python method signatures that define the contract between layers.

## Repository Interfaces

### TransactionRepository

```python
from abc import ABC, abstractmethod
from typing import List, Optional
from datetime import date

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
```

### CategoryRepository

```python
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
        """Check if category exists."""
        pass
```

### BudgetRepository

```python
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
```

## Service Interfaces

### TransactionService

```python
class TransactionService:
    """Business logic for transaction operations."""

    def add_transaction(
        self,
        type: str,          # "income" or "expense"
        amount: float,       # Must be > 0
        category: str,       # Must exist
        note: str = "",      # Optional
        date: str = None,    # YYYY-MM-DD, defaults to today
        recurring: bool = False
    ) -> Result[Transaction, str]:
        """
        Add a new transaction.

        Returns:
            Success: Transaction object with generated ID
            Failure: Error message string

        Validation:
            - Amount > 0
            - Category must exist
            - Date must be valid YYYY-MM-DD
            - Type must be "income" or "expense"
        """
        pass

    def update_transaction(
        self,
        id: int,
        **updates  # Any combination of: type, amount, category, note, date, recurring
    ) -> Result[Transaction, str]:
        """
        Update an existing transaction.

        Returns:
            Success: Updated Transaction object
            Failure: Error message (not found, validation error)
        """
        pass

    def delete_transaction(self, id: int) -> Result[bool, str]:
        """
        Delete a transaction by ID.

        Returns:
            Success: True
            Failure: Error message (not found)
        """
        pass

    def list_transactions(self) -> List[Transaction]:
        """Get all transactions."""
        pass

    def filter_by_category(self, category: str) -> List[Transaction]:
        """Get transactions filtered by category."""
        pass

    def filter_by_date(self, start: str, end: str) -> Result[List[Transaction], str]:
        """
        Get transactions within date range.

        Args:
            start: YYYY-MM-DD
            end: YYYY-MM-DD

        Returns:
            Success: Filtered list
            Failure: Error message (invalid date format)
        """
        pass

    def sort_by_amount(self, descending: bool = False) -> List[Transaction]:
        """Get transactions sorted by amount."""
        pass
```

### BudgetService

```python
class BudgetService:
    """Business logic for budget operations."""

    def set_budget(self, category: str, limit: float) -> Result[Budget, str]:
        """
        Set monthly budget for a category.

        Returns:
            Success: Budget object
            Failure: Error message (category not found, invalid limit)

        Validation:
            - Category must exist
            - Limit must be > 0
        """
        pass

    def get_budget_status(self, category: str) -> Result[BudgetStatus, str]:
        """
        Get budget status for a category.

        Returns:
            Success: BudgetStatus with spent, remaining, percentage, exceeded
            Failure: Error message (category not found, no budget set)
        """
        pass

    def get_all_budgets_status(self) -> List[BudgetStatus]:
        """Get status for all budgets."""
        pass
```

## Data Transfer Objects

### BudgetStatus

```python
@dataclass
class BudgetStatus:
    category: str
    limit: float
    spent: float
    remaining: float
    percentage: float  # 0-100+
    exceeded: bool
```

### Result Type

```python
from typing import TypeVar, Generic, Union

T = TypeVar('T')
E = TypeVar('E')

class Result(Generic[T, E]):
    """Simple result type for success/failure handling."""

    @staticmethod
    def ok(value: T) -> 'Result[T, E]': ...

    @staticmethod
    def err(error: E) -> 'Result[T, E]': ...

    def is_ok(self) -> bool: ...
    def is_err(self) -> bool: ...
    def unwrap(self) -> T: ...  # Raises if error
    def unwrap_err(self) -> E: ...  # Raises if ok
```

## Error Codes

| Code | Description |
|------|-------------|
| `VALIDATION_ERROR` | Input validation failed |
| `NOT_FOUND` | Entity not found |
| `DUPLICATE` | Entity already exists |
| `INVALID_DATE` | Date format invalid |
| `INVALID_AMOUNT` | Amount <= 0 |
| `INVALID_TYPE` | Transaction type not income/expense |
| `CATEGORY_NOT_FOUND` | Referenced category does not exist |
| `BUDGET_NOT_SET` | No budget set for category |
