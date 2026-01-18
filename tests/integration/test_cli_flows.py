"""Integration tests for CLI flows."""
import pytest
from datetime import date

from src.repositories.memory import (
    InMemoryTransactionRepository,
    InMemoryCategoryRepository,
    InMemoryBudgetRepository,
)
from src.services import TransactionService, BudgetService, CategoryService


class TestTransactionFlows:
    """Integration tests for transaction workflows."""

    @pytest.fixture
    def services(self):
        """Initialize all services with fresh repositories."""
        txn_repo = InMemoryTransactionRepository()
        cat_repo = InMemoryCategoryRepository()
        budget_repo = InMemoryBudgetRepository()

        cat_service = CategoryService(cat_repo)
        cat_service.load_default_categories()

        txn_service = TransactionService(txn_repo, cat_repo)
        budget_service = BudgetService(budget_repo, txn_repo, cat_repo)

        return txn_service, budget_service, cat_service

    def test_complete_transaction_lifecycle(self, services):
        """Test add → update → delete transaction flow."""
        txn_service, _, _ = services

        # Add
        result = txn_service.add_transaction(
            type="expense",
            amount=50.0,
            category="Food",
            note="Lunch",
        )
        assert result.is_ok()
        txn = result.unwrap()
        assert txn.id == 1

        # Update
        result = txn_service.update_transaction(1, amount=75.0)
        assert result.is_ok()
        assert result.unwrap().amount == 75.0

        # Delete
        result = txn_service.delete_transaction(1)
        assert result.is_ok()

        # Verify deleted
        assert txn_service.get_transaction(1) is None

    def test_multiple_transactions_with_filtering(self, services):
        """Test adding multiple transactions and filtering."""
        txn_service, _, _ = services

        # Add mixed transactions
        txn_service.add_transaction(type="income", amount=3000.0, category="Salary")
        txn_service.add_transaction(type="expense", amount=500.0, category="Food")
        txn_service.add_transaction(type="expense", amount=1000.0, category="Rent")
        txn_service.add_transaction(type="expense", amount=200.0, category="Food")
        txn_service.add_transaction(type="expense", amount=100.0, category="Utilities")

        # Filter by category
        food_txns = txn_service.filter_by_category("Food")
        assert len(food_txns) == 2
        assert sum(t.amount for t in food_txns) == 700.0

        # Get totals
        totals = txn_service.get_totals()
        assert totals["income"] == 3000.0
        assert totals["expense"] == 1800.0
        assert totals["net"] == 1200.0

    def test_sorting_transactions(self, services):
        """Test sorting transactions by amount."""
        txn_service, _, _ = services

        txn_service.add_transaction(type="expense", amount=100.0, category="Food")
        txn_service.add_transaction(type="expense", amount=50.0, category="Food")
        txn_service.add_transaction(type="expense", amount=200.0, category="Food")

        # Ascending
        sorted_asc = txn_service.sort_by_amount(descending=False)
        assert sorted_asc[0].amount == 50.0
        assert sorted_asc[-1].amount == 200.0

        # Descending
        sorted_desc = txn_service.sort_by_amount(descending=True)
        assert sorted_desc[0].amount == 200.0
        assert sorted_desc[-1].amount == 50.0


class TestBudgetFlows:
    """Integration tests for budget workflows."""

    @pytest.fixture
    def services(self):
        """Initialize all services with fresh repositories."""
        txn_repo = InMemoryTransactionRepository()
        cat_repo = InMemoryCategoryRepository()
        budget_repo = InMemoryBudgetRepository()

        cat_service = CategoryService(cat_repo)
        cat_service.load_default_categories()

        txn_service = TransactionService(txn_repo, cat_repo)
        budget_service = BudgetService(budget_repo, txn_repo, cat_repo)

        return txn_service, budget_service, cat_service

    def test_budget_tracking_with_transactions(self, services):
        """Test budget status updates as transactions are added."""
        txn_service, budget_service, _ = services

        # Set budget
        budget_service.set_budget("Food", 500.0)

        # Initial status
        result = budget_service.get_budget_status("Food")
        assert result.is_ok()
        status = result.unwrap()
        assert status.spent == 0.0
        assert status.remaining == 500.0
        assert status.exceeded is False

        # Add transactions
        txn_service.add_transaction(type="expense", amount=200.0, category="Food")
        txn_service.add_transaction(type="expense", amount=150.0, category="Food")

        # Check updated status
        result = budget_service.get_budget_status("Food")
        status = result.unwrap()
        assert status.spent == 350.0
        assert status.remaining == 150.0
        assert status.percentage == 70.0
        assert status.exceeded is False

        # Exceed budget
        txn_service.add_transaction(type="expense", amount=200.0, category="Food")

        result = budget_service.get_budget_status("Food")
        status = result.unwrap()
        assert status.spent == 550.0
        assert status.remaining == -50.0
        assert status.exceeded is True

    def test_multiple_budgets_status(self, services):
        """Test tracking multiple category budgets."""
        txn_service, budget_service, _ = services

        # Set budgets
        budget_service.set_budget("Food", 500.0)
        budget_service.set_budget("Rent", 2000.0)
        budget_service.set_budget("Utilities", 300.0)

        # Add transactions
        txn_service.add_transaction(type="expense", amount=400.0, category="Food")
        txn_service.add_transaction(type="expense", amount=1800.0, category="Rent")
        txn_service.add_transaction(type="expense", amount=250.0, category="Utilities")

        # Get all statuses
        statuses = budget_service.get_all_budgets_status()
        assert len(statuses) == 3

        food = next(s for s in statuses if s.category == "Food")
        assert food.spent == 400.0
        assert food.exceeded is False

        rent = next(s for s in statuses if s.category == "Rent")
        assert rent.spent == 1800.0
        assert rent.exceeded is False

        utilities = next(s for s in statuses if s.category == "Utilities")
        assert utilities.spent == 250.0
        assert utilities.exceeded is False


class TestRecurringTransactions:
    """Integration tests for recurring transaction flag."""

    @pytest.fixture
    def services(self):
        txn_repo = InMemoryTransactionRepository()
        cat_repo = InMemoryCategoryRepository()

        cat_service = CategoryService(cat_repo)
        cat_service.load_default_categories()

        txn_service = TransactionService(txn_repo, cat_repo)

        return txn_service, cat_service

    def test_toggle_recurring(self, services):
        """Test toggling recurring flag on transaction."""
        txn_service, _ = services

        # Add non-recurring
        txn_service.add_transaction(
            type="expense",
            amount=1000.0,
            category="Rent",
            recurring=False,
        )

        txn = txn_service.get_transaction(1)
        assert txn.recurring is False

        # Toggle to recurring
        result = txn_service.toggle_recurring(1)
        assert result.is_ok()
        assert result.unwrap().recurring is True

        # Toggle back
        result = txn_service.toggle_recurring(1)
        assert result.unwrap().recurring is False
