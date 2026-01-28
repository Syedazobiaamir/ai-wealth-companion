"""Category API endpoints."""

from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.session import get_session
from src.models.category import CategoryRead
from src.services.category import CategoryService

router = APIRouter()


@router.get(
    "",
    response_model=List[CategoryRead],
    summary="List all categories",
    description="Get all predefined transaction categories ordered by name.",
)
async def list_categories(
    session: AsyncSession = Depends(get_session),
) -> List[CategoryRead]:
    """Get all categories."""
    service = CategoryService(session)
    return await service.get_all()


@router.get(
    "/search",
    response_model=List[CategoryRead],
    summary="Search categories",
    description="Search categories by name.",
)
async def search_categories(
    q: str = Query(..., min_length=1, max_length=50, description="Search query"),
    session: AsyncSession = Depends(get_session),
) -> List[CategoryRead]:
    """Search categories by name."""
    service = CategoryService(session)
    return await service.search(q)


@router.get(
    "/{category_id}",
    response_model=CategoryRead,
    summary="Get category by ID",
    description="Get a single category by its UUID.",
)
async def get_category(
    category_id: UUID,
    session: AsyncSession = Depends(get_session),
) -> CategoryRead:
    """Get a category by ID."""
    service = CategoryService(session)
    category = await service.get_by_id(category_id)
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Category with ID {category_id} not found",
        )
    return category
