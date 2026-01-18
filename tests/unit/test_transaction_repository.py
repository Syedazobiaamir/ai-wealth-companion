"""Unit tests for TransactionRepository."""
import pytest
from datetime import date, timedelta

from src.models import Transaction
from src.repositories.memory import InMemoryTransactionRepository


class TestInMemoryTransactionRepository:
    """Tests for InMemoryTransactionRepository."""

    @pytest.fixture
    def repo(self):
        """Fresh repository for each test."""
        return InMemoryTransactionRepository()

    @pytest.fixture
    def sample_txn(self):
        """Sample transaction without ID (ID assigned on create)."""
        return Transaction(
            id=0,  # Will be assigned
            type="expense",
            amount=50.0,
            category="Food",
            note="Test expense",
            date=date.today(),
            recurring=False,
        )

    def test_create_assigns_id(self, repo, sample_txn):
        """Create assigns auto-incrementing ID."""
        txn = repo.create(sample_txn)
        assert txn.id == 1

        txn2 = repo.create(sample_txn)
        assert txn2.id == 2

    def test_get_by_id_returns_transaction(self, repo, sample_txn):
        """get_by_id returns the correct transaction."""
        created = repo.create(sample_txn)
        fetched = repo.get_by_id(created.id)
        assert fetched is not None
        assert fetched.id == created.id
        assert fetched.amount == 50.0

    def test_get_by_id_returns_none_for_missing(self, repo):
        """get_by_id returns None for non-existent ID."""
        result = repo.get_by_id(999)
        assert result is None

    def test_get_all_returns_all_transactions(self, repo, sample_txn):
        """get_all returns all created transactions."""
        repo.create(sample_txn)
        repo.create(sample_txn)
        repo.create(sample_txn)

        all_txns = repo.get_all()
        assert len(all_txns) == 3

    def test_update_modifies_transaction(self, repo, sample_txn):
        """update modifies transaction fields."""
        created = repo.create(sample_txn)
        updated = repo.update(created.id, {"amount": 75.0, "note": "Updated"})

        assert updated is not None
        assert updated.amount == 75.0
        assert updated.note == "Updated"
        assert updated.id == created.id  # ID unchanged

    def test_update_returns_none_for_missing(self, repo):
        """update returns None for non-existent ID."""
        result = repo.update(999, {"amount": 100.0})
        assert result is None

    def test_delete_removes_transaction(self, repo, sample_txn):
        """delete removes the transaction."""
        created = repo.create(sample_txn)
        result = repo.delete(created.id)

        assert result is True
        assert repo.get_by_id(created.id) is None

    def test_delete_returns_false_for_missing(self, repo):
        """delete returns False for non-existent ID."""
        result = repo.delete(999)
        assert result is False

    def test_filter_by_category(self, repo):
        """filter_by_category returns matching transactions."""
        repo.create(Transaction(id=0, type="expense", amount=50, category="Food"))
        repo.create(Transaction(id=0, type="expense", amount=100, category="Rent"))
        repo.create(Transaction(id=0, type="expense", amount=25, category="Food"))

        food_txns = repo.filter_by_category("Food")
        assert len(food_txns) == 2

        rent_txns = repo.filter_by_category("Rent")
        assert len(rent_txns) == 1

    def test_filter_by_category_case_insensitive(self, repo):
        """filter_by_category is case-insensitive."""
        repo.create(Transaction(id=0, type="expense", amount=50, category="Food"))

        result = repo.filter_by_category("food")
        assert len(result) == 1

        result = repo.filter_by_category("FOOD")
        assert len(result) == 1

    def test_filter_by_date_range(self, repo):
        """filter_by_date_range returns transactions in range."""
        today = date.today()
        yesterday = today - timedelta(days=1)
        tomorrow = today + timedelta(days=1)
        last_week = today - timedelta(days=7)

        repo.create(Transaction(id=0, type="expense", amount=50, category="Food", date=yesterday))
        repo.create(Transaction(id=0, type="expense", amount=100, category="Food", date=today))
        repo.create(Transaction(id=0, type="expense", amount=25, category="Food", date=last_week))

        # Yesterday to today should return 2
        result = repo.filter_by_date_range(yesterday, today)
        assert len(result) == 2

        # Last week to yesterday should return 2
        result = repo.filter_by_date_range(last_week, yesterday)
        assert len(result) == 2

    def test_sort_by_amount_ascending(self, repo):
        """sort_by_amount ascending returns smallest first."""
        repo.create(Transaction(id=0, type="expense", amount=100, category="Food"))
        repo.create(Transaction(id=0, type="expense", amount=25, category="Food"))
        repo.create(Transaction(id=0, type="expense", amount=50, category="Food"))

        result = repo.sort_by_amount(ascending=True)
        assert result[0].amount == 25
        assert result[1].amount == 50
        assert result[2].amount == 100

    def test_sort_by_amount_descending(self, repo):
        """sort_by_amount descending returns largest first."""
        repo.create(Transaction(id=0, type="expense", amount=100, category="Food"))
        repo.create(Transaction(id=0, type="expense", amount=25, category="Food"))
        repo.create(Transaction(id=0, type="expense", amount=50, category="Food"))

        result = repo.sort_by_amount(ascending=False)
        assert result[0].amount == 100
        assert result[1].amount == 50
        assert result[2].amount == 25

    def test_get_next_id(self, repo, sample_txn):
        """get_next_id returns the next available ID."""
        assert repo.get_next_id() == 1
        repo.create(sample_txn)
        assert repo.get_next_id() == 2
