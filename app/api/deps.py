from __future__ import annotations

import sqlite3
from collections.abc import Generator

from app.persistence.db import get_conn


def get_db_conn() -> Generator[sqlite3.Connection, None, None]:
    conn = get_conn()
    try:
        yield conn
    finally:
        conn.close()
