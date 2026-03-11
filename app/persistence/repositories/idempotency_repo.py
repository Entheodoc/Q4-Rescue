import sqlite3
import json
from typing import Optional


class IdempotencyRepository:
    def __init__(self, conn: sqlite3.Connection):
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
            INSERT INTO idempotency_keys (route, key, response)
            VALUES (?, ?, ?)
            """,
            (route, key, json.dumps(response)),
        )
        self.conn.commit()
