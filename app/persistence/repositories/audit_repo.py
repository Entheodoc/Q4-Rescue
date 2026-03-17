from __future__ import annotations

import json
from datetime import datetime, timezone
from uuid import uuid4

from app.persistence.connection import DatabaseConnection


class AuditLogRepository:
    def __init__(self, conn: DatabaseConnection):
        self.conn = conn

    def record(
        self,
        *,
        action: str,
        resource_type: str,
        resource_id: str | None,
        actor_subject: str,
        actor_permissions: list[str],
        request_id: str,
        metadata: dict | None = None,
        created_at: datetime | None = None,
    ) -> None:
        timestamp = created_at or datetime.now(timezone.utc)
        self.conn.execute(
            """
            INSERT INTO audit_events (
                id,
                action,
                resource_type,
                resource_id,
                actor_subject,
                actor_permissions,
                request_id,
                metadata,
                created_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                str(uuid4()),
                action,
                resource_type,
                resource_id,
                actor_subject,
                json.dumps(sorted(actor_permissions)),
                request_id,
                json.dumps(metadata or {}, sort_keys=True),
                timestamp.isoformat(),
            ),
        )
