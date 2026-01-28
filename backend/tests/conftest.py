"""Pytest configuration and fixtures."""

import asyncio
from typing import AsyncGenerator, Generator
from uuid import uuid4

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlmodel import SQLModel

from src.main import app
from src.db.session import get_session
from src.models import Category, Transaction, Budget, TransactionType
from src.models.user import User
from src.core.security import hash_password, create_access_token


# Test database URL (in-memory SQLite for tests)
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest.fixture(scope="session")
def event_loop() -> Generator:
    """Create event loop for async tests."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="function")
async def engine():
    """Create test database engine."""
    engine = create_async_engine(
        TEST_DATABASE_URL,
        echo=False,
        future=True,
    )
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
    yield engine
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.drop_all)
    await engine.dispose()


@pytest_asyncio.fixture(scope="function")
async def session(engine) -> AsyncGenerator[AsyncSession, None]:
    """Create test database session."""
    async_session = sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )
    async with async_session() as session:
        yield session


@pytest_asyncio.fixture(scope="function")
async def client(session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """Create test client with overridden dependencies."""

    async def override_get_session():
        yield session

    app.dependency_overrides[get_session] = override_get_session

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client

    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def sample_category(session: AsyncSession) -> Category:
    """Create a sample category for testing."""
    category = Category(
        id=uuid4(),
        name="Test Category",
        emoji="🧪",
    )
    session.add(category)
    await session.commit()
    await session.refresh(category)
    return category


@pytest_asyncio.fixture
async def sample_categories(session: AsyncSession) -> list[Category]:
    """Create multiple sample categories."""
    categories = [
        Category(id=uuid4(), name="Food", emoji="🍔"),
        Category(id=uuid4(), name="Transport", emoji="🚗"),
        Category(id=uuid4(), name="Salary", emoji="💵"),
    ]
    for cat in categories:
        session.add(cat)
    await session.commit()
    for cat in categories:
        await session.refresh(cat)
    return categories


@pytest_asyncio.fixture
async def sample_transaction(session: AsyncSession, sample_category: Category, sample_user: User) -> Transaction:
    """Create a sample transaction for testing."""
    from datetime import date
    from decimal import Decimal

    transaction = Transaction(
        id=uuid4(),
        user_id=sample_user.id,
        type=TransactionType.expense,
        amount=Decimal("50.00"),
        category_id=sample_category.id,
        transaction_date=date.today(),
        note="Test transaction",
        recurring=False,
    )
    session.add(transaction)
    await session.commit()
    await session.refresh(transaction)
    return transaction


@pytest_asyncio.fixture
async def sample_budget(session: AsyncSession, sample_category: Category, sample_user: User) -> Budget:
    """Create a sample budget for testing."""
    from datetime import date
    from decimal import Decimal

    today = date.today()
    budget = Budget(
        id=uuid4(),
        user_id=sample_user.id,
        category_id=sample_category.id,
        limit_amount=Decimal("500.00"),
        month=today.month,
        year=today.year,
    )
    session.add(budget)
    await session.commit()
    await session.refresh(budget)
    return budget


@pytest_asyncio.fixture
async def sample_user(session: AsyncSession) -> User:
    """Create a sample user for testing."""
    user = User(
        id=uuid4(),
        email="testuser@example.com",
        password_hash=hash_password("TestPassword123!"),
        display_name="Test User",
        preferred_currency="PKR",
        preferred_locale="en",
        is_active=True,
    )
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user


@pytest_asyncio.fixture
async def auth_headers(sample_user: User) -> dict:
    """Generate auth headers for a sample user."""
    token = create_access_token(subject=str(sample_user.id))
    return {"Authorization": f"Bearer {token}"}


@pytest_asyncio.fixture
async def authenticated_client(
    session: AsyncSession, sample_user: User
) -> AsyncGenerator[AsyncClient, None]:
    """Create authenticated test client."""

    async def override_get_session():
        yield session

    app.dependency_overrides[get_session] = override_get_session

    token = create_access_token(subject=str(sample_user.id))
    transport = ASGITransport(app=app)
    async with AsyncClient(
        transport=transport,
        base_url="http://test",
        headers={"Authorization": f"Bearer {token}"},
    ) as client:
        yield client

    app.dependency_overrides.clear()
