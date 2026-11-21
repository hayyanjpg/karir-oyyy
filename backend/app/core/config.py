from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

PROJECT_ROOT = Path(__file__).resolve().parents[3]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=PROJECT_ROOT / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    app_env: str = "development"

    database_url: str = "postgresql+psycopg://postgres:postgres@localhost:5432/karirtrack"
    database_url_direct: str | None = None

    jwt_secret_key: str = Field(default="dev-only-change-me-please-32-chars!!", min_length=32)
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 15
    refresh_token_expire_days: int = 7

    google_client_id: str = ""

    cors_origins: str = "http://localhost:5173"
    frontend_url: str = "http://localhost:5173"

    cookie_secure: bool = False
    cookie_samesite: Literal["lax", "strict", "none"] = "lax"
    cookie_domain: str | None = None
    cookie_path: str = "/api/v1/auth"

    max_export_rows: int = 2000

    @field_validator("database_url_direct", "cookie_domain", mode="before")
    @classmethod
    def empty_string_to_none(cls, value: object) -> object:
        if isinstance(value, str) and not value.strip():
            return None
        return value

    @property
    def cors_origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]

    @property
    def is_production(self) -> bool:
        return self.app_env.lower() == "production"

    @property
    def migration_database_url(self) -> str:
        return self.database_url_direct or self.database_url


@lru_cache
def get_settings() -> Settings:
    return Settings()
