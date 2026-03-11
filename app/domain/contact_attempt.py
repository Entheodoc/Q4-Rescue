from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
from uuid import UUID, uuid4

from app.domain.errors import ValidationError


class ContactPartyType(str, Enum):
    MEMBER = "member"
    PROVIDER = "provider"
    PHARMACY = "pharmacy"


class ContactMethod(str, Enum):
    CALL = "call"
    TEXT = "text"
    FAX = "fax"


@dataclass(frozen=True)
class ContactAttemptId:
    value: UUID

    @staticmethod
    def new() -> "ContactAttemptId":
        return ContactAttemptId(uuid4())


@dataclass
class ContactAttempt:
    id: ContactAttemptId
    contact_party_type: ContactPartyType
    contact_party_id: UUID
    contact_method: ContactMethod
    attempted_at: datetime
    outcome: str | None
    outcome_notes: str | None
    initiated_by: str | None
    created_at: datetime
    updated_at: datetime

    @staticmethod
    def create(
        *,
        contact_party_type: ContactPartyType,
        contact_party_id: UUID,
        contact_method: ContactMethod,
        attempted_at: datetime | None = None,
        outcome: str | None = None,
        outcome_notes: str | None = None,
        initiated_by: str | None = None,
        now: datetime | None = None,
    ) -> "ContactAttempt":
        now = now or datetime.now(timezone.utc)
        attempted_at = attempted_at or now

        if attempted_at > now:
            raise ValidationError("attempted_at cannot be in the future")

        return ContactAttempt(
            id=ContactAttemptId.new(),
            contact_party_type=contact_party_type,
            contact_party_id=contact_party_id,
            contact_method=contact_method,
            attempted_at=attempted_at,
            outcome=outcome.strip() if outcome and outcome.strip() else None,
            outcome_notes=outcome_notes.strip() if outcome_notes and outcome_notes.strip() else None,
            initiated_by=initiated_by.strip() if initiated_by and initiated_by.strip() else None,
            created_at=now,
            updated_at=now,
        )
