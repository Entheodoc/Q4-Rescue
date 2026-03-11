import json
import os
import sqlite3
from pathlib import Path
from uuid import NAMESPACE_URL, uuid5


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
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def _table_exists(conn: sqlite3.Connection, table_name: str) -> bool:
    row = conn.execute(
        "SELECT 1 FROM sqlite_master WHERE type = 'table' AND name = ?",
        (table_name,),
    ).fetchone()
    return row is not None


def _table_columns(conn: sqlite3.Connection, table_name: str) -> set[str]:
    return {
        row["name"]
        for row in conn.execute(f"PRAGMA table_info({table_name})").fetchall()
    }


def _stable_uuid(kind: str, value: str) -> str:
    return str(uuid5(NAMESPACE_URL, f"q4-rescue:{kind}:{value}"))


def _rename_legacy_case_tables(conn: sqlite3.Connection) -> None:
    if _table_exists(conn, "measure_cases") and not _table_exists(conn, "legacy_measure_cases"):
        conn.execute("ALTER TABLE measure_cases RENAME TO legacy_measure_cases")

    if _table_exists(conn, "cases"):
        case_columns = _table_columns(conn, "cases")
        if "measure_type" in case_columns and "referral_id" not in case_columns:
            if not _table_exists(conn, "legacy_cases"):
                conn.execute("ALTER TABLE cases RENAME TO legacy_cases")


def _insert_legacy_case_graph(
    conn: sqlite3.Connection,
    *,
    legacy_case_id: str,
    legacy_member_id: str,
    measure_type: str,
    year: int,
    current_pdc: float,
    target_pdc: float,
    status: str,
    created_at: str,
    updated_at: str,
) -> None:
    member_id = _stable_uuid("legacy-member", legacy_member_id)
    referral_id = _stable_uuid("legacy-referral", legacy_case_id)
    case_id = _stable_uuid("legacy-case", legacy_case_id)
    measure_id = _stable_uuid("legacy-measure", legacy_case_id)

    conn.execute(
        """
        INSERT OR IGNORE INTO members (
            id,
            health_plan_member_id,
            first_name,
            last_name,
            birth_date,
            sex,
            phone_number,
            preferred_contact_method,
            preferred_language,
            supported_languages,
            address_line_1,
            address_line_2,
            city,
            state,
            zip,
            pbp,
            low_income_subsidy_level,
            active_status,
            created_at,
            updated_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            member_id,
            legacy_member_id,
            "Legacy",
            "Member",
            None,
            None,
            None,
            None,
            None,
            json.dumps([]),
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            created_at,
            updated_at,
        ),
    )

    conn.execute(
        """
        INSERT OR IGNORE INTO referrals (
            id,
            member_id,
            case_id,
            received_at,
            referral_source,
            source_record_id,
            referral_reason,
            referral_notes,
            snapshot_health_plan_member_id,
            snapshot_first_name,
            snapshot_last_name,
            snapshot_birth_date,
            snapshot_phone_number,
            snapshot_preferred_language,
            snapshot_supported_languages,
            snapshot_address_line_1,
            snapshot_address_line_2,
            snapshot_city,
            snapshot_state,
            snapshot_zip,
            snapshot_pbp,
            snapshot_low_income_subsidy_level,
            snapshot_active_status,
            created_at,
            updated_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            referral_id,
            member_id,
            None,
            created_at,
            "legacy_case_migration",
            legacy_case_id,
            "Migrated from legacy MeasureCase",
            None,
            legacy_member_id,
            "Legacy",
            "Member",
            None,
            None,
            None,
            json.dumps([]),
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            created_at,
            updated_at,
        ),
    )

    closed_at = updated_at if status in {"closed", "archived"} else None
    archived_at = updated_at if status == "archived" else None
    closed_reason = "legacy_case_migration" if status in {"closed", "archived"} else None

    conn.execute(
        """
        INSERT OR IGNORE INTO cases (
            id,
            member_id,
            referral_id,
            status,
            opened_at,
            closed_at,
            archived_at,
            closed_reason,
            case_summary,
            priority,
            created_at,
            updated_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            case_id,
            member_id,
            referral_id,
            status,
            created_at,
            closed_at,
            archived_at,
            closed_reason,
            "Migrated legacy case",
            None,
            created_at,
            updated_at,
        ),
    )

    conn.execute(
        """
        UPDATE referrals
        SET case_id = ?,
            updated_at = ?
        WHERE id = ?
        """,
        (case_id, updated_at, referral_id),
    )

    conn.execute(
        """
        INSERT OR IGNORE INTO measures (
            id,
            case_id,
            measure_code,
            measure_name,
            performance_year,
            pdc,
            status,
            actionable_status,
            identified_at,
            opened_at,
            closed_at,
            closure_reason,
            critical_by_date,
            target_threshold,
            source_system,
            source_measure_id,
            created_at,
            updated_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            measure_id,
            case_id,
            measure_type,
            measure_type.title(),
            year,
            current_pdc,
            status,
            None,
            created_at,
            created_at,
            closed_at,
            closed_reason,
            None,
            target_pdc,
            "legacy_case_migration",
            legacy_case_id,
            created_at,
            updated_at,
        ),
    )


def _migrate_legacy_cases(conn: sqlite3.Connection) -> None:
    for table_name in ("legacy_measure_cases", "legacy_cases"):
        if not _table_exists(conn, table_name):
            continue

        rows = conn.execute(f"SELECT * FROM {table_name}").fetchall()
        for row in rows:
            _insert_legacy_case_graph(
                conn,
                legacy_case_id=row["id"],
                legacy_member_id=row["member_id"],
                measure_type=row["measure_type"],
                year=row["year"],
                current_pdc=row["current_pdc"],
                target_pdc=row["target_pdc"],
                status=row["status"],
                created_at=row["created_at"],
                updated_at=row["updated_at"],
            )

        conn.execute(f"DROP TABLE {table_name}")


def init_db() -> None:
    """
    Initializes database schema.
    """
    db_path = get_db_path()
    db_path.parent.mkdir(parents=True, exist_ok=True)

    conn = get_conn()
    try:
        _rename_legacy_case_tables(conn)
        conn.executescript(get_schema_path().read_text(encoding="utf-8"))
        _migrate_legacy_cases(conn)
        conn.commit()
    finally:
        conn.close()
