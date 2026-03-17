import json
from datetime import datetime, timezone
from typing import Optional

from app.persistence.connection import DatabaseConnection


class IdempotencyRepository:
    def __init__(self, conn: DatabaseConnection):
        self.conn = conn

    # ---------------------------------------------------------
    # GET
    # ---------------------------------------------------------

    def get(self, route: str, key: str) -> Optional[dict]:
        cursor = self.conn.cursor()
        cursor.execute(
            """
            SELECT response
            FROM idempotency_keys
            WHERE route = ?
              AND key = ?
            """,
            (route, key),
        )
        row = cursor.fetchone()
        if not row:
            return None

        return json.loads(row["response"])

    # ---------------------------------------------------------
    # SAVE
    # ---------------------------------------------------------

    def save(self, route: str, key: str, response: dict) -> None:
        cursor = self.conn.cursor()
        cursor.execute(
            """
            INSERT INTO idempotency_keys (route, key, response, created_at)
            VALUES (?, ?, ?, ?)
            """,
            (route, key, json.dumps(response), datetime.now(timezone.utc).isoformat()),
        )
        self.conn.commit()
