from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from uuid import UUID, uuid4


@dataclass(frozen=True)
class MedicationProviderId:
    value: UUID

    @staticmethod
    def new() -> "MedicationProviderId":
        return MedicationProviderId(uuid4())


@dataclass
class MedicationProvider:
    id: MedicationProviderId
    medication_id: UUID
    provider_id: UUID
    prescribing_role: str | None
    is_current_prescriber: bool
    last_prescribed_at: datetime | None
    refill_request_status: str | None
    provider_notes: str | None
    contact_for_refills: bool
    created_at: datetime
    updated_at: datetime

    @staticmethod
    def create(
        *,
        medication_id: UUID,
        provider_id: UUID,
        prescribing_role: str | None = None,
        is_current_prescriber: bool = False,
        last_prescribed_at: datetime | None = None,
        refill_request_status: str | None = None,
        provider_notes: str | None = None,
        contact_for_refills: bool = False,
        now: datetime | None = None,
    ) -> "MedicationProvider":
        now = now or datetime.now(timezone.utc)

        return MedicationProvider(
            id=MedicationProviderId.new(),
            medication_id=medication_id,
            provider_id=provider_id,
            prescribing_role=prescribing_role.strip() if prescribing_role and prescribing_role.strip() else None,
            is_current_prescriber=is_current_prescriber,
            last_prescribed_at=last_prescribed_at,
            refill_request_status=(
                refill_request_status.strip()
                if refill_request_status and refill_request_status.strip()
                else None
            ),
            provider_notes=provider_notes.strip() if provider_notes and provider_notes.strip() else None,
            contact_for_refills=contact_for_refills,
            created_at=now,
            updated_at=now,
        )
