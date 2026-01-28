"""Transaction API endpoints."""

from datetime import date
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.deps import CurrentUser, get_db
from src.models.transaction import (
    TransactionCreate,
    TransactionRead,
    TransactionType,
    TransactionUpdate,
    TransactionWithCategory,
)
from src.services.category import CategoryService
from src.services.transaction import TransactionService

router = APIRouter()


@router.get(
    "",
    response_model=List[TransactionRead],
    summary="List transactions",
    description="Get all transactions with optional filters, sorting, and pagination.",
)
async def list_transactions(
    current_user: CurrentUser,
    start_date: Optional[date] = Query(None, description="Filter by start date"),
    end_date: Optional[date] = Query(None, description="Filter by end date"),
    type: Optional[TransactionType] = Query(None, description="Filter by type"),
    category_id: Optional[UUID] = Query(None, description="Filter by category"),
    wallet_id: Optional[UUID] = Query(None, description="Filter by wallet"),
    sort_by: str = Query("date", description="Sort by field (date, amount, created_at)"),
    sort_order: str = Query("desc", description="Sort order (asc, desc)"),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Max records to return"),
    session: AsyncSession = Depends(get_db),
) -> List[TransactionRead]:
    """Get transactions with optional filters and sorting."""
    service = TransactionService(session)

    # Always use get_by_filters which supports type filtering
    return await service.get_by_filters(
        user_id=current_user.id,
        start_date=start_date,
        end_date=end_date,
        transaction_type=type,
        category_id=category_id,
        wallet_id=wallet_id,
        skip=skip,
        limit=limit,
        sort_by=sort_by,
        sort_order=sort_order,
    )


@router.get(
    "/search",
    response_model=List[TransactionRead],
    summary="Search transactions",
    description="Search transactions by note content.",
)
async def search_transactions(
    current_user: CurrentUser,
    q: str = Query(..., min_length=1, max_length=255, description="Search query"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    session: AsyncSession = Depends(get_db),
) -> List[TransactionRead]:
    """Search transactions by note."""
    service = TransactionService(session)
    return await service.search(current_user.id, q, skip=skip, limit=limit)


@router.get(
    "/{transaction_id}",
    response_model=TransactionWithCategory,
    summary="Get transaction by ID",
    description="Get a single transaction with category details.",
)
async def get_transaction(
    transaction_id: UUID,
    current_user: CurrentUser,
    session: AsyncSession = Depends(get_db),
) -> TransactionWithCategory:
    """Get a transaction by ID with category details."""
    service = TransactionService(session)
    transaction = await service.get_with_category(current_user.id, transaction_id)
    if not transaction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Transaction with ID {transaction_id} not found",
        )
    return transaction


@router.post(
    "",
    response_model=TransactionRead,
    status_code=status.HTTP_201_CREATED,
    summary="Create transaction",
    description="Create a new income or expense transaction.",
)
async def create_transaction(
    data: TransactionCreate,
    current_user: CurrentUser,
    session: AsyncSession = Depends(get_db),
) -> TransactionRead:
    """Create a new transaction."""
    # Validate category exists
    category_service = CategoryService(session)
    if not await category_service.exists(data.category_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Category with ID {data.category_id} not found",
        )

    service = TransactionService(session)
    return await service.create(current_user.id, data)


@router.put(
    "/{transaction_id}",
    response_model=TransactionRead,
    summary="Update transaction",
    description="Update an existing transaction.",
)
async def update_transaction(
    transaction_id: UUID,
    data: TransactionUpdate,
    current_user: CurrentUser,
    session: AsyncSession = Depends(get_db),
) -> TransactionRead:
    """Update a transaction."""
    # Validate category if being updated
    if data.category_id:
        category_service = CategoryService(session)
        if not await category_service.exists(data.category_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Category with ID {data.category_id} not found",
            )

    service = TransactionService(session)
    transaction = await service.update(current_user.id, transaction_id, data)
    if not transaction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Transaction with ID {transaction_id} not found",
        )
    return transaction


@router.delete(
    "/{transaction_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete transaction",
    description="Soft delete a transaction.",
)
async def delete_transaction(
    transaction_id: UUID,
    current_user: CurrentUser,
    session: AsyncSession = Depends(get_db),
) -> None:
    """Soft delete a transaction."""
    service = TransactionService(session)
    deleted = await service.delete(current_user.id, transaction_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Transaction with ID {transaction_id} not found",
        )


@router.post(
    "/{transaction_id}/restore",
    response_model=TransactionRead,
    summary="Restore transaction",
    description="Restore a soft-deleted transaction.",
)
async def restore_transaction(
    transaction_id: UUID,
    current_user: CurrentUser,
    session: AsyncSession = Depends(get_db),
) -> TransactionRead:
    """Restore a soft-deleted transaction."""
    service = TransactionService(session)
    transaction = await service.restore(current_user.id, transaction_id)
    if not transaction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Transaction with ID {transaction_id} not found or not deleted",
        )
    return transaction
