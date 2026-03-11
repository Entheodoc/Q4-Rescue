import sqlite3
from pathlib import Path

# SQLite file lives at the project root beside pyproject.toml
DB_PATH = Path(__file__).resolve().parents[2] / "q4_rescue.sqlite3"
SCHEMA_PATH = Path(__file__).resolve().parent / "schema.sql"


def get_conn() -> sqlite3.Connection:
    """
    Returns a SQLite connection with Row factory enabled.
    """
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    """
    Initializes database schema.
    """
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)

    with get_conn() as conn:
        conn.executescript(SCHEMA_PATH.read_text(encoding="utf-8"))
