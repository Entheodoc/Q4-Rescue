from __future__ import annotations

from collections.abc import Generator
from uuid import uuid4

from fastapi import Header, Request, Response

from app.persistence.connection import DatabaseConnection
from app.persistence.db import get_conn


def get_db_conn() -> Generator[DatabaseConnection, None, None]:
    conn = get_conn()
    try:
        yield conn
    finally:
        conn.close()


def get_request_id(
    request: Request,
    response: Response,
    request_id: str | None = Header(default=None, alias="X-Request-ID"),
) -> str:
    state_request_id = getattr(request.state, "request_id", None)
    resolved_request_id = (
        state_request_id
        or (request_id.strip() if request_id and request_id.strip() else str(uuid4()))
    )
    request.state.request_id = resolved_request_id
    response.headers["X-Request-ID"] = resolved_request_id
    return resolved_request_id
