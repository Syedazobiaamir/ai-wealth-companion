"""API v1 router aggregating all endpoints."""

from fastapi import APIRouter

from src.api.v1.endpoints import (
    categories,
    transactions,
    budgets,
    summary,
    wallets,
    goals,
    tasks,
    dashboard,
    ai,
    demo,
)
from src.api.routes import auth, oauth

api_router = APIRouter()

# Authentication routes (no prefix - already has /auth prefix)
api_router.include_router(auth.router)

# OAuth routes (no prefix - already has /auth/oauth prefix)
api_router.include_router(oauth.router)

api_router.include_router(
    categories.router,
    prefix="/categories",
    tags=["Categories"],
)

api_router.include_router(
    transactions.router,
    prefix="/transactions",
    tags=["Transactions"],
)

api_router.include_router(
    budgets.router,
    prefix="/budgets",
    tags=["Budgets"],
)

api_router.include_router(
    summary.router,
    prefix="/summary",
    tags=["Summary"],
)

api_router.include_router(
    wallets.router,
    prefix="/wallets",
    tags=["Wallets"],
)

api_router.include_router(
    goals.router,
    prefix="/goals",
    tags=["Goals"],
)

api_router.include_router(
    tasks.router,
    prefix="/tasks",
    tags=["Tasks"],
)

api_router.include_router(
    dashboard.router,
    prefix="/dashboard",
    tags=["Dashboard"],
)

api_router.include_router(
    ai.router,
    prefix="/ai",
    tags=["AI"],
)

api_router.include_router(
    demo.router,
    prefix="/demo",
    tags=["Demo"],
)
