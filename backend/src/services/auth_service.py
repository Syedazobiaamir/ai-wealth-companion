"""Authentication service for user management and token handling."""

import secrets
from datetime import datetime, timedelta
from typing import Optional, Tuple
from uuid import UUID

from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from src.core.config import get_settings
from src.core.security import (
    create_access_token,
    create_refresh_token,
    hash_password,
    verify_password,
    verify_token,
)
from src.models.user import User, UserCreate, UserRead

settings = get_settings()


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

    async def create_password_reset_token(self, email: str) -> Optional[str]:
        """
        Create a password reset token for a user.

        Args:
            email: User's email address

        Returns:
            Reset token if user exists, None otherwise
        """
        user = await self.get_user_by_email(email)
        if not user:
            return None

        # Generate secure random token
        token = secrets.token_urlsafe(32)

        # Set token and expiration
        user.password_reset_token = token
        user.password_reset_expires = datetime.utcnow() + timedelta(
            minutes=settings.password_reset_expire_minutes
        )

        await self.session.commit()
        return token

    async def verify_password_reset_token(self, token: str) -> Optional[User]:
        """
        Verify a password reset token and return the user.

        Args:
            token: Password reset token

        Returns:
            User if token is valid and not expired, None otherwise
        """
        statement = select(User).where(User.password_reset_token == token)
        result = await self.session.execute(statement)
        user = result.scalar_one_or_none()

        if not user:
            return None

        # Check if token is expired
        if user.password_reset_expires and user.password_reset_expires < datetime.utcnow():
            return None

        return user

    async def reset_password(self, token: str, new_password: str) -> Optional[User]:
        """
        Reset user's password using a valid reset token.

        Args:
            token: Password reset token
            new_password: New password to set

        Returns:
            User if password was reset successfully, None otherwise
        """
        user = await self.verify_password_reset_token(token)
        if not user:
            return None

        # Update password and clear reset token
        user.password_hash = hash_password(new_password)
        user.password_reset_token = None
        user.password_reset_expires = None
        user.updated_at = datetime.utcnow()

        await self.session.commit()
        await self.session.refresh(user)
        return user


class TokenResponse:
    """Token response data."""

    def __init__(self, access_token: str, token_type: str = "Bearer", expires_in: int = 3600):
        self.access_token = access_token
        self.token_type = token_type
        self.expires_in = expires_in
