"""API dependencies for dependency injection."""

from typing import Annotated, AsyncGenerator, Optional

from fastapi import Cookie, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.security import verify_token
from src.db.session import async_session_factory
from src.models.user import User
from src.services.auth_service import AuthService

# Security scheme for Bearer token
security = HTTPBearer(auto_error=False)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Dependency that provides an async database session."""
    async with async_session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


async def get_auth_service(
    session: Annotated[AsyncSession, Depends(get_db)],
) -> AuthService:
    """Dependency that provides AuthService instance."""
    return AuthService(session)


async def get_current_user(
    credentials: Annotated[Optional[HTTPAuthorizationCredentials], Depends(security)],
    session: Annotated[AsyncSession, Depends(get_db)],
) -> User:
    """Dependency that validates JWT token and returns current user."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    if not credentials:
        raise credentials_exception

    token = credentials.credentials
    user_id_str = verify_token(token, token_type="access")

    if not user_id_str:
        raise credentials_exception

    auth_service = AuthService(session)
    user = await auth_service.get_current_user_from_token(token)

    if not user:
        raise credentials_exception

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive",
        )

    return user


async def get_current_active_user(
    current_user: Annotated[User, Depends(get_current_user)],
) -> User:
    """Dependency that ensures user is active."""
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive",
        )
    return current_user


async def get_optional_current_user(
    credentials: Annotated[Optional[HTTPAuthorizationCredentials], Depends(security)],
    session: Annotated[AsyncSession, Depends(get_db)],
) -> Optional[User]:
    """Dependency that optionally returns current user (for public endpoints)."""
    if not credentials:
        return None

    token = credentials.credentials
    user_id_str = verify_token(token, token_type="access")

    if not user_id_str:
        return None

    auth_service = AuthService(session)
    return await auth_service.get_current_user_from_token(token)


# Type aliases for convenience
DbSession = Annotated[AsyncSession, Depends(get_db)]
CurrentUser = Annotated[User, Depends(get_current_user)]
OptionalUser = Annotated[Optional[User], Depends(get_optional_current_user)]
