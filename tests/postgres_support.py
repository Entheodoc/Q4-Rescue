from __future__ import annotations

import os

import psycopg


DEFAULT_TEST_DATABASE_URL = (
    "postgresql://q4_rescue:q4_rescue_dev@localhost:5432/q4_rescue_test"
)


def get_test_database_url() -> str:
    return os.getenv("Q4_RESCUE_TEST_DATABASE_URL", DEFAULT_TEST_DATABASE_URL)


def reset_database(database_url: str | None = None) -> str:
    resolved_database_url = database_url or get_test_database_url()
    with psycopg.connect(resolved_database_url, autocommit=True) as conn:
        with conn.cursor() as cursor:
            cursor.execute("DROP SCHEMA IF EXISTS public CASCADE")
            cursor.execute("CREATE SCHEMA public")
            cursor.execute("GRANT ALL ON SCHEMA public TO CURRENT_USER")
            cursor.execute("GRANT ALL ON SCHEMA public TO public")
    return resolved_database_url
