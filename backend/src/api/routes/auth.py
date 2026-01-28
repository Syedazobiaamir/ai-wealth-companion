"""Authentication API routes."""

from datetime import datetime
from typing import Annotated, Any

from fastapi import APIRouter, Cookie, Depends, HTTPException, Request, Response, status
from pydantic import BaseModel
from slowapi import Limiter
from slowapi.util import get_remote_address
from sqlmodel.ext.asyncio.session import AsyncSession

from src.api.deps import CurrentUser, get_auth_service, get_db
from src.core.config import get_settings
from src.models.user import UserCreate, UserLogin, UserRead
from src.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["Authentication"])
settings = get_settings()
limiter = Limiter(key_func=get_remote_address)


class TokenResponse(BaseModel):
    """Token response schema."""

    access_token: str
    token_type: str = "Bearer"
    expires_in: int


class AuthResponse(BaseModel):
    """Authentication response with user and tokens."""

    success: bool = True
    data: dict[str, Any]
    meta: dict[str, Any]


class MessageResponse(BaseModel):
    """Simple message response."""

    success: bool = True
    data: dict[str, str]


@router.post("/register", status_code=status.HTTP_201_CREATED, response_model=AuthResponse)
@limiter.limit(settings.auth_rate_limit)
async def register(
    request: Request,
    user_data: UserCreate,
    response: Response,
    session: Annotated[AsyncSession, Depends(get_db)],
) -> AuthResponse:
    """Register a new user account."""
    auth_service = AuthService(session)

    try:
        user = await auth_service.create_user(user_data)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )

    access_token, refresh_token = auth_service.create_tokens(user)

    # Set refresh token as httpOnly cookie
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=True,
        samesite="lax",
        max_age=settings.refresh_token_expire_days * 24 * 60 * 60,
        path="/api/v1/auth",
    )

    return AuthResponse(
        data={
            "user": UserRead.model_validate(user).model_dump(),
            "tokens": {
                "access_token": access_token,
                "token_type": "Bearer",
                "expires_in": settings.access_token_expire_minutes * 60,
            },
        },
        meta={
            "request_id": f"req_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}",
            "timestamp": datetime.utcnow().isoformat() + "Z",
        },
    )


@router.post("/login", response_model=AuthResponse)
@limiter.limit(settings.auth_rate_limit)
async def login(
    request: Request,
    credentials: UserLogin,
    response: Response,
    session: Annotated[AsyncSession, Depends(get_db)],
) -> AuthResponse:
    """Authenticate user and receive tokens."""
    auth_service = AuthService(session)

    user = await auth_service.authenticate_user(
        email=credentials.email,
        password=credentials.password,
    )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token, refresh_token = auth_service.create_tokens(user)

    # Set refresh token as httpOnly cookie
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=True,
        samesite="lax",
        max_age=settings.refresh_token_expire_days * 24 * 60 * 60,
        path="/api/v1/auth",
    )

    return AuthResponse(
        data={
            "user": {
                "id": str(user.id),
                "email": user.email,
                "display_name": user.display_name,
                "last_login_at": user.last_login_at.isoformat() + "Z" if user.last_login_at else None,
            },
            "tokens": {
                "access_token": access_token,
                "token_type": "Bearer",
                "expires_in": settings.access_token_expire_minutes * 60,
            },
        },
        meta={
            "request_id": f"req_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}",
        },
    )


@router.post("/refresh", response_model=AuthResponse)
@limiter.limit("10/minute")
async def refresh_token(
    request: Request,
    response: Response,
    session: Annotated[AsyncSession, Depends(get_db)],
    refresh_token: Annotated[str | None, Cookie()] = None,
) -> AuthResponse:
    """Refresh access token using refresh token cookie."""
    if not refresh_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token missing",
        )

    auth_service = AuthService(session)
    tokens = await auth_service.refresh_access_token(refresh_token)

    if not tokens:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token",
        )

    new_access_token, new_refresh_token = tokens

    # Set new refresh token as httpOnly cookie (token rotation)
    response.set_cookie(
        key="refresh_token",
        value=new_refresh_token,
        httponly=True,
        secure=True,
        samesite="lax",
        max_age=settings.refresh_token_expire_days * 24 * 60 * 60,
        path="/api/v1/auth",
    )

    return AuthResponse(
        data={
            "access_token": new_access_token,
            "token_type": "Bearer",
            "expires_in": settings.access_token_expire_minutes * 60,
        },
        meta={},
    )


@router.post("/logout", response_model=MessageResponse)
async def logout(
    response: Response,
    current_user: CurrentUser,
) -> MessageResponse:
    """Invalidate refresh token and clear cookie."""
    # Clear the refresh token cookie
    response.delete_cookie(
        key="refresh_token",
        path="/api/v1/auth",
    )

    return MessageResponse(
        data={"message": "Logged out successfully"},
    )


@router.get("/me", response_model=AuthResponse)
async def get_current_user_profile(
    current_user: CurrentUser,
) -> AuthResponse:
    """Get current authenticated user profile."""
    return AuthResponse(
        data=UserRead.model_validate(current_user).model_dump(),
        meta={},
    )
