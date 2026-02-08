"""OAuth authentication routes for Google and GitHub."""

import secrets
from datetime import datetime
from typing import Optional
from urllib.parse import urlencode

import httpx
from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import RedirectResponse
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from src.api.deps import get_db
from src.core.config import get_settings
from src.core.security import create_access_token, create_refresh_token
from src.models.user import User

router = APIRouter(prefix="/auth/oauth", tags=["OAuth"])
settings = get_settings()

# OAuth state storage (in production, use Redis or database)
oauth_states: dict[str, dict] = {}


# ── Google OAuth ──────────────────────────────────────────────────────


@router.get("/google")
async def google_oauth_redirect():
    """Redirect to Google OAuth consent screen."""
    if not settings.google_client_id:
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="Google OAuth not configured",
        )

    state = secrets.token_urlsafe(32)
    oauth_states[state] = {"provider": "google", "created_at": datetime.utcnow()}

    params = {
        "client_id": settings.google_client_id,
        "redirect_uri": f"{settings.oauth_redirect_base}/api/v1/auth/oauth/google/callback",
        "response_type": "code",
        "scope": "openid email profile",
        "state": state,
        "access_type": "offline",
        "prompt": "consent",
    }

    google_auth_url = f"https://accounts.google.com/o/oauth2/v2/auth?{urlencode(params)}"
    return RedirectResponse(url=google_auth_url)


@router.get("/google/callback")
async def google_oauth_callback(
    code: str = Query(...),
    state: str = Query(...),
    session: AsyncSession = Depends(get_db),
):
    """Handle Google OAuth callback."""
    # Verify state
    if state not in oauth_states or oauth_states[state]["provider"] != "google":
        raise HTTPException(status_code=400, detail="Invalid OAuth state")

    del oauth_states[state]

    # Exchange code for tokens
    async with httpx.AsyncClient() as client:
        token_response = await client.post(
            "https://oauth2.googleapis.com/token",
            data={
                "client_id": settings.google_client_id,
                "client_secret": settings.google_client_secret,
                "code": code,
                "grant_type": "authorization_code",
                "redirect_uri": f"{settings.oauth_redirect_base}/api/v1/auth/oauth/google/callback",
            },
        )

        if token_response.status_code != 200:
            raise HTTPException(status_code=400, detail="Failed to exchange code for token")

        tokens = token_response.json()
        access_token = tokens["access_token"]

        # Get user info
        user_response = await client.get(
            "https://www.googleapis.com/oauth2/v2/userinfo",
            headers={"Authorization": f"Bearer {access_token}"},
        )

        if user_response.status_code != 200:
            raise HTTPException(status_code=400, detail="Failed to get user info")

        user_info = user_response.json()

    # Find or create user
    email = user_info["email"]
    stmt = select(User).where(User.email == email)
    result = await session.execute(stmt)
    user = result.scalar_one_or_none()

    if not user:
        # Create new user
        user = User(
            email=email,
            password_hash="",  # OAuth users have no password
            display_name=user_info.get("name", email.split("@")[0]),
            preferred_currency="PKR",
            preferred_locale="en",
            oauth_provider="google",
            oauth_provider_id=user_info.get("id"),
        )
        session.add(user)
        await session.commit()
        await session.refresh(user)
    else:
        # Update last login
        user.last_login_at = datetime.utcnow()
        await session.commit()

    # Create tokens
    access_token = create_access_token(subject=user.id, extra_claims={"email": user.email})
    refresh_token = create_refresh_token(subject=user.id)

    # Redirect to frontend with tokens
    frontend_url = settings.oauth_redirect_base
    redirect_url = f"{frontend_url}/auth/callback?access_token={access_token}&provider=google"

    response = RedirectResponse(url=redirect_url)
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=True,
        samesite="lax",
        max_age=settings.refresh_token_expire_days * 24 * 60 * 60,
        path="/api/v1/auth",
    )

    return response


