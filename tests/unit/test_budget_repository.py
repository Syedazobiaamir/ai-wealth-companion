"""Unit tests for BudgetRepository."""
import pytest

from src.models import Budget
from src.repositories.memory import InMemoryBudgetRepository


class TestInMemoryBudgetRepository:
    """Tests for InMemoryBudgetRepository."""

    @pytest.fixture
    def repo(self):
        """Fresh repository for each test."""
        return InMemoryBudgetRepository()

    def test_set_creates_budget(self, repo):
        """set creates a new budget."""
        budget = Budget(category="Food", limit=500.0)
        result = repo.set(budget)

        assert result.category == "Food"
        assert result.limit == 500.0

    def test_set_updates_existing_budget(self, repo):
        """set updates existing budget for same category."""
        repo.set(Budget(category="Food", limit=500.0))
        repo.set(Budget(category="Food", limit=750.0))

        result = repo.get_by_category("Food")
        assert result.limit == 750.0

    def test_get_by_category_returns_budget(self, repo):
        """get_by_category returns correct budget."""
        repo.set(Budget(category="Food", limit=500.0))

        result = repo.get_by_category("Food")
        assert result is not None
        assert result.limit == 500.0

    def test_get_by_category_case_insensitive(self, repo):
        """get_by_category is case-insensitive."""
        repo.set(Budget(category="Food", limit=500.0))

        assert repo.get_by_category("food") is not None
        assert repo.get_by_category("FOOD") is not None

    def test_get_by_category_returns_none_for_missing(self, repo):
        """get_by_category returns None for non-existent category."""
        result = repo.get_by_category("NonExistent")
        assert result is None

    def test_get_all_returns_all_budgets(self, repo):
        """get_all returns all set budgets."""
        repo.set(Budget(category="Food", limit=500.0))
        repo.set(Budget(category="Rent", limit=2000.0))
        repo.set(Budget(category="Utilities", limit=300.0))

        all_budgets = repo.get_all()
        assert len(all_budgets) == 3
