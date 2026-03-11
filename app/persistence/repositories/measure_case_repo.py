import sqlite3
from uuid import UUID
from datetime import datetime
from app.domain.measure_case import MeasureCase, MeasureCaseStatus, MeasureCaseId


class MeasureCaseRepository:
    def __init__(self, conn: sqlite3.Connection):
        self.conn = conn

    # ---------------------------------------------------------
    # CREATE
    # ---------------------------------------------------------

    def create(self, case: MeasureCase) -> None:
        cursor = self.conn.cursor()
        cursor.execute(
            """
            INSERT INTO measure_cases (
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
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                str(case.id.value),
                case.member_id,
                case.measure_type,
                case.year,
                case.current_pdc,
                case.target_pdc,
                case.status.value,
                case.created_at.isoformat(),
                case.updated_at.isoformat(),
            ),
        )
        self.conn.commit()

    # ---------------------------------------------------------
    # EXISTS ACTIVE
    # ---------------------------------------------------------

    def exists_active_case(self, member_id: str, measure_type: str, year: int) -> bool:
        cursor = self.conn.cursor()
        cursor.execute(
            """
            SELECT 1 FROM measure_cases
            WHERE member_id = ?
              AND measure_type = ?
              AND year = ?
              AND status != 'archived'
            LIMIT 1
            """,
            (member_id, measure_type, year),
        )
        return cursor.fetchone() is not None

    # ---------------------------------------------------------
    # LIST
    # ---------------------------------------------------------

    def list_all(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM measure_cases")
        rows = cursor.fetchall()
        return [self._row_to_domain(row) for row in rows]

    # ---------------------------------------------------------
    # GET BY ID
    # ---------------------------------------------------------

    def get_by_id(self, case_id: UUID):
        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT * FROM measure_cases WHERE id = ?",
            (str(case_id),),
        )
        row = cursor.fetchone()
        if not row:
            return None
        return self._row_to_domain(row)

    # ---------------------------------------------------------
    # UPDATE
    # ---------------------------------------------------------

    def update(self, case: MeasureCase) -> None:
        cursor = self.conn.cursor()
        cursor.execute(
            """
            UPDATE measure_cases
            SET status = ?,
                updated_at = ?
            WHERE id = ?
            """,
            (
                case.status.value,
                case.updated_at.isoformat(),
                str(case.id.value),
            ),
        )
        self.conn.commit()

    # ---------------------------------------------------------
    # INTERNAL MAPPER
    # ---------------------------------------------------------

    def _row_to_domain(self, row) -> MeasureCase:
        return MeasureCase(
            id=MeasureCaseId(UUID(row["id"])),
            member_id=row["member_id"],
            measure_type=row["measure_type"],
            year=row["year"],
            current_pdc=row["current_pdc"],
            target_pdc=row["target_pdc"],
            status=MeasureCaseStatus(row["status"]),
            created_at=datetime.fromisoformat(row["created_at"]),
            updated_at=datetime.fromisoformat(row["updated_at"]),
        )
