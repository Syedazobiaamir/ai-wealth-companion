"""Tests for Budgets API endpoints."""

import pytest
from datetime import date
from httpx import AsyncClient

from src.models import Category, Budget


@pytest.mark.asyncio
class TestBudgetsAPI:
    """Tests for /api/v1/budgets endpoints."""

    async def test_list_budgets_empty(self, client: AsyncClient):
        """Test listing budgets when empty."""
        response = await client.get("/api/v1/budgets")
        assert response.status_code == 200
        assert response.json() == []

    async def test_list_budgets(self, client: AsyncClient, sample_budget: Budget):
        """Test listing budgets."""
        today = date.today()
        response = await client.get(
            f"/api/v1/budgets?month={today.month}&year={today.year}"
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["id"] == str(sample_budget.id)

    async def test_create_budget(self, client: AsyncClient, sample_category: Category):
        """Test creating a budget."""
        today = date.today()
        payload = {
            "category_id": str(sample_category.id),
            "limit_amount": 300.00,
            "month": today.month,
            "year": today.year,
        }
        response = await client.post("/api/v1/budgets", json=payload)
        assert response.status_code == 201
        data = response.json()
        assert float(data["limit_amount"]) == 300.00
        assert data["month"] == today.month

    async def test_create_budget_invalid_category(self, client: AsyncClient):
        """Test creating a budget with invalid category."""
        from uuid import uuid4
        today = date.today()
        payload = {
            "category_id": str(uuid4()),
            "limit_amount": 200.00,
            "month": today.month,
            "year": today.year,
        }
        response = await client.post("/api/v1/budgets", json=payload)
        assert response.status_code == 400

    async def test_get_budget_by_id(self, client: AsyncClient, sample_budget: Budget):
        """Test getting a budget by ID."""
        response = await client.get(f"/api/v1/budgets/{sample_budget.id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == str(sample_budget.id)

    async def test_get_budget_status(self, client: AsyncClient, sample_budget: Budget):
        """Test getting budget status."""
        today = date.today()
        response = await client.get(
            f"/api/v1/budgets/status?month={today.month}&year={today.year}"
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 1
        assert "spent" in data[0]
        assert "percentage" in data[0]

    async def test_delete_budget(self, client: AsyncClient, sample_budget: Budget):
        """Test deleting a budget."""
        response = await client.delete(f"/api/v1/budgets/{sample_budget.id}")
        assert response.status_code == 204

        # Verify it's deleted
        response = await client.get(f"/api/v1/budgets/{sample_budget.id}")
        assert response.status_code == 404
