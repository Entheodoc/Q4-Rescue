from __future__ import annotations

from pathlib import Path

from alembic import command
from alembic.config import Config

from app.settings import get_settings


def get_alembic_ini_path() -> Path:
    return Path(__file__).resolve().parents[2] / "alembic.ini"


def get_migrations_path() -> Path:
    return Path(__file__).resolve().parents[2] / "alembic"


def get_alembic_config(database_url: str | None = None) -> Config:
    settings = get_settings()
    resolved_database_url = database_url or settings.sqlalchemy_database_url
    if not resolved_database_url:
        raise RuntimeError("A database URL is required to run Alembic migrations.")

    config = Config(str(get_alembic_ini_path()))
    config.set_main_option("script_location", str(get_migrations_path()))
    config.set_main_option("sqlalchemy.url", resolved_database_url)
    return config


def upgrade_database(database_url: str | None = None) -> None:
    command.upgrade(get_alembic_config(database_url), "head")
