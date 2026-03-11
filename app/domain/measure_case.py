from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
from uuid import UUID, uuid4

from app.domain.errors import InvalidStateTransition, ValidationError


class MeasureCaseStatus(str, Enum):
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    ON_HOLD = "on_hold"
    CLOSED = "closed"
    ARCHIVED = "archived"


@dataclass(frozen=True)
class MeasureCaseId:
    value: UUID

    @staticmethod
    def new() -> "MeasureCaseId":
        return MeasureCaseId(uuid4())


@dataclass
class MeasureCase:
    id: MeasureCaseId
    member_id: str
    measure_type: str
    year: int
    current_pdc: float
    target_pdc: float
    status: MeasureCaseStatus
    created_at: datetime
    updated_at: datetime

    # ---------------------------------------------------------
    # CREATE
    # ---------------------------------------------------------

    @staticmethod
    def create(
        *,
        member_id: str,
        measure_type: str,
        year: int,
        current_pdc: float,
        target_pdc: float = 0.80,
        now: datetime | None = None,
    ) -> "MeasureCase":

        now = now or datetime.now(timezone.utc)

        if not member_id or not member_id.strip():
            raise ValidationError("member_id is required")

        if not measure_type or not measure_type.strip():
            raise ValidationError("measure_type is required")

        if year < 2000 or year > 2100:
            raise ValidationError("year out of allowed range")

        MeasureCase._validate_pdc(current_pdc, field="current_pdc")
        MeasureCase._validate_pdc(target_pdc, field="target_pdc")

        return MeasureCase(
            id=MeasureCaseId.new(),
            member_id=member_id.strip(),
            measure_type=measure_type.strip().upper(),
            year=year,
            current_pdc=float(current_pdc),
            target_pdc=float(target_pdc),
            status=MeasureCaseStatus.OPEN,
            created_at=now,
            updated_at=now,
        )

    # ---------------------------------------------------------
    # VALIDATION
    # ---------------------------------------------------------

    @staticmethod
    def _validate_pdc(value: float, *, field: str) -> None:
        try:
            v = float(value)
        except Exception as e:
            raise ValidationError(f"{field} must be a number") from e

        if v < 0.0 or v > 1.0:
            raise ValidationError(f"{field} must be between 0.0 and 1.0")

    # ---------------------------------------------------------
    # TRANSITIONS
    # ---------------------------------------------------------

    def start(self, *, now: datetime | None = None) -> None:
        now = now or datetime.now(timezone.utc)

        if self.status not in {MeasureCaseStatus.OPEN, MeasureCaseStatus.ON_HOLD}:
            raise InvalidStateTransition(f"Cannot start case from status={self.status}")

        self.status = MeasureCaseStatus.IN_PROGRESS
        self.updated_at = now

    def hold(self, *, now: datetime | None = None) -> None:
        now = now or datetime.now(timezone.utc)

        if self.status not in {MeasureCaseStatus.OPEN, MeasureCaseStatus.IN_PROGRESS}:
            raise InvalidStateTransition(f"Cannot hold case from status={self.status}")

        self.status = MeasureCaseStatus.ON_HOLD
        self.updated_at = now

    def close(self, *, now: datetime | None = None) -> None:
        now = now or datetime.now(timezone.utc)

        if self.status not in {MeasureCaseStatus.IN_PROGRESS, MeasureCaseStatus.ON_HOLD}:
            raise InvalidStateTransition(f"Cannot close case from status={self.status}")

        self.status = MeasureCaseStatus.CLOSED
        self.updated_at = now

    def archive(self, *, now: datetime | None = None) -> None:
        now = now or datetime.now(timezone.utc)

        if self.status != MeasureCaseStatus.CLOSED:
            raise InvalidStateTransition("Only CLOSED cases can be archived")

        self.status = MeasureCaseStatus.ARCHIVED
        self.updated_at = now
