"""Seed database with default categories."""

import asyncio
from uuid import uuid4
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession

from src.db.session import async_session_factory, init_db
from src.models.category import Category


DEFAULT_CATEGORIES = [
    {"name": "Food", "emoji": "\U0001F354"},  # Burger
    {"name": "Rent", "emoji": "\U0001F3E0"},  # House
    {"name": "Utilities", "emoji": "\U0001F4A1"},  # Light bulb
    {"name": "Salary", "emoji": "\U0001F4B5"},  # Dollar
    {"name": "Investment", "emoji": "\U0001F48E"},  # Gem
    {"name": "Transportation", "emoji": "\U0001F697"},  # Car
    {"name": "Entertainment", "emoji": "\U0001F3AC"},  # Clapper board
    {"name": "Healthcare", "emoji": "\U0001F3E5"},  # Hospital
    {"name": "Shopping", "emoji": "\U0001F6D2"},  # Shopping cart
    {"name": "Education", "emoji": "\U0001F4DA"},  # Books
    {"name": "Travel", "emoji": "\u2708\uFE0F"},  # Airplane
    {"name": "Other", "emoji": "\U0001F4C1"},  # Folder
]


async def seed_categories(session: AsyncSession) -> None:
    """Seed default categories if they don't exist."""
    from sqlalchemy import select

    # Check if categories already exist
    result = await session.execute(select(Category).limit(1))
    existing = result.scalar_one_or_none()

    if existing:
        print("Categories already seeded, skipping...")
        return

    # Insert default categories
    for cat_data in DEFAULT_CATEGORIES:
        category = Category(
            id=uuid4(),
            name=cat_data["name"],
            emoji=cat_data["emoji"],
            created_at=datetime.utcnow(),
        )
        session.add(category)

    await session.commit()
    print(f"Seeded {len(DEFAULT_CATEGORIES)} default categories")


async def main() -> None:
    """Run seed operations."""
    print("Initializing database...")
    await init_db()

    print("Seeding categories...")
    async with async_session_factory() as session:
        await seed_categories(session)

    print("Seed complete!")


if __name__ == "__main__":
    asyncio.run(main())
