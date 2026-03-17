from app.persistence.connection import DatabaseConnection
from app.persistence.migrations import upgrade_database
from app.settings import get_settings, validate_runtime_settings


def get_conn() -> DatabaseConnection:
    """Returns a Postgres database connection wrapper for the configured backend."""
    validate_runtime_settings()
    settings = get_settings()
    return DatabaseConnection.connect_postgres(settings.database_url or "")


def init_db() -> None:
    """
    Initializes database schema.
    """
    validate_runtime_settings()
    settings = get_settings()
    upgrade_database(settings.sqlalchemy_database_url)
