from __future__ import annotations

import json
import os

from dotenv import load_dotenv
from pydantic import BaseModel, Field


load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env"))


def _env_bool(name: str, default: bool) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


class AuthTokenSettings(BaseModel):
    subject: str
    permissions: frozenset[str] = Field(default_factory=frozenset)


class Settings(BaseModel):
    environment: str = "development"
    database_url: str | None = None
    auth_enabled: bool = True
    docs_enabled: bool = True
    auth_tokens: dict[str, AuthTokenSettings] = Field(default_factory=dict)
    service_name: str = "q4-rescue-api"
    service_version: str = "0.1.0"
    log_level: str = "INFO"
    metrics_enabled: bool = True
    otel_enabled: bool = True
    otel_exporter_otlp_endpoint: str | None = None
    otel_exporter_otlp_headers: dict[str, str] = Field(default_factory=dict)

    @property
    def is_production(self) -> bool:
        return self.environment.lower() == "production"

    @property
    def sqlalchemy_database_url(self) -> str:
        database_url = (self.database_url or "").strip()
        if not database_url:
            return ""
        if database_url.startswith("postgresql+psycopg://"):
            return database_url
        if database_url.startswith("postgresql://"):
            return database_url.replace("postgresql://", "postgresql+psycopg://", 1)
        if database_url.startswith("postgres://"):
            return database_url.replace("postgres://", "postgresql+psycopg://", 1)
        return database_url


def _load_auth_tokens() -> dict[str, AuthTokenSettings]:
    raw_value = os.getenv("Q4_RESCUE_AUTH_TOKENS")
    if not raw_value:
        return {}

    parsed = json.loads(raw_value)
    auth_tokens: dict[str, AuthTokenSettings] = {}
    for token, config in parsed.items():
        auth_tokens[token] = AuthTokenSettings.model_validate(config)
    return auth_tokens


def _load_string_map(name: str) -> dict[str, str]:
    raw_value = os.getenv(name)
    if not raw_value:
        return {}

    parsed = json.loads(raw_value)
    return {str(key): str(value) for key, value in parsed.items()}


def get_settings() -> Settings:
    environment = os.getenv("Q4_RESCUE_ENV", "development").strip().lower() or "development"
    docs_default = environment != "production"
    log_level_default = "WARNING" if environment == "test" else "INFO"

    return Settings(
        environment=environment,
        database_url=os.getenv("Q4_RESCUE_DATABASE_URL"),
        auth_enabled=_env_bool("Q4_RESCUE_AUTH_ENABLED", True),
        docs_enabled=_env_bool("Q4_RESCUE_DOCS_ENABLED", docs_default),
        auth_tokens=_load_auth_tokens(),
        service_name=os.getenv("Q4_RESCUE_SERVICE_NAME", "q4-rescue-api").strip() or "q4-rescue-api",
        service_version=os.getenv("Q4_RESCUE_SERVICE_VERSION", "0.1.0").strip() or "0.1.0",
        log_level=os.getenv("Q4_RESCUE_LOG_LEVEL", log_level_default).strip() or log_level_default,
        metrics_enabled=_env_bool("Q4_RESCUE_METRICS_ENABLED", True),
        otel_enabled=_env_bool("Q4_RESCUE_OTEL_ENABLED", True),
        otel_exporter_otlp_endpoint=os.getenv("Q4_RESCUE_OTEL_EXPORTER_OTLP_ENDPOINT"),
        otel_exporter_otlp_headers=_load_string_map("Q4_RESCUE_OTEL_EXPORTER_OTLP_HEADERS"),
    )


def validate_runtime_settings() -> None:
    settings = get_settings()

    if not settings.database_url:
        raise RuntimeError("Q4_RESCUE_DATABASE_URL is required.")

    normalized_url = settings.database_url.lower()
    if not normalized_url.startswith(
        ("postgres://", "postgresql://", "postgresql+psycopg://")
    ):
        raise RuntimeError("Q4_RESCUE_DATABASE_URL must be a Postgres connection string.")

    if settings.auth_enabled and not settings.auth_tokens:
        raise RuntimeError(
            "Authentication is enabled, but Q4_RESCUE_AUTH_TOKENS is not configured."
        )
