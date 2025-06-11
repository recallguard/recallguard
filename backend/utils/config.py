"""Application configuration via environment variables (Pydantic v2)."""

from __future__ import annotations
import os, json
from functools import lru_cache

from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import field_validator


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        env_prefix="",        # keep env-vars exactly as written
    )

    # ─── Core ───
    DATABASE_URI: str        # accepts sqlite:///… or postgres://…
    JWT_SECRET: str
    JWT_EXPIRE_MINUTES: int = Field(60, description="Token lifetime in minutes")

    # ─── OpenAI ───
    OPENAI_API_KEY: str | None = None
    OPENAI_COMPLETIONS_MODEL: str = "gpt-4"
    OPENAI_CLASSIFICATION_MODEL: str = "gpt-3.5-turbo"

    # ─── Stripe ───
    STRIPE_SECRET_KEY: str | None = None
    STRIPE_WEBHOOK_SECRET: str | None = None

    # ─── CORS ───
    CORS_ORIGINS: list[str] = Field(
        default_factory=list,
        description="List of allowed origins (can be JSON or comma-separated)",
    )

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def _parse_cors_origins(cls, v):
        # if someone set CORS_ORIGINS='["a","b"]' it'll JSON-decode;
        # else split on commas
        if isinstance(v, str):
            v = v.strip()
            if v.startswith("[") and v.endswith("]"):
                return json.loads(v)
            return [h.strip() for h in v.split(",") if h.strip()]
        return v

    # (you can add more validators here as you add new complex types)


@lru_cache()
def get_settings() -> Settings:
    os.environ.setdefault("ENV_FILE_ENCODING", "utf-8")
    return Settings()
