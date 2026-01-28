"""Tests for authentication API endpoints."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_register_user(client: AsyncClient):
    """Test user registration."""
    response = await client.post(
        "/api/v1/auth/register",
        json={
            "email": "test@example.com",
            "password": "TestPassword123!",
            "display_name": "Test User",
            "preferred_currency": "PKR",
            "preferred_locale": "en",
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["success"] is True
    assert "user" in data["data"]
    assert "tokens" in data["data"]
    assert data["data"]["user"]["email"] == "test@example.com"
    assert "access_token" in data["data"]["tokens"]


@pytest.mark.asyncio
async def test_register_duplicate_email(client: AsyncClient):
    """Test registration with duplicate email fails."""
    user_data = {
        "email": "duplicate@example.com",
        "password": "TestPassword123!",
        "display_name": "Test User",
    }

    # First registration should succeed
    response1 = await client.post("/api/v1/auth/register", json=user_data)
    assert response1.status_code == 201

    # Second registration with same email should fail
    response2 = await client.post("/api/v1/auth/register", json=user_data)
    assert response2.status_code == 400


@pytest.mark.asyncio
async def test_login_success(client: AsyncClient):
    """Test successful login."""
    # Register first
    await client.post(
        "/api/v1/auth/register",
        json={
            "email": "login@example.com",
            "password": "TestPassword123!",
            "display_name": "Login Test",
        },
    )

    # Login
    response = await client.post(
        "/api/v1/auth/login",
        json={
            "email": "login@example.com",
            "password": "TestPassword123!",
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "tokens" in data["data"]


@pytest.mark.asyncio
async def test_login_invalid_credentials(client: AsyncClient):
    """Test login with invalid credentials fails."""
    response = await client.post(
        "/api/v1/auth/login",
        json={
            "email": "nonexistent@example.com",
            "password": "WrongPassword123!",
        },
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_get_current_user(client: AsyncClient):
    """Test getting current user profile."""
    # Register and get token
    register_response = await client.post(
        "/api/v1/auth/register",
        json={
            "email": "me@example.com",
            "password": "TestPassword123!",
            "display_name": "Me Test",
        },
    )
    token = register_response.json()["data"]["tokens"]["access_token"]

    # Get current user
    response = await client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["data"]["email"] == "me@example.com"


@pytest.mark.asyncio
async def test_get_current_user_unauthorized(client: AsyncClient):
    """Test getting current user without token fails."""
    response = await client.get("/api/v1/auth/me")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_logout(client: AsyncClient):
    """Test logout clears session."""
    # Register and get token
    register_response = await client.post(
        "/api/v1/auth/register",
        json={
            "email": "logout@example.com",
            "password": "TestPassword123!",
            "display_name": "Logout Test",
        },
    )
    token = register_response.json()["data"]["tokens"]["access_token"]

    # Logout
    response = await client.post(
        "/api/v1/auth/logout",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["data"]["message"] == "Logged out successfully"
