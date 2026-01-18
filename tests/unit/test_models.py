"""Unit tests for data models."""
import pytest
from datetime import date

from src.models.result import Result
from src.models.category import Category
from src.models.transaction import Transaction
from src.models.budget import Budget, BudgetStatus


class TestResult:
    """Tests for Result type."""

    def test_ok_creates_success_result(self):
        """Ok() creates a successful result with value."""
        result = Result.ok(42)
        assert result.is_ok() is True
        assert result.is_err() is False
        assert result.unwrap() == 42

    def test_err_creates_failure_result(self):
        """Err() creates a failure result with error."""
        result = Result.err("Something went wrong")
        assert result.is_ok() is False
        assert result.is_err() is True
        assert result.unwrap_err() == "Something went wrong"

    def test_unwrap_raises_on_error(self):
        """unwrap() raises ValueError on error result."""
        result = Result.err("Error")
        with pytest.raises(ValueError):
            result.unwrap()

    def test_unwrap_err_raises_on_ok(self):
        """unwrap_err() raises ValueError on ok result."""
        result = Result.ok("Success")
        with pytest.raises(ValueError):
            result.unwrap_err()


class TestCategory:
    """Tests for Category model."""

    def test_category_creation(self):
        """Category can be created with name and emoji."""
        cat = Category(name="Food", emoji="🍔")
        assert cat.name == "Food"
        assert cat.emoji == "🍔"

    def test_category_default_emoji(self):
        """Category has empty string as default emoji."""
        cat = Category(name="Other")
        assert cat.name == "Other"
        assert cat.emoji == ""

    def test_category_equality(self):
        """Categories with same name and emoji are equal."""
        cat1 = Category(name="Food", emoji="🍔")
        cat2 = Category(name="Food", emoji="🍔")
        assert cat1 == cat2

    def test_category_display_with_emoji(self):
        """Category display includes emoji when present."""
        cat = Category(name="Food", emoji="🍔")
        assert cat.display() == "🍔 Food"

    def test_category_display_without_emoji(self):
        """Category display is just name when no emoji."""
        cat = Category(name="Other", emoji="")
        assert cat.display() == "Other"


class TestTransaction:
    """Tests for Transaction model."""

    def test_transaction_creation(self):
        """Transaction can be created with all fields."""
        txn = Transaction(
            id=1,
            type="expense",
            amount=50.0,
            category="Food",
            note="Lunch",
            date=date(2026, 1, 18),
            recurring=False,
        )
        assert txn.id == 1
        assert txn.type == "expense"
        assert txn.amount == 50.0
        assert txn.category == "Food"
        assert txn.note == "Lunch"
        assert txn.date == date(2026, 1, 18)
        assert txn.recurring is False

    def test_transaction_default_values(self):
        """Transaction has sensible defaults."""
        txn = Transaction(
            id=1,
            type="income",
            amount=100.0,
            category="Salary",
        )
        assert txn.note == ""
        assert txn.date == date.today()
        assert txn.recurring is False

    def test_transaction_is_income(self):
        """is_income() returns True for income type."""
        txn = Transaction(id=1, type="income", amount=100.0, category="Salary")
        assert txn.is_income() is True
        assert txn.is_expense() is False

    def test_transaction_is_expense(self):
        """is_expense() returns True for expense type."""
        txn = Transaction(id=1, type="expense", amount=50.0, category="Food")
        assert txn.is_income() is False
        assert txn.is_expense() is True


class TestBudget:
    """Tests for Budget model."""

    def test_budget_creation(self):
        """Budget can be created with category and limit."""
        budget = Budget(category="Food", limit=500.0)
        assert budget.category == "Food"
        assert budget.limit == 500.0

    def test_budget_equality(self):
        """Budgets with same category and limit are equal."""
        b1 = Budget(category="Food", limit=500.0)
        b2 = Budget(category="Food", limit=500.0)
        assert b1 == b2


class TestBudgetStatus:
    """Tests for BudgetStatus model."""

    def test_budget_status_creation(self):
        """BudgetStatus can be created with all fields."""
        status = BudgetStatus(
            category="Food",
            limit=500.0,
            spent=200.0,
            remaining=300.0,
            percentage=40.0,
            exceeded=False,
        )
        assert status.category == "Food"
        assert status.limit == 500.0
        assert status.spent == 200.0
        assert status.remaining == 300.0
        assert status.percentage == 40.0
        assert status.exceeded is False

    def test_budget_status_exceeded(self):
        """BudgetStatus correctly reflects exceeded state."""
        status = BudgetStatus(
            category="Food",
            limit=500.0,
            spent=600.0,
            remaining=-100.0,
            percentage=120.0,
            exceeded=True,
        )
        assert status.exceeded is True
        assert status.remaining == -100.0
        assert status.percentage == 120.0
