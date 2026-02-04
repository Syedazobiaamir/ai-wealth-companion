"""FastAPI application entry point."""

import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address
from sqlalchemy import text

from src.api.v1.router import api_router
from src.core.config import get_settings
from src.db.session import init_db, engine, async_session_factory
from src.db.seed import seed_categories

settings = get_settings()

# Rate limiter
limiter = Limiter(key_func=get_remote_address)


async def keep_db_warm():
    """Background task to keep database connections warm and prevent cold starts."""
    while True:
        try:
            async with engine.connect() as conn:
                await conn.execute(text("SELECT 1"))
        except Exception:
            pass  # Silently ignore connection errors
        await asyncio.sleep(60)  # Ping every 60 seconds


async def cleanup_idle_conversations():
    """Background task to close idle conversations (TTL: 30 min)."""
    import logging

    logger = logging.getLogger("ai.cleanup")
    while True:
        await asyncio.sleep(300)  # Run every 5 minutes
        try:
            from src.services.conversation import ConversationService

            async with async_session_factory() as session:
                service = ConversationService(session)
                closed = await service.cleanup_idle_conversations(idle_minutes=30)
                if closed > 0:
                    logger.info("Closed %d idle conversations", closed)
                    await session.commit()
        except Exception:
            pass  # Non-critical background task


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    # Startup
    await init_db()
    # Seed default categories
    async with async_session_factory() as session:
        await seed_categories(session)
    # Start background tasks
    warmup_task = asyncio.create_task(keep_db_warm())
    cleanup_task = asyncio.create_task(cleanup_idle_conversations())
    yield
    # Shutdown
    warmup_task.cancel()
    cleanup_task.cancel()
    try:
        await warmup_task
    except asyncio.CancelledError:
        pass
    try:
        await cleanup_task
    except asyncio.CancelledError:
        pass


# Create FastAPI application
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="AI-powered personal finance tracking and spending analysis",
    lifespan=lifespan,
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
)

# Add rate limiter
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Health check endpoints
@app.get("/health", tags=["Health"])
async def health_check():
    """Basic health check."""
    return {"status": "healthy", "version": settings.app_version}


@app.get("/health/ready", tags=["Health"])
async def readiness_check():
    """Readiness check including database connectivity."""
    from sqlalchemy import text
    from src.db.session import engine

    try:
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        return {"status": "ready", "database": "connected"}
    except Exception as e:
        return JSONResponse(
            status_code=503,
            content={"status": "not ready", "database": str(e)},
        )


# Include API v1 router
app.include_router(api_router, prefix="/api/v1")


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Handle unexpected exceptions."""
    return JSONResponse(
        status_code=500,
        content={
            "detail": "An unexpected error occurred",
            "type": type(exc).__name__,
        },
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "src.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug,
    )
