"""User model for authentication and preferences."""

from datetime import datetime
from enum import Enum
from typing import Optional
from uuid import UUID, uuid4

from pydantic import EmailStr
from sqlmodel import Field, SQLModel


class ThemePreference(str, Enum):
    """User theme preference enumeration."""

    light = "light"
    dark = "dark"
    system = "system"


class UserBase(SQLModel):
    """Base user schema with common fields."""

    email: EmailStr = Field(index=True, unique=True)
    display_name: Optional[str] = Field(default=None, max_length=100)
    preferred_currency: str = Field(default="PKR", max_length=3)
    preferred_locale: str = Field(default="en", max_length=10)
    theme_preference: ThemePreference = Field(default=ThemePreference.system)
    timezone: str = Field(default="UTC", max_length=50)


class User(UserBase, table=True):
    """User database model for authentication and preferences."""

    __tablename__ = "users"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    password_hash: str = Field(default="", max_length=255)
    is_active: bool = Field(default=True, index=True)
    is_demo_user: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    last_login_at: Optional[datetime] = Field(default=None)
    # OAuth fields
    oauth_provider: Optional[str] = Field(default=None, max_length=20)
    oauth_provider_id: Optional[str] = Field(default=None, max_length=255)


class UserCreate(SQLModel):
    """User registration schema."""

    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    display_name: Optional[str] = Field(default=None, max_length=100)
    preferred_currency: str = Field(default="PKR", max_length=3)
    preferred_locale: str = Field(default="en", max_length=10)


class UserRead(SQLModel):
    """User response schema (no sensitive data)."""

    id: UUID
    email: EmailStr
    display_name: Optional[str]
    preferred_currency: str
    preferred_locale: str
    theme_preference: ThemePreference
    created_at: datetime
    last_login_at: Optional[datetime]


class UserUpdate(SQLModel):
    """User update schema."""

    display_name: Optional[str] = None
    preferred_currency: Optional[str] = None
    preferred_locale: Optional[str] = None
    theme_preference: Optional[ThemePreference] = None
    timezone: Optional[str] = None


class UserLogin(SQLModel):
    """User login schema."""

    email: EmailStr
    password: str
