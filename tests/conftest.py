"""Shared pytest fixtures for AI Wealth & Spending Companion tests."""
import pytest
from datetime import date

from src.models import Category, Transaction, Budget
from src.repositories.memory import (
    InMemoryCategoryRepository,
    InMemoryTransactionRepository,
    InMemoryBudgetRepository,
)
from src.services import TransactionService, BudgetService, CategoryService


@pytest.fixture
def category_repo():
    """Fresh in-memory category repository."""
    return InMemoryCategoryRepository()


@pytest.fixture
def transaction_repo():
    """Fresh in-memory transaction repository."""
    return InMemoryTransactionRepository()


@pytest.fixture
def budget_repo():
    """Fresh in-memory budget repository."""
    return InMemoryBudgetRepository()


@pytest.fixture
def category_service(category_repo):
    """Category service with fresh repository."""
    service = CategoryService(category_repo)
    service.load_default_categories()
    return service


@pytest.fixture
def transaction_service(transaction_repo, category_repo):
    """Transaction service with fresh repositories and default categories."""
    cat_service = CategoryService(category_repo)
    cat_service.load_default_categories()
    return TransactionService(transaction_repo, category_repo)


@pytest.fixture
def budget_service(budget_repo, transaction_repo, category_repo):
    """Budget service with fresh repositories and default categories."""
    cat_service = CategoryService(category_repo)
    cat_service.load_default_categories()
    return BudgetService(budget_repo, transaction_repo, category_repo)


@pytest.fixture
def sample_categories():
    """Default categories for testing."""
    return [
        Category(name="Food", emoji="🍔"),
        Category(name="Rent", emoji="🏠"),
        Category(name="Utilities", emoji="💡"),
        Category(name="Salary", emoji="💵"),
        Category(name="Investment", emoji="💎"),
    ]


@pytest.fixture
def sample_transaction():
    """Sample transaction for testing."""
    return Transaction(
        id=1,
        type="expense",
        amount=50.0,
        category="Food",
        note="Grocery shopping",
        date=date.today(),
        recurring=False,
    )


@pytest.fixture
def sample_budget():
    """Sample budget for testing."""
    return Budget(category="Food", limit=500.0)
