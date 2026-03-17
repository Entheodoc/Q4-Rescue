from __future__ import annotations

from collections.abc import Sequence
from time import perf_counter
from typing import Any

import psycopg
from opentelemetry.trace import Status, StatusCode
from psycopg.rows import dict_row

from app.observability.metrics import record_db_operation
from app.observability.tracing import get_tracer
from app.persistence.sql import split_sql_script


class DatabaseIntegrityError(Exception):
    """Raised when the underlying database rejects a write for integrity reasons."""


TRACER = get_tracer(__name__)


class DatabaseCursor:
    def __init__(self, conn: "DatabaseConnection", cursor: Any):
        self._conn = conn
        self._cursor = cursor

    def execute(self, query: str, params: Sequence[Any] | None = None) -> "DatabaseCursor":
        translated_query = self._conn.translate_query(query)
        normalized_params = tuple(params or ())
        operation = self._conn.query_operation(query)
        start_time = perf_counter()

        with TRACER.start_as_current_span("db.query") as span:
            span.set_attribute("db.system", "postgresql")
            span.set_attribute("db.operation", operation)

            try:
                self._cursor.execute(translated_query, normalized_params)
            except self._conn.integrity_errors as exc:
                span.record_exception(exc)
                span.set_status(Status(StatusCode.ERROR))
                record_db_operation(
                    operation=operation,
                    outcome="integrity_error",
                    duration_seconds=perf_counter() - start_time,
                )
                raise DatabaseIntegrityError(str(exc)) from exc
            except Exception as exc:
                span.record_exception(exc)
                span.set_status(Status(StatusCode.ERROR))
                record_db_operation(
                    operation=operation,
                    outcome="error",
                    duration_seconds=perf_counter() - start_time,
                )
                raise

        record_db_operation(
            operation=operation,
            outcome="success",
            duration_seconds=perf_counter() - start_time,
        )
        return self

    def fetchone(self):
        return self._cursor.fetchone()

    def fetchall(self):
        return self._cursor.fetchall()


class DatabaseConnection:
    def __init__(self, *, raw_connection: Any):
        self._raw_connection = raw_connection

    @classmethod
    def connect_postgres(cls, database_url: str) -> "DatabaseConnection":
        connection = psycopg.connect(database_url, row_factory=dict_row)
        return cls(raw_connection=connection)

    @property
    def integrity_errors(self) -> tuple[type[BaseException], ...]:
        return (psycopg.IntegrityError,)

    def cursor(self) -> DatabaseCursor:
        return DatabaseCursor(self, self._raw_connection.cursor())

    def execute(self, query: str, params: Sequence[Any] | None = None) -> DatabaseCursor:
        cursor = self.cursor()
        cursor.execute(query, params)
        return cursor

    def executescript(self, script: str) -> None:
        for statement in split_sql_script(script):
            if statement.strip():
                self.execute(statement)

    def translate_query(self, query: str) -> str:
        return query.replace("?", "%s")

    def query_operation(self, query: str) -> str:
        for token in query.strip().split():
            normalized_token = token.strip().upper()
            if normalized_token:
                return normalized_token
        return "UNKNOWN"

    def commit(self) -> None:
        self._raw_connection.commit()

    def rollback(self) -> None:
        self._raw_connection.rollback()

    def close(self) -> None:
        self._raw_connection.close()

    def __enter__(self) -> "DatabaseConnection":
        return self

    def __exit__(self, exc_type, exc, tb) -> bool:
        if exc_type is None:
            self.commit()
        else:
            self.rollback()
        return False
