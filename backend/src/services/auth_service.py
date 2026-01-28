"""Authentication service for user management and token handling."""

from datetime import datetime
from typing import Optional, Tuple
from uuid import UUID

from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from src.core.security import (
    create_access_token,
    create_refresh_token,
    hash_password,
    verify_password,
    verify_token,
)
from src.models.user import User, UserCreate, UserRead


class AuthService:
    """Service for authentication operations."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_user_by_email(self, email: str) -> Optional[User]:
        """Get a user by email."""
        statement = select(User).where(User.email == email)
        result = await self.session.execute(statement)
        return result.scalar_one_or_none()

    async def get_user_by_id(self, user_id: UUID) -> Optional[User]:
        """Get a user by ID."""
        statement = select(User).where(User.id == user_id)
        result = await self.session.execute(statement)
        return result.scalar_one_or_none()

    async def create_user(self, user_data: UserCreate) -> User:
        """Create a new user with hashed password."""
        # Check if user already exists
        existing_user = await self.get_user_by_email(user_data.email)
        if existing_user:
            raise ValueError("User with this email already exists")

        # Create user with hashed password
        user = User(
            email=user_data.email,
            password_hash=hash_password(user_data.password),
            display_name=user_data.display_name,
            preferred_currency=user_data.preferred_currency,
            preferred_locale=user_data.preferred_locale,
        )

        self.session.add(user)
        await self.session.commit()
        await self.session.refresh(user)
        return user

    async def authenticate_user(self, email: str, password: str) -> Optional[User]:
        """Authenticate a user with email and password."""
        user = await self.get_user_by_email(email)
        if not user:
            return None

        if not user.is_active:
            return None

        if not verify_password(password, user.password_hash):
            return None

        # Update last login timestamp
        user.last_login_at = datetime.utcnow()
        await self.session.commit()

        return user

    def create_tokens(self, user: User) -> Tuple[str, str]:
        """Create access and refresh tokens for a user."""
        access_token = create_access_token(
            subject=user.id,
            extra_claims={"email": user.email},
        )
        refresh_token = create_refresh_token(subject=user.id)
        return access_token, refresh_token

    async def refresh_access_token(self, refresh_token: str) -> Optional[Tuple[str, str]]:
        """Refresh access token using refresh token."""
        user_id_str = verify_token(refresh_token, token_type="refresh")
        if not user_id_str:
            return None

        try:
            user_id = UUID(user_id_str)
        except ValueError:
            return None

        user = await self.get_user_by_id(user_id)
        if not user or not user.is_active:
            return None

        # Create new tokens (token rotation)
        return self.create_tokens(user)

    async def get_current_user_from_token(self, token: str) -> Optional[User]:
        """Get user from access token."""
        user_id_str = verify_token(token, token_type="access")
        if not user_id_str:
            return None

        try:
            user_id = UUID(user_id_str)
        except ValueError:
            return None

        return await self.get_user_by_id(user_id)


class TokenResponse:
    """Token response data."""

    def __init__(self, access_token: str, token_type: str = "Bearer", expires_in: int = 3600):
        self.access_token = access_token
        self.token_type = token_type
        self.expires_in = expires_in
