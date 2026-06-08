"""Application configuration loaded from environment variables.

Uses ``pydantic-settings`` so configuration is type-checked and documented in
one place. No secrets are hardcoded; values come from the environment or a
local ``.env`` file (see ``.env.example``).
"""

from __future__ import annotations

from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Strongly-typed application settings."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # --- App metadata ---
    app_name: str = Field(default="RightsAI Nigeria")
    app_version: str = Field(default="0.1.0")
    environment: str = Field(default="development")
    log_level: str = Field(default="INFO")

    # --- API / CORS ---
    cors_origins: str = Field(
        default="*",
        description="Comma-separated list of allowed CORS origins, or '*'.",
    )

    # --- OpenAI / LLM ---
    openai_api_key: str | None = Field(default=None)
    openai_model: str = Field(default="gpt-4o-mini")
    openai_timeout_seconds: float = Field(default=30.0)
    openai_max_retries: int = Field(default=2)

    # --- Database / pgvector (placeholders for future RAG integration) ---
    database_url: str | None = Field(
        default=None,
        description="PostgreSQL DSN (e.g. postgresql+asyncpg://...).",
    )

    @property
    def llm_configured(self) -> bool:
        """Whether an OpenAI API key is present."""
        return bool(self.openai_api_key)

    @property
    def cors_origin_list(self) -> list[str]:
        """Parse ``cors_origins`` into a list."""
        raw = self.cors_origins.strip()
        if raw == "*" or not raw:
            return ["*"]
        return [origin.strip() for origin in raw.split(",") if origin.strip()]


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return a cached :class:`Settings` instance."""
    return Settings()
