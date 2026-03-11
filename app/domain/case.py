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
    member_id: UUID
    referral_id: UUID
    status: CaseStatus
    opened_at: datetime
    closed_at: datetime | None
    archived_at: datetime | None
    closed_reason: str | None
    case_summary: str | None
    priority: str | None
    created_at: datetime
    updated_at: datetime

    @staticmethod
    def create(
        *,
        member_id: UUID,
        referral_id: UUID,
        case_summary: str | None = None,
        priority: str | None = None,
        now: datetime | None = None,
    ) -> "Case":
        now = now or datetime.now(timezone.utc)

        if not isinstance(member_id, UUID):
            raise ValidationError("member_id is required")

        if not isinstance(referral_id, UUID):
            raise ValidationError("referral_id is required")

        return Case(
            id=CaseId.new(),
            member_id=member_id,
            referral_id=referral_id,
            status=CaseStatus.OPEN,
            opened_at=now,
            closed_at=None,
            archived_at=None,
            closed_reason=None,
            case_summary=case_summary.strip() if case_summary and case_summary.strip() else None,
            priority=priority.strip() if priority and priority.strip() else None,
            created_at=now,
            updated_at=now,
        )

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

    def close(
        self,
        *,
        closed_reason: str | None = None,
        now: datetime | None = None,
    ) -> None:
        now = now or datetime.now(timezone.utc)

        if self.status not in {CaseStatus.IN_PROGRESS, CaseStatus.ON_HOLD}:
            raise InvalidStateTransition(f"Cannot close case from status={self.status}")

        self.status = CaseStatus.CLOSED
        self.closed_at = now
        self.closed_reason = (
            closed_reason.strip() if closed_reason and closed_reason.strip() else None
        )
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
        self.archived_at = now
        self.updated_at = now
