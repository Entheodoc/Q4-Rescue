import os
import sqlite3
from pathlib import Path


def get_db_path() -> Path:
    override = os.getenv("Q4_RESCUE_DB_PATH")
    if override:
        return Path(override)
    return Path(__file__).resolve().parents[2] / "q4_rescue.sqlite3"


def get_schema_path() -> Path:
    return Path(__file__).resolve().parent / "schema.sql"


def get_conn() -> sqlite3.Connection:
    """
    Returns a SQLite connection with Row factory enabled.
    """
    conn = sqlite3.connect(get_db_path())
    conn.row_factory = sqlite3.Row
    return conn


def _table_exists(conn: sqlite3.Connection, table_name: str) -> bool:
    row = conn.execute(
        "SELECT 1 FROM sqlite_master WHERE type = 'table' AND name = ?",
        (table_name,),
    ).fetchone()
    return row is not None


def _migrate_legacy_measure_cases(conn: sqlite3.Connection) -> None:
    has_legacy = _table_exists(conn, "measure_cases")
    has_cases = _table_exists(conn, "cases")

    if has_legacy and not has_cases:
        conn.execute("ALTER TABLE measure_cases RENAME TO cases")
        return

    if has_legacy and has_cases:
        conn.execute(
            """
            INSERT INTO cases (
                id,
                member_id,
                measure_type,
                year,
                current_pdc,
                target_pdc,
                status,
                created_at,
                updated_at
            )
            SELECT
                legacy.id,
                legacy.member_id,
                legacy.measure_type,
                legacy.year,
                legacy.current_pdc,
                legacy.target_pdc,
                legacy.status,
                legacy.created_at,
                legacy.updated_at
            FROM measure_cases AS legacy
            WHERE NOT EXISTS (
                SELECT 1 FROM cases AS current WHERE current.id = legacy.id
            )
            """
        )
        conn.execute("DROP TABLE measure_cases")


def init_db() -> None:
    """
    Initializes database schema.
    """
    db_path = get_db_path()
    db_path.parent.mkdir(parents=True, exist_ok=True)

    with get_conn() as conn:
        _migrate_legacy_measure_cases(conn)
        conn.executescript(get_schema_path().read_text(encoding="utf-8"))