# ── GitHub OAuth ──────────────────────────────────────────────────────


@router.get("/github")
async def github_oauth_redirect():
    """Redirect to GitHub OAuth consent screen."""
    if not settings.github_client_id:
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="GitHub OAuth not configured",
        )

    state = secrets.token_urlsafe(32)
    oauth_states[state] = {"provider": "github", "created_at": datetime.utcnow()}

    params = {
        "client_id": settings.github_client_id,
        "redirect_uri": f"{settings.oauth_redirect_base}/api/v1/auth/oauth/github/callback",
        "scope": "user:email",
        "state": state,
    }

    github_auth_url = f"https://github.com/login/oauth/authorize?{urlencode(params)}"
    return RedirectResponse(url=github_auth_url)


@router.get("/github/callback")
async def github_oauth_callback(
    code: str = Query(...),
    state: str = Query(...),
    session: AsyncSession = Depends(get_db),
):
    """Handle GitHub OAuth callback."""
    # Verify state
    if state not in oauth_states or oauth_states[state]["provider"] != "github":
        raise HTTPException(status_code=400, detail="Invalid OAuth state")

    del oauth_states[state]

    # Exchange code for tokens
    async with httpx.AsyncClient() as client:
        token_response = await client.post(
            "https://github.com/login/oauth/access_token",
            data={
                "client_id": settings.github_client_id,
                "client_secret": settings.github_client_secret,
                "code": code,
            },
            headers={"Accept": "application/json"},
        )

        if token_response.status_code != 200:
            raise HTTPException(status_code=400, detail="Failed to exchange code for token")

        tokens = token_response.json()
        access_token = tokens.get("access_token")

        if not access_token:
            raise HTTPException(status_code=400, detail="No access token received")

        # Get user info
        user_response = await client.get(
            "https://api.github.com/user",
            headers={
                "Authorization": f"Bearer {access_token}",
                "Accept": "application/vnd.github.v3+json",
            },
        )

        if user_response.status_code != 200:
            raise HTTPException(status_code=400, detail="Failed to get user info")

        user_info = user_response.json()

        # Get user email (may need separate request if email is private)
        email = user_info.get("email")
        if not email:
            email_response = await client.get(
                "https://api.github.com/user/emails",
                headers={
                    "Authorization": f"Bearer {access_token}",
                    "Accept": "application/vnd.github.v3+json",
                },
            )
            if email_response.status_code == 200:
                emails = email_response.json()
                primary_email = next(
                    (e for e in emails if e.get("primary") and e.get("verified")),
                    None,
                )
                if primary_email:
                    email = primary_email["email"]

        if not email:
            raise HTTPException(status_code=400, detail="Could not get email from GitHub")

    # Find or create user
    stmt = select(User).where(User.email == email)
    result = await session.execute(stmt)
    user = result.scalar_one_or_none()

    if not user:
        # Create new user
        user = User(
            email=email,
            password_hash="",  # OAuth users have no password
            display_name=user_info.get("name") or user_info.get("login", email.split("@")[0]),
            preferred_currency="PKR",
            preferred_locale="en",
            oauth_provider="github",
            oauth_provider_id=str(user_info.get("id")),
        )
        session.add(user)
        await session.commit()
        await session.refresh(user)
    else:
        # Update last login
        user.last_login_at = datetime.utcnow()
        await session.commit()

    # Create tokens
    access_token = create_access_token(subject=user.id, extra_claims={"email": user.email})
    refresh_token = create_refresh_token(subject=user.id)

    # Redirect to frontend with tokens
    frontend_url = settings.oauth_redirect_base
    redirect_url = f"{frontend_url}/auth/callback?access_token={access_token}&provider=github"

    response = RedirectResponse(url=redirect_url)
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=True,
        samesite="lax",
        max_age=settings.refresh_token_expire_days * 24 * 60 * 60,
        path="/api/v1/auth",
    )

    return response
