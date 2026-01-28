"""Tests for Transactions API endpoints."""

import pytest
from datetime import date
from decimal import Decimal
from httpx import AsyncClient

from src.models import Category, Transaction


@pytest.mark.asyncio
class TestTransactionsAPI:
    """Tests for /api/v1/transactions endpoints."""

    async def test_list_transactions_empty(self, client: AsyncClient):
        """Test listing transactions when empty."""
        response = await client.get("/api/v1/transactions")
        assert response.status_code == 200
        assert response.json() == []

    async def test_list_transactions(self, client: AsyncClient, sample_transaction: Transaction):
        """Test listing transactions."""
        response = await client.get("/api/v1/transactions")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["id"] == str(sample_transaction.id)

    async def test_create_transaction(self, client: AsyncClient, sample_category: Category):
        """Test creating a transaction."""
        payload = {
            "type": "expense",
            "amount": 75.50,
            "category_id": str(sample_category.id),
            "date": str(date.today()),
            "note": "Lunch",
            "recurring": False,
        }
        response = await client.post("/api/v1/transactions", json=payload)
        assert response.status_code == 201
        data = response.json()
        assert data["type"] == "expense"
        assert float(data["amount"]) == 75.50
        assert data["note"] == "Lunch"

    async def test_create_transaction_invalid_category(self, client: AsyncClient):
        """Test creating a transaction with invalid category."""
        from uuid import uuid4
        payload = {
            "type": "expense",
            "amount": 50.00,
            "category_id": str(uuid4()),
            "date": str(date.today()),
        }
        response = await client.post("/api/v1/transactions", json=payload)
        assert response.status_code == 400

    async def test_get_transaction_by_id(self, client: AsyncClient, sample_transaction: Transaction):
        """Test getting a transaction by ID."""
        response = await client.get(f"/api/v1/transactions/{sample_transaction.id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == str(sample_transaction.id)
        assert "category_name" in data

    async def test_update_transaction(self, client: AsyncClient, sample_transaction: Transaction):
        """Test updating a transaction."""
        payload = {"note": "Updated note", "amount": 100.00}
        response = await client.put(
            f"/api/v1/transactions/{sample_transaction.id}",
            json=payload,
        )
        assert response.status_code == 200
        data = response.json()
        assert data["note"] == "Updated note"
        assert float(data["amount"]) == 100.00

    async def test_delete_transaction(self, client: AsyncClient, sample_transaction: Transaction):
        """Test deleting a transaction (soft delete)."""
        response = await client.delete(f"/api/v1/transactions/{sample_transaction.id}")
        assert response.status_code == 204

        # Verify it's no longer in the list
        response = await client.get("/api/v1/transactions")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 0

    async def test_search_transactions(self, client: AsyncClient, sample_transaction: Transaction):
        """Test searching transactions."""
        response = await client.get("/api/v1/transactions/search?q=Test")
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 1
