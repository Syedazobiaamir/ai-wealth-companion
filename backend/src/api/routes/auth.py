"""Authentication API routes."""

from datetime import datetime
from typing import Annotated, Any

from fastapi import APIRouter, Cookie, Depends, HTTPException, Request, Response, status
from pydantic import BaseModel
from slowapi import Limiter
from slowapi.util import get_remote_address
from sqlmodel.ext.asyncio.session import AsyncSession

from pydantic import EmailStr

from src.api.deps import CurrentUser, get_auth_service, get_db
from src.core.config import get_settings
from src.models.user import UserCreate, UserLogin, UserRead
from src.services.auth_service import AuthService
from src.services.email_service import email_service

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

    # Set refresh token as httpOnly cookie (samesite=none for cross-domain)
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=True,
        samesite="none",
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

    # Set refresh token as httpOnly cookie (samesite=none for cross-domain)
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=True,
        samesite="none",
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

    # Set new refresh token as httpOnly cookie (token rotation, samesite=none for cross-domain)
    response.set_cookie(
        key="refresh_token",
        value=new_refresh_token,
        httponly=True,
        secure=True,
        samesite="none",
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
    # Clear the refresh token cookie (samesite=none for cross-domain)
    response.delete_cookie(
        key="refresh_token",
        path="/api/v1/auth",
        secure=True,
        samesite="none",
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


class ForgotPasswordRequest(BaseModel):
    """Forgot password request schema."""

    email: EmailStr


class ResetPasswordRequest(BaseModel):
    """Reset password request schema."""

    token: str
    password: str


@router.post("/forgot-password", response_model=MessageResponse)
@limiter.limit("3/minute")
async def forgot_password(
    request: Request,
    data: ForgotPasswordRequest,
    session: Annotated[AsyncSession, Depends(get_db)],
) -> MessageResponse:
    """
    Request a password reset email.

    Always returns success to prevent email enumeration attacks.
    """
    auth_service = AuthService(session)

    # Create reset token (returns None if user doesn't exist)
    token = await auth_service.create_password_reset_token(data.email)

    if token:
        # Get user for display name
        user = await auth_service.get_user_by_email(data.email)

        # Send password reset email
        await email_service.send_password_reset_email(
            to_email=data.email,
            reset_token=token,
            user_name=user.display_name if user else None,
        )

    # Always return success to prevent email enumeration
    return MessageResponse(
        data={
            "message": "If an account with that email exists, a password reset link has been sent."
        },
    )


@router.post("/reset-password", response_model=MessageResponse)
@limiter.limit("5/minute")
async def reset_password(
    request: Request,
    data: ResetPasswordRequest,
    session: Annotated[AsyncSession, Depends(get_db)],
) -> MessageResponse:
    """Reset password using a valid reset token."""
    if len(data.password) < 8:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password must be at least 8 characters long",
        )

    auth_service = AuthService(session)
    user = await auth_service.reset_password(data.token, data.password)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired reset token",
        )

    # Send confirmation email
    await email_service.send_password_changed_notification(
        to_email=user.email,
        user_name=user.display_name,
    )

    return MessageResponse(
        data={"message": "Password has been reset successfully. You can now log in."},
    )


@router.get("/verify-reset-token/{token}", response_model=MessageResponse)
async def verify_reset_token(
    token: str,
    session: Annotated[AsyncSession, Depends(get_db)],
) -> MessageResponse:
    """Verify if a password reset token is valid."""
    auth_service = AuthService(session)
    user = await auth_service.verify_password_reset_token(token)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired reset token",
        )

    return MessageResponse(
        data={"message": "Token is valid"},
    )
