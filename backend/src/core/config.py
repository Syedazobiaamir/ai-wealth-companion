"""Application configuration using Pydantic Settings."""

from functools import lru_cache
from typing import List

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # Application
    app_name: str = "AI Wealth & Spending Companion"
    app_version: str = "2.0.0"
    debug: bool = False

    # Database
    database_url: str = "postgresql+asyncpg://user:password@localhost:5432/finance"

    # CORS (comma-separated string in env, converted to list)
    cors_origins: str = "http://localhost:3000"

    @property
    def cors_origins_list(self) -> List[str]:
        """Parse CORS origins as a list."""
        return [origin.strip() for origin in self.cors_origins.split(",")]

    # JWT Authentication
    jwt_secret_key: str = "your-super-secret-key-change-in-production"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60  # 1 hour
    refresh_token_expire_days: int = 7  # 7 days

    # AI Providers (Gemini takes priority over OpenAI)
    gemini_api_key: str = ""
    openai_api_key: str = ""
    openai_model: str = "gpt-4"

    # Rate limiting
    rate_limit_requests: int = 100
    rate_limit_period: int = 60  # seconds
    auth_rate_limit: str = "5/minute"
    write_rate_limit: str = "30/minute"
    read_rate_limit: str = "100/minute"
    ai_rate_limit: str = "10/minute"

    @property
    def async_database_url(self) -> str:
        """Ensure database URL uses asyncpg driver and proper SSL params."""
        url = self.database_url
        if url.startswith("postgresql://"):
            url = url.replace("postgresql://", "postgresql+asyncpg://", 1)
        # asyncpg uses 'ssl' instead of 'sslmode'
        url = url.replace("sslmode=require", "ssl=require")
        url = url.replace("sslmode=disable", "ssl=disable")
        # Remove channel_binding param not supported by asyncpg
        if "channel_binding=" in url:
            import re
            url = re.sub(r"[&?]channel_binding=[^&]*", "", url)
        return url


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
