"""Tests for SQLModel models."""

import pytest
from datetime import date, datetime
from decimal import Decimal
from uuid import uuid4

from src.models import (
    Category,
    CategoryRead,
    Transaction,
    TransactionCreate,
    TransactionType,
    Budget,
    BudgetCreate,
    BudgetStatus,
)


class TestCategoryModel:
    """Tests for Category model."""

    def test_category_creation(self):
        """Test creating a category."""
        category = Category(
            id=uuid4(),
            name="Food",
            emoji="🍔",
        )
        assert category.name == "Food"
        assert category.emoji == "🍔"
        assert category.id is not None

    def test_category_read_schema(self):
        """Test CategoryRead schema."""
        category_id = uuid4()
        category_read = CategoryRead(
            id=category_id,
            name="Transport",
            emoji="🚗",
        )
        assert category_read.id == category_id
        assert category_read.name == "Transport"


class TestTransactionModel:
    """Tests for Transaction model."""

    def test_transaction_creation(self):
        """Test creating a transaction."""
        category_id = uuid4()
        transaction = Transaction(
            id=uuid4(),
            type=TransactionType.expense,
            amount=Decimal("100.50"),
            category_id=category_id,
            date=date.today(),
            note="Test expense",
            recurring=False,
        )
        assert transaction.type == TransactionType.expense
        assert transaction.amount == Decimal("100.50")
        assert transaction.note == "Test expense"
        assert transaction.deleted_at is None

    def test_transaction_create_schema(self):
        """Test TransactionCreate schema."""
        category_id = uuid4()
        tx_create = TransactionCreate(
            type=TransactionType.income,
            amount=Decimal("1000.00"),
            category_id=category_id,
            date=date.today(),
            note="Salary",
            recurring=True,
        )
        assert tx_create.type == TransactionType.income
        assert tx_create.amount == Decimal("1000.00")
        assert tx_create.recurring is True

    def test_transaction_type_enum(self):
        """Test TransactionType enumeration."""
        assert TransactionType.income.value == "income"
        assert TransactionType.expense.value == "expense"


class TestBudgetModel:
    """Tests for Budget model."""

    def test_budget_creation(self):
        """Test creating a budget."""
        category_id = uuid4()
        budget = Budget(
            id=uuid4(),
            category_id=category_id,
            limit_amount=Decimal("500.00"),
            month=1,
            year=2026,
        )
        assert budget.limit_amount == Decimal("500.00")
        assert budget.month == 1
        assert budget.year == 2026

    def test_budget_create_schema(self):
        """Test BudgetCreate schema."""
        category_id = uuid4()
        budget_create = BudgetCreate(
            category_id=category_id,
            limit_amount=Decimal("300.00"),
            month=6,
            year=2026,
        )
        assert budget_create.month == 6
        assert budget_create.limit_amount == Decimal("300.00")

    def test_budget_status_schema(self):
        """Test BudgetStatus computed schema."""
        status = BudgetStatus(
            category="Food",
            emoji="🍔",
            limit=Decimal("500.00"),
            spent=Decimal("400.00"),
            remaining=Decimal("100.00"),
            percentage=Decimal("80.00"),
            exceeded=False,
            warning=True,
        )
        assert status.warning is True
        assert status.exceeded is False
        assert status.percentage == Decimal("80.00")
