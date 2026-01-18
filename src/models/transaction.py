"""Transaction model for financial events."""
from dataclasses import dataclass, field
from datetime import date
from typing import Optional


@dataclass
class Transaction:
    """
    Represents a financial event (income or expense).

    Attributes:
        id: Unique identifier (auto-generated)
        type: Transaction direction ("income" or "expense")
        amount: Transaction value (must be > 0)
        category: Classification (must reference existing Category)
        note: Optional user notes (max 500 chars)
        date: Transaction date (YYYY-MM-DD format)
        recurring: Whether this is a recurring transaction
    """
    id: int
    type: str  # "income" or "expense"
    amount: float
    category: str
    note: str = field(default="")
    date: date = field(default_factory=date.today)
    recurring: bool = field(default=False)

    def is_income(self) -> bool:
        """Return True if this is an income transaction."""
        return self.type == "income"

    def is_expense(self) -> bool:
        """Return True if this is an expense transaction."""
        return self.type == "expense"

    def __hash__(self):
        return hash(self.id)
