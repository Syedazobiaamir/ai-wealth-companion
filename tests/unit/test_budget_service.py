"""Unit tests for BudgetService."""
import pytest

from src.models import Budget
from src.repositories.memory import (
    InMemoryBudgetRepository,
    InMemoryTransactionRepository,
    InMemoryCategoryRepository,
)
from src.services.budget_service import BudgetService
from src.services.category_service import CategoryService
from src.services.transaction_service import TransactionService


class TestBudgetService:
    """Tests for BudgetService."""

    @pytest.fixture
    def repos(self):
        """Fresh repositories."""
        budget_repo = InMemoryBudgetRepository()
        txn_repo = InMemoryTransactionRepository()
        cat_repo = InMemoryCategoryRepository()
        return budget_repo, txn_repo, cat_repo

    @pytest.fixture
    def services(self, repos):
        """BudgetService with loaded categories."""
        budget_repo, txn_repo, cat_repo = repos

        # Load default categories
        cat_service = CategoryService(cat_repo)
        cat_service.load_default_categories()

        txn_service = TransactionService(txn_repo, cat_repo)
        budget_service = BudgetService(budget_repo, txn_repo, cat_repo)

        return budget_service, txn_service

    def test_set_budget_success(self, services):
        """set_budget creates budget for valid category."""
        budget_service, _ = services

        result = budget_service.set_budget("Food", 500.0)

        assert result.is_ok()
        budget = result.unwrap()
        assert budget.category == "Food"
        assert budget.limit == 500.0

    def test_set_budget_invalid_category(self, services):
        """set_budget rejects non-existent category."""
        budget_service, _ = services

        result = budget_service.set_budget("NonExistent", 500.0)

        assert result.is_err()
        assert "category" in result.unwrap_err().lower()

    def test_set_budget_invalid_limit(self, services):
        """set_budget rejects zero or negative limit."""
        budget_service, _ = services

        result = budget_service.set_budget("Food", 0)
        assert result.is_err()
        assert "limit" in result.unwrap_err().lower()

        result = budget_service.set_budget("Food", -100)
        assert result.is_err()

    def test_set_budget_updates_existing(self, services):
        """set_budget updates existing budget."""
        budget_service, _ = services

        budget_service.set_budget("Food", 500.0)
        result = budget_service.set_budget("Food", 750.0)

        assert result.is_ok()
        assert result.unwrap().limit == 750.0

    def test_get_budget_status_no_spending(self, services):
        """get_budget_status shows zero spent when no transactions."""
        budget_service, _ = services

        budget_service.set_budget("Food", 500.0)
        result = budget_service.get_budget_status("Food")

        assert result.is_ok()
        status = result.unwrap()
        assert status.category == "Food"
        assert status.limit == 500.0
        assert status.spent == 0.0
        assert status.remaining == 500.0
        assert status.percentage == 0.0
        assert status.exceeded is False

    def test_get_budget_status_with_spending(self, services):
        """get_budget_status calculates spent from transactions."""
        budget_service, txn_service = services

        budget_service.set_budget("Food", 500.0)
        txn_service.add_transaction(type="expense", amount=100.0, category="Food")
        txn_service.add_transaction(type="expense", amount=150.0, category="Food")

        result = budget_service.get_budget_status("Food")

        assert result.is_ok()
        status = result.unwrap()
        assert status.spent == 250.0
        assert status.remaining == 250.0
        assert status.percentage == 50.0
        assert status.exceeded is False

    def test_get_budget_status_exceeded(self, services):
        """get_budget_status detects overspending."""
        budget_service, txn_service = services

        budget_service.set_budget("Food", 500.0)
        txn_service.add_transaction(type="expense", amount=600.0, category="Food")

        result = budget_service.get_budget_status("Food")

        assert result.is_ok()
        status = result.unwrap()
        assert status.spent == 600.0
        assert status.remaining == -100.0
        assert status.percentage == 120.0
        assert status.exceeded is True

    def test_get_budget_status_ignores_income(self, services):
        """get_budget_status only counts expenses."""
        budget_service, txn_service = services

        budget_service.set_budget("Salary", 5000.0)
        txn_service.add_transaction(type="income", amount=3000.0, category="Salary")

        result = budget_service.get_budget_status("Salary")

        assert result.is_ok()
        status = result.unwrap()
        assert status.spent == 0.0  # Income not counted

    def test_get_budget_status_category_not_found(self, services):
        """get_budget_status returns error for non-existent category."""
        budget_service, _ = services

        result = budget_service.get_budget_status("NonExistent")
        assert result.is_err()

    def test_get_budget_status_no_budget_set(self, services):
        """get_budget_status returns error when no budget set."""
        budget_service, _ = services

        result = budget_service.get_budget_status("Food")
        assert result.is_err()
        assert "no budget" in result.unwrap_err().lower()

    def test_get_all_budgets_status(self, services):
        """get_all_budgets_status returns status for all budgets."""
        budget_service, txn_service = services

        budget_service.set_budget("Food", 500.0)
        budget_service.set_budget("Rent", 2000.0)
        txn_service.add_transaction(type="expense", amount=200.0, category="Food")
        txn_service.add_transaction(type="expense", amount=1800.0, category="Rent")

        statuses = budget_service.get_all_budgets_status()

        assert len(statuses) == 2

        food_status = next(s for s in statuses if s.category == "Food")
        assert food_status.spent == 200.0

        rent_status = next(s for s in statuses if s.category == "Rent")
        assert rent_status.spent == 1800.0
