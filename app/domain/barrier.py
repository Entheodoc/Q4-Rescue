from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
from uuid import UUID, uuid4

from app.domain.errors import ValidationError


class BarrierStatus(str, Enum):
    OPEN = "open"
    RESOLVED = "resolved"
    DISMISSED = "dismissed"


@dataclass(frozen=True)
class BarrierId:
    value: UUID

    @staticmethod
    def new() -> "BarrierId":
        return BarrierId(uuid4())


@dataclass
class Barrier:
    id: BarrierId
    case_id: UUID
    barrier_type: str
    title: str
    status: BarrierStatus
    severity: str | None
    description: str | None
    identified_at: datetime
    resolved_at: datetime | None
    created_at: datetime
    updated_at: datetime

    @staticmethod
    def create(
        *,
        case_id: UUID,
        barrier_type: str,
        title: str,
        severity: str | None = None,
        description: str | None = None,
        identified_at: datetime | None = None,
        now: datetime | None = None,
    ) -> "Barrier":
        now = now or datetime.now(timezone.utc)
        identified_at = identified_at or now

        if not barrier_type or not barrier_type.strip():
            raise ValidationError("barrier_type is required")

        if not title or not title.strip():
            raise ValidationError("title is required")

        return Barrier(
            id=BarrierId.new(),
            case_id=case_id,
            barrier_type=barrier_type.strip(),
            title=title.strip(),
            status=BarrierStatus.OPEN,
            severity=severity.strip() if severity and severity.strip() else None,
            description=description.strip() if description and description.strip() else None,
            identified_at=identified_at,
            resolved_at=None,
            created_at=now,
            updated_at=now,
        )
