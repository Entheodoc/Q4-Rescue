from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from uuid import UUID, uuid4

from app.domain.errors import ValidationError


@dataclass(frozen=True)
class MedicationId:
    value: UUID

    @staticmethod
    def new() -> "MedicationId":
        return MedicationId(uuid4())


@dataclass
class Medication:
    id: MedicationId
    measure_id: UUID
    medication_name: str
    display_name: str | None
    created_at: datetime
    updated_at: datetime

    @staticmethod
    def create(
        *,
        measure_id: UUID,
        medication_name: str,
        display_name: str | None = None,
        now: datetime | None = None,
    ) -> "Medication":
        now = now or datetime.now(timezone.utc)

        if not medication_name or not medication_name.strip():
            raise ValidationError("medication_name is required")

        normalized_name = medication_name.strip()

        return Medication(
            id=MedicationId.new(),
            measure_id=measure_id,
            medication_name=normalized_name,
            display_name=display_name.strip() if display_name and display_name.strip() else normalized_name,
            created_at=now,
            updated_at=now,
        )
