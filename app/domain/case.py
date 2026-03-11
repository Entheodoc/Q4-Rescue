from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
from uuid import UUID, uuid4

from app.domain.errors import InvalidStateTransition, ValidationError


class CaseStatus(str, Enum):
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    ON_HOLD = "on_hold"
    CLOSED = "closed"
    ARCHIVED = "archived"


@dataclass(frozen=True)
class CaseId:
    value: UUID

    @staticmethod
    def new() -> "CaseId":
        return CaseId(uuid4())


@dataclass
class Case:
    id: CaseId
    member_id: str
    measure_type: str
    year: int
    current_pdc: float
    target_pdc: float
    status: CaseStatus
    created_at: datetime
    updated_at: datetime

    @staticmethod
    def create(
        *,
        member_id: str,
        measure_type: str,
        year: int,
        current_pdc: float,
        target_pdc: float = 0.80,
        now: datetime | None = None,
    ) -> "Case":
        now = now or datetime.now(timezone.utc)

        if not member_id or not member_id.strip():
            raise ValidationError("member_id is required")

        if not measure_type or not measure_type.strip():
            raise ValidationError("measure_type is required")

        if year < 2000 or year > 2100:
            raise ValidationError("year out of allowed range")

        Case._validate_pdc(current_pdc, field="current_pdc")
        Case._validate_pdc(target_pdc, field="target_pdc")

        return Case(
            id=CaseId.new(),
            member_id=member_id.strip(),
            measure_type=measure_type.strip().upper(),
            year=year,
            current_pdc=float(current_pdc),
            target_pdc=float(target_pdc),
            status=CaseStatus.OPEN,
            created_at=now,
            updated_at=now,
        )

    @staticmethod
    def _validate_pdc(value: float, *, field: str) -> None:
        try:
            normalized = float(value)
        except Exception as exc:
            raise ValidationError(f"{field} must be a number") from exc

        if normalized < 0.0 or normalized > 1.0:
            raise ValidationError(f"{field} must be between 0.0 and 1.0")

    def start(self, *, now: datetime | None = None) -> None:
        now = now or datetime.now(timezone.utc)

        if self.status not in {CaseStatus.OPEN, CaseStatus.ON_HOLD}:
            raise InvalidStateTransition(f"Cannot start case from status={self.status}")

        self.status = CaseStatus.IN_PROGRESS
        self.updated_at = now

    def hold(self, *, now: datetime | None = None) -> None:
        now = now or datetime.now(timezone.utc)

        if self.status not in {CaseStatus.OPEN, CaseStatus.IN_PROGRESS}:
            raise InvalidStateTransition(f"Cannot hold case from status={self.status}")

        self.status = CaseStatus.ON_HOLD
        self.updated_at = now

    def close(self, *, now: datetime | None = None) -> None:
        now = now or datetime.now(timezone.utc)

        if self.status not in {CaseStatus.IN_PROGRESS, CaseStatus.ON_HOLD}:
            raise InvalidStateTransition(f"Cannot close case from status={self.status}")

        self.status = CaseStatus.CLOSED
        self.updated_at = now

    def reopen(self, *, now: datetime | None = None) -> None:
        now = now or datetime.now(timezone.utc)

        if self.status != CaseStatus.ON_HOLD:
            raise InvalidStateTransition("Only ON_HOLD cases can be reopened to OPEN")

        self.status = CaseStatus.OPEN
        self.updated_at = now

    def archive(self, *, now: datetime | None = None) -> None:
        now = now or datetime.now(timezone.utc)

        if self.status != CaseStatus.CLOSED:
            raise InvalidStateTransition("Only CLOSED cases can be archived")

        self.status = CaseStatus.ARCHIVED
        self.updated_at = now
