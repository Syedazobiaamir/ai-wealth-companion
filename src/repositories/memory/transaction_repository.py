"""In-memory implementation of TransactionRepository."""
from typing import Dict, List, Optional
from datetime import date
from dataclasses import replace

from src.models import Transaction
from src.repositories.base import TransactionRepository


class InMemoryTransactionRepository(TransactionRepository):
    """In-memory storage for transactions using a dictionary."""

    def __init__(self):
        self._transactions: Dict[int, Transaction] = {}
        self._next_id: int = 1

    def create(self, transaction: Transaction) -> Transaction:
        """
        Create a new transaction with auto-generated ID.

        Args:
            transaction: Transaction to create (ID will be assigned)

        Returns:
            The created transaction with assigned ID
        """
        txn = replace(transaction, id=self._next_id)
        self._transactions[txn.id] = txn
        self._next_id += 1
        return txn

    def get_by_id(self, id: int) -> Optional[Transaction]:
        """Get transaction by ID."""
        return self._transactions.get(id)

    def get_all(self) -> List[Transaction]:
        """Get all transactions."""
        return list(self._transactions.values())

    def update(self, id: int, updates: dict) -> Optional[Transaction]:
        """
        Update transaction fields.

        Args:
            id: Transaction ID
            updates: Dictionary of field names to new values

        Returns:
            Updated transaction or None if not found
        """
        txn = self._transactions.get(id)
        if txn is None:
            return None

        updated = replace(txn, **updates)
        self._transactions[id] = updated
        return updated

    def delete(self, id: int) -> bool:
        """Delete transaction by ID."""
        if id in self._transactions:
            del self._transactions[id]
            return True
        return False

    def filter_by_category(self, category: str) -> List[Transaction]:
        """Get transactions filtered by category name (case-insensitive)."""
        return [
            txn for txn in self._transactions.values()
            if txn.category.lower() == category.lower()
        ]

    def filter_by_date_range(self, start: date, end: date) -> List[Transaction]:
        """Get transactions within date range (inclusive)."""
        return [
            txn for txn in self._transactions.values()
            if start <= txn.date <= end
        ]

    def sort_by_amount(self, ascending: bool = True) -> List[Transaction]:
        """Get all transactions sorted by amount."""
        return sorted(
            self._transactions.values(),
            key=lambda txn: txn.amount,
            reverse=not ascending
        )

    def get_next_id(self) -> int:
        """Get the next available transaction ID."""
        return self._next_id

    def clear(self) -> None:
        """Clear all transactions and reset ID counter (for testing)."""
        self._transactions.clear()
        self._next_id = 1
