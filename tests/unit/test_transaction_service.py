"""Unit tests for TransactionService."""
import pytest
from datetime import date, timedelta

from src.models import Transaction, Category
from src.repositories.memory import InMemoryTransactionRepository, InMemoryCategoryRepository
from src.services.transaction_service import TransactionService
from src.services.category_service import CategoryService


class TestTransactionService:
    """Tests for TransactionService."""

    @pytest.fixture
    def repos(self):
        """Fresh repositories."""
        txn_repo = InMemoryTransactionRepository()
        cat_repo = InMemoryCategoryRepository()
        return txn_repo, cat_repo

    @pytest.fixture
    def service(self, repos):
        """TransactionService with default categories loaded."""
        txn_repo, cat_repo = repos
        cat_service = CategoryService(cat_repo)
        cat_service.load_default_categories()
        return TransactionService(txn_repo, cat_repo)

    def test_add_transaction_success(self, service):
        """add_transaction creates valid transaction."""
        result = service.add_transaction(
            type="expense",
            amount=50.0,
            category="Food",
            note="Lunch",
        )

        assert result.is_ok()
        txn = result.unwrap()
        assert txn.id == 1
        assert txn.type == "expense"
        assert txn.amount == 50.0
        assert txn.category == "Food"
        assert txn.note == "Lunch"

    def test_add_transaction_with_date(self, service):
        """add_transaction accepts custom date."""
        result = service.add_transaction(
            type="income",
            amount=3000.0,
            category="Salary",
            date="2026-01-15",
        )

        assert result.is_ok()
        txn = result.unwrap()
        assert txn.date == date(2026, 1, 15)

    def test_add_transaction_invalid_amount(self, service):
        """add_transaction rejects zero or negative amount."""
        result = service.add_transaction(
            type="expense",
            amount=0,
            category="Food",
        )
        assert result.is_err()
        assert "amount" in result.unwrap_err().lower()

        result = service.add_transaction(
            type="expense",
            amount=-50,
            category="Food",
        )
        assert result.is_err()

    def test_add_transaction_invalid_type(self, service):
        """add_transaction rejects invalid type."""
        result = service.add_transaction(
            type="invalid",
            amount=50.0,
            category="Food",
        )
        assert result.is_err()
        assert "type" in result.unwrap_err().lower()

    def test_add_transaction_invalid_category(self, service):
        """add_transaction rejects non-existent category."""
        result = service.add_transaction(
            type="expense",
            amount=50.0,
            category="NonExistent",
        )
        assert result.is_err()
        assert "category" in result.unwrap_err().lower()

    def test_add_transaction_invalid_date(self, service):
        """add_transaction rejects invalid date format."""
        result = service.add_transaction(
            type="expense",
            amount=50.0,
            category="Food",
            date="invalid-date",
        )
        assert result.is_err()
        assert "date" in result.unwrap_err().lower()

    def test_update_transaction_success(self, service):
        """update_transaction modifies existing transaction."""
        # Create first
        service.add_transaction(type="expense", amount=50.0, category="Food")

        # Update
        result = service.update_transaction(1, amount=75.0, note="Updated")

        assert result.is_ok()
        txn = result.unwrap()
        assert txn.amount == 75.0
        assert txn.note == "Updated"

    def test_update_transaction_not_found(self, service):
        """update_transaction returns error for non-existent ID."""
        result = service.update_transaction(999, amount=100.0)
        assert result.is_err()
        assert "not found" in result.unwrap_err().lower()

    def test_update_transaction_validates_amount(self, service):
        """update_transaction validates new amount."""
        service.add_transaction(type="expense", amount=50.0, category="Food")

        result = service.update_transaction(1, amount=-10)
        assert result.is_err()

    def test_update_transaction_validates_category(self, service):
        """update_transaction validates new category."""
        service.add_transaction(type="expense", amount=50.0, category="Food")

        result = service.update_transaction(1, category="NonExistent")
        assert result.is_err()

    def test_delete_transaction_success(self, service):
        """delete_transaction removes existing transaction."""
        service.add_transaction(type="expense", amount=50.0, category="Food")

        result = service.delete_transaction(1)
        assert result.is_ok()
        assert result.unwrap() is True

    def test_delete_transaction_not_found(self, service):
        """delete_transaction returns error for non-existent ID."""
        result = service.delete_transaction(999)
        assert result.is_err()
        assert "not found" in result.unwrap_err().lower()

    def test_list_transactions(self, service):
        """list_transactions returns all transactions."""
        service.add_transaction(type="expense", amount=50.0, category="Food")
        service.add_transaction(type="income", amount=3000.0, category="Salary")

        txns = service.list_transactions()
        assert len(txns) == 2

    def test_filter_by_category(self, service):
        """filter_by_category returns matching transactions."""
        service.add_transaction(type="expense", amount=50.0, category="Food")
        service.add_transaction(type="expense", amount=100.0, category="Rent")
        service.add_transaction(type="expense", amount=25.0, category="Food")

        result = service.filter_by_category("Food")
        assert len(result) == 2

    def test_filter_by_date(self, service):
        """filter_by_date returns transactions in range."""
        today = date.today()
        yesterday = today - timedelta(days=1)

        service.add_transaction(type="expense", amount=50.0, category="Food", date=yesterday.isoformat())
        service.add_transaction(type="expense", amount=100.0, category="Food", date=today.isoformat())

        result = service.filter_by_date(yesterday.isoformat(), today.isoformat())
        assert result.is_ok()
        assert len(result.unwrap()) == 2

    def test_filter_by_date_invalid_format(self, service):
        """filter_by_date returns error for invalid dates."""
        result = service.filter_by_date("invalid", "also-invalid")
        assert result.is_err()

    def test_sort_by_amount(self, service):
        """sort_by_amount returns sorted transactions."""
        service.add_transaction(type="expense", amount=100.0, category="Food")
        service.add_transaction(type="expense", amount=25.0, category="Food")
        service.add_transaction(type="expense", amount=50.0, category="Food")

        result = service.sort_by_amount(descending=False)
        assert result[0].amount == 25
        assert result[2].amount == 100

        result = service.sort_by_amount(descending=True)
        assert result[0].amount == 100
        assert result[2].amount == 25

    def test_toggle_recurring(self, service):
        """toggle_recurring flips the recurring flag."""
        service.add_transaction(type="expense", amount=50.0, category="Food", recurring=False)

        result = service.toggle_recurring(1)
        assert result.is_ok()
        assert result.unwrap().recurring is True

        result = service.toggle_recurring(1)
        assert result.is_ok()
        assert result.unwrap().recurring is False

    def test_get_totals(self, service):
        """get_totals returns income, expense, and net."""
        service.add_transaction(type="income", amount=3000.0, category="Salary")
        service.add_transaction(type="expense", amount=500.0, category="Food")
        service.add_transaction(type="expense", amount=1000.0, category="Rent")

        totals = service.get_totals()
        assert totals["income"] == 3000.0
        assert totals["expense"] == 1500.0
        assert totals["net"] == 1500.0
