"""Async database session management for Neon PostgreSQL or SQLite."""

from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from sqlmodel import SQLModel

from src.core.config import get_settings

# Import all models to register them with SQLModel
from src.models.user import User  # noqa: F401
from src.models.wallet import Wallet  # noqa: F401
from src.models.category import Category  # noqa: F401
from src.models.transaction import Transaction  # noqa: F401
from src.models.budget import Budget  # noqa: F401
from src.models.goal import Goal  # noqa: F401
from src.models.monthly_snapshot import MonthlySnapshot  # noqa: F401
from src.models.insight_cache import InsightCache  # noqa: F401
from src.models.agent_memory import AgentMemory  # noqa: F401
from src.models.event_log import EventLog  # noqa: F401

settings = get_settings()

# Determine engine kwargs based on database type
is_sqlite = "sqlite" in settings.async_database_url

if is_sqlite:
    # SQLite configuration (for local development)
    engine_kwargs = {
        "echo": settings.debug,
        "future": True,
        "connect_args": {"check_same_thread": False},
        "poolclass": StaticPool,
    }
else:
    # PostgreSQL configuration (for production with Neon serverless)
    engine_kwargs = {
        "echo": settings.debug,
        "future": True,
        "pool_pre_ping": True,
        "pool_size": 5,
        "max_overflow": 10,
        "pool_recycle": 300,  # Recycle connections every 5 minutes
        "pool_timeout": 30,  # Connection timeout
        "connect_args": {
            "server_settings": {
                "application_name": "ai-wealth-companion",
            },
            "command_timeout": 30,  # Query timeout
        },
    }

# Create async engine
engine = create_async_engine(settings.async_database_url, **engine_kwargs)

# Async session factory
async_session_factory = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


async def init_db() -> None:
    """Initialize database tables."""
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """Dependency that provides an async database session."""
    async with async_session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
