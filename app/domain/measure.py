from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
from uuid import UUID, uuid4

from app.domain.errors import ValidationError


class MeasureStatus(str, Enum):
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    ON_HOLD = "on_hold"
    CLOSED = "closed"
    ARCHIVED = "archived"


@dataclass(frozen=True)
class MeasureId:
    value: UUID

    @staticmethod
    def new() -> "MeasureId":
        return MeasureId(uuid4())


@dataclass
class Measure:
    id: MeasureId
    case_id: UUID
    measure_code: str
    measure_name: str
    performance_year: int
    pdc: float | None
    status: MeasureStatus
    actionable_status: str | None
    identified_at: datetime
    opened_at: datetime | None
    closed_at: datetime | None
    closure_reason: str | None
    critical_by_date: datetime | None
    target_threshold: float | None
    source_system: str | None
    source_measure_id: str | None
    created_at: datetime
    updated_at: datetime

    @staticmethod
    def create(
        *,
        case_id: UUID,
        measure_code: str,
        measure_name: str,
        performance_year: int,
        identified_at: datetime | None = None,
        pdc: float | None = None,
        actionable_status: str | None = None,
        critical_by_date: datetime | None = None,
        target_threshold: float | None = None,
        source_system: str | None = None,
        source_measure_id: str | None = None,
        now: datetime | None = None,
    ) -> "Measure":
        now = now or datetime.now(timezone.utc)
        identified_at = identified_at or now

        if not measure_code or not measure_code.strip():
            raise ValidationError("measure_code is required")

        if not measure_name or not measure_name.strip():
            raise ValidationError("measure_name is required")

        if performance_year < 2000 or performance_year > 2100:
            raise ValidationError("performance_year out of allowed range")

        if pdc is not None and (pdc < 0.0 or pdc > 1.0):
            raise ValidationError("pdc must be between 0.0 and 1.0")

        if target_threshold is not None and (target_threshold < 0.0 or target_threshold > 1.0):
            raise ValidationError("target_threshold must be between 0.0 and 1.0")

        return Measure(
            id=MeasureId.new(),
            case_id=case_id,
            measure_code=measure_code.strip().upper(),
            measure_name=measure_name.strip(),
            performance_year=performance_year,
            pdc=pdc,
            status=MeasureStatus.OPEN,
            actionable_status=actionable_status.strip() if actionable_status and actionable_status.strip() else None,
            identified_at=identified_at,
            opened_at=now,
            closed_at=None,
            closure_reason=None,
            critical_by_date=critical_by_date,
            target_threshold=target_threshold,
            source_system=source_system.strip() if source_system and source_system.strip() else None,
            source_measure_id=(
                source_measure_id.strip() if source_measure_id and source_measure_id.strip() else None
            ),
            created_at=now,
            updated_at=now,
        )
