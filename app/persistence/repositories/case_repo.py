import sqlite3
from datetime import datetime
from uuid import UUID

from app.domain.case import Case, CaseId, CaseStatus


class CaseRepository:
    def __init__(self, conn: sqlite3.Connection):
        self.conn = conn

    def create(self, case: Case) -> None:
        cursor = self.conn.cursor()
        cursor.execute(
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

    def exists_active_case(self, member_id: str, measure_type: str, year: int) -> bool:
        normalized_measure_type = measure_type.strip().upper()
        cursor = self.conn.cursor()
        cursor.execute(
            """
            SELECT 1 FROM cases
            WHERE member_id = ?
              AND measure_type = ?
              AND year = ?
              AND status != 'archived'
            LIMIT 1
            """,
            (member_id, normalized_measure_type, year),
        )
        return cursor.fetchone() is not None

    def list_all(self) -> list[Case]:
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM cases")
        rows = cursor.fetchall()
        return [self._row_to_domain(row) for row in rows]

    def get_by_id(self, case_id: UUID) -> Case | None:
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM cases WHERE id = ?", (str(case_id),))
        row = cursor.fetchone()
        if not row:
            return None
        return self._row_to_domain(row)

    def update(self, case: Case) -> None:
        cursor = self.conn.cursor()
        cursor.execute(
            """
            UPDATE cases
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

    def _row_to_domain(self, row: sqlite3.Row) -> Case:
        return Case(
            id=CaseId(UUID(row["id"])),
            member_id=row["member_id"],
            measure_type=row["measure_type"],
            year=row["year"],
            current_pdc=row["current_pdc"],
            target_pdc=row["target_pdc"],
            status=CaseStatus(row["status"]),
            created_at=datetime.fromisoformat(row["created_at"]),
            updated_at=datetime.fromisoformat(row["updated_at"]),
        )
