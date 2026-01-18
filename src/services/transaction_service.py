"""Transaction service for business logic."""
from datetime import date, datetime
from typing import List, Optional, Dict, Any

from src.models import Transaction, Result
from src.repositories.base import TransactionRepository, CategoryRepository


VALID_TYPES = {"income", "expense"}


class TransactionService:
    """Business logic for transaction operations."""

    def __init__(
        self,
        transaction_repo: TransactionRepository,
        category_repo: CategoryRepository,
    ):
        self._txn_repo = transaction_repo
        self._cat_repo = category_repo

    def add_transaction(
        self,
        type: str,
        amount: float,
        category: str,
        note: str = "",
        date: Optional[str] = None,
        recurring: bool = False,
    ) -> Result[Transaction, str]:
        """
        Add a new transaction.

        Args:
            type: "income" or "expense"
            amount: Transaction value (must be > 0)
            category: Category name (must exist)
            note: Optional user note
            date: Optional date string (YYYY-MM-DD), defaults to today
            recurring: Whether this is recurring

        Returns:
            Result with Transaction on success, error message on failure
        """
        # Validate type
        if type not in VALID_TYPES:
            return Result.err(f"Invalid type '{type}'. Must be 'income' or 'expense'.")

        # Validate amount
        if amount <= 0:
            return Result.err(f"Invalid amount {amount}. Amount must be greater than 0.")

        # Validate category exists
        if not self._cat_repo.exists(category):
            return Result.err(f"Category '{category}' not found.")

        # Parse date
        txn_date = self._parse_date(date)
        if txn_date is None:
            return Result.err(f"Invalid date format '{date}'. Use YYYY-MM-DD.")

        # Create transaction
        txn = Transaction(
            id=0,  # Will be assigned by repository
            type=type,
            amount=amount,
            category=category,
            note=note[:500] if note else "",  # Truncate to max 500 chars
            date=txn_date,
            recurring=recurring,
        )

        created = self._txn_repo.create(txn)
        return Result.ok(created)

    def update_transaction(self, id: int, **updates) -> Result[Transaction, str]:
        """
        Update an existing transaction.

        Args:
            id: Transaction ID
            **updates: Fields to update (type, amount, category, note, date, recurring)

        Returns:
            Result with updated Transaction on success, error message on failure
        """
        # Check transaction exists
        existing = self._txn_repo.get_by_id(id)
        if existing is None:
            return Result.err(f"Transaction {id} not found.")

        # Validate updates
        validated_updates = {}

        if "type" in updates:
            if updates["type"] not in VALID_TYPES:
                return Result.err(f"Invalid type '{updates['type']}'. Must be 'income' or 'expense'.")
            validated_updates["type"] = updates["type"]

        if "amount" in updates:
            if updates["amount"] <= 0:
                return Result.err(f"Invalid amount. Amount must be greater than 0.")
            validated_updates["amount"] = updates["amount"]

        if "category" in updates:
            if not self._cat_repo.exists(updates["category"]):
                return Result.err(f"Category '{updates['category']}' not found.")
            validated_updates["category"] = updates["category"]

        if "note" in updates:
            validated_updates["note"] = updates["note"][:500] if updates["note"] else ""

        if "date" in updates:
            parsed = self._parse_date(updates["date"])
            if parsed is None:
                return Result.err(f"Invalid date format. Use YYYY-MM-DD.")
            validated_updates["date"] = parsed

        if "recurring" in updates:
            validated_updates["recurring"] = bool(updates["recurring"])

        # Apply updates
        updated = self._txn_repo.update(id, validated_updates)
        return Result.ok(updated)

    def delete_transaction(self, id: int) -> Result[bool, str]:
        """
        Delete a transaction.

        Args:
            id: Transaction ID

        Returns:
            Result with True on success, error message on failure
        """
        if not self._txn_repo.delete(id):
            return Result.err(f"Transaction {id} not found.")
        return Result.ok(True)

    def list_transactions(self) -> List[Transaction]:
        """Get all transactions."""
        return self._txn_repo.get_all()

    def get_transaction(self, id: int) -> Optional[Transaction]:
        """Get a single transaction by ID."""
        return self._txn_repo.get_by_id(id)

    def filter_by_category(self, category: str) -> List[Transaction]:
        """Get transactions filtered by category."""
        return self._txn_repo.filter_by_category(category)

    def filter_by_date(self, start: str, end: str) -> Result[List[Transaction], str]:
        """
        Get transactions within date range.

        Args:
            start: Start date (YYYY-MM-DD)
            end: End date (YYYY-MM-DD)

        Returns:
            Result with filtered list on success, error message on failure
        """
        start_date = self._parse_date(start)
        end_date = self._parse_date(end)

        if start_date is None or end_date is None:
            return Result.err("Invalid date format. Use YYYY-MM-DD.")

        return Result.ok(self._txn_repo.filter_by_date_range(start_date, end_date))

    def sort_by_amount(self, descending: bool = False) -> List[Transaction]:
        """Get transactions sorted by amount."""
        return self._txn_repo.sort_by_amount(ascending=not descending)

    def toggle_recurring(self, id: int) -> Result[Transaction, str]:
        """Toggle the recurring flag on a transaction."""
        txn = self._txn_repo.get_by_id(id)
        if txn is None:
            return Result.err(f"Transaction {id} not found.")

        updated = self._txn_repo.update(id, {"recurring": not txn.recurring})
        return Result.ok(updated)

    def get_totals(self) -> Dict[str, float]:
        """
        Calculate total income, expenses, and net.

        Returns:
            Dictionary with 'income', 'expense', and 'net' keys
        """
        transactions = self._txn_repo.get_all()
        income = sum(t.amount for t in transactions if t.is_income())
        expense = sum(t.amount for t in transactions if t.is_expense())
        return {
            "income": income,
            "expense": expense,
            "net": income - expense,
        }

    def get_category_totals(self) -> Dict[str, float]:
        """
        Calculate total expenses per category.

        Returns:
            Dictionary of category name -> total expense amount
        """
        transactions = self._txn_repo.get_all()
        totals: Dict[str, float] = {}
        for txn in transactions:
            if txn.is_expense():
                key = txn.category.lower()
                totals[key] = totals.get(key, 0) + txn.amount
        return totals

    def _parse_date(self, date_str: Optional[str]) -> Optional[date]:
        """Parse date string or return today if None."""
        if date_str is None:
            return date.today()
        try:
            return datetime.strptime(date_str, "%Y-%m-%d").date()
        except ValueError:
            return None
