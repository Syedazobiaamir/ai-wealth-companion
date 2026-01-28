"""Tests for Categories API endpoints."""

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from src.models import Category


@pytest.mark.asyncio
class TestCategoriesAPI:
    """Tests for /api/v1/categories endpoints."""

    async def test_list_categories_empty(self, client: AsyncClient):
        """Test listing categories when empty."""
        response = await client.get("/api/v1/categories")
        assert response.status_code == 200
        assert response.json() == []

    async def test_list_categories(self, client: AsyncClient, sample_categories: list[Category]):
        """Test listing categories."""
        response = await client.get("/api/v1/categories")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 3
        names = [c["name"] for c in data]
        assert "Food" in names
        assert "Transport" in names

    async def test_get_category_by_id(self, client: AsyncClient, sample_category: Category):
        """Test getting a category by ID."""
        response = await client.get(f"/api/v1/categories/{sample_category.id}")
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == sample_category.name
        assert data["emoji"] == sample_category.emoji

    async def test_get_category_not_found(self, client: AsyncClient):
        """Test getting a non-existent category."""
        from uuid import uuid4
        fake_id = uuid4()
        response = await client.get(f"/api/v1/categories/{fake_id}")
        assert response.status_code == 404

    async def test_search_categories(self, client: AsyncClient, sample_categories: list[Category]):
        """Test searching categories."""
        response = await client.get("/api/v1/categories/search?q=Food")
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 1
        assert data[0]["name"] == "Food"
