from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, timezone
from uuid import UUID, uuid4


@dataclass(frozen=True)
class MedicationPharmacyId:
    value: UUID

    @staticmethod
    def new() -> "MedicationPharmacyId":
        return MedicationPharmacyId(uuid4())


@dataclass(frozen=True)
class RefillDetail:
    days_supply: int
    expiration_date: date | None
    status: str | None = None


@dataclass
class MedicationPharmacy:
    id: MedicationPharmacyId
    medication_id: UUID
    pharmacy_id: UUID
    pharmacy_status: str | None
    last_fill_date: date | None
    next_fill_date: date | None
    pickup_date: date | None
    last_fill_days_supply: int | None
    refills: tuple[RefillDetail, ...]
    created_at: datetime
    updated_at: datetime

    @staticmethod
    def create(
        *,
        medication_id: UUID,
        pharmacy_id: UUID,
        pharmacy_status: str | None = None,
        last_fill_date: date | None = None,
        next_fill_date: date | None = None,
        pickup_date: date | None = None,
        last_fill_days_supply: int | None = None,
        refills: tuple[RefillDetail, ...] = (),
        now: datetime | None = None,
    ) -> "MedicationPharmacy":
        now = now or datetime.now(timezone.utc)

        return MedicationPharmacy(
            id=MedicationPharmacyId.new(),
            medication_id=medication_id,
            pharmacy_id=pharmacy_id,
            pharmacy_status=pharmacy_status.strip() if pharmacy_status and pharmacy_status.strip() else None,
            last_fill_date=last_fill_date,
            next_fill_date=next_fill_date,
            pickup_date=pickup_date,
            last_fill_days_supply=last_fill_days_supply,
            refills=tuple(refills),
            created_at=now,
            updated_at=now,
        )
