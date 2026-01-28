"""Tests for Summary API endpoints."""

import pytest
from datetime import date
from httpx import AsyncClient

from src.models import Transaction


@pytest.mark.asyncio
class TestSummaryAPI:
    """Tests for /api/v1/summary endpoints."""

    async def test_get_financial_summary_empty(self, client: AsyncClient):
        """Test financial summary with no transactions."""
        response = await client.get("/api/v1/summary/financial")
        assert response.status_code == 200
        data = response.json()
        assert float(data["total_income"]) == 0
        assert float(data["total_expense"]) == 0
        assert float(data["net_balance"]) == 0

    async def test_get_financial_summary(self, client: AsyncClient, sample_transaction: Transaction):
        """Test financial summary with transactions."""
        today = date.today()
        response = await client.get(
            f"/api/v1/summary/financial?start_date={today}&end_date={today}"
        )
        assert response.status_code == 200
        data = response.json()
        assert "total_income" in data
        assert "total_expense" in data
        assert "net_balance" in data

    async def test_get_category_breakdown(self, client: AsyncClient, sample_transaction: Transaction):
        """Test category breakdown."""
        today = date.today()
        response = await client.get(
            f"/api/v1/summary/categories?start_date={today}&end_date={today}&type=expense"
        )
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    async def test_get_monthly_trends(self, client: AsyncClient):
        """Test monthly trends."""
        year = date.today().year
        response = await client.get(f"/api/v1/summary/trends?year={year}")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    async def test_get_dashboard_summary(self, client: AsyncClient):
        """Test dashboard summary."""
        response = await client.get("/api/v1/summary/dashboard")
        assert response.status_code == 200
        data = response.json()
        assert "financial_summary" in data
        assert "category_breakdown" in data
