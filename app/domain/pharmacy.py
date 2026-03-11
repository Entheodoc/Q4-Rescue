from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from uuid import UUID, uuid4

from app.domain.errors import ValidationError


@dataclass(frozen=True)
class PharmacyId:
    value: UUID

    @staticmethod
    def new() -> "PharmacyId":
        return PharmacyId(uuid4())


@dataclass
class Pharmacy:
    id: PharmacyId
    name: str
    phone_numbers: tuple[str, ...]
    preferred_phone_number: str | None
    fax_number: str | None
    address_line_1: str | None
    address_line_2: str | None
    city: str | None
    state: str | None
    zip_code: str | None
    created_at: datetime
    updated_at: datetime

    @staticmethod
    def create(
        *,
        name: str,
        phone_numbers: tuple[str, ...] = (),
        preferred_phone_number: str | None = None,
        fax_number: str | None = None,
        address_line_1: str | None = None,
        address_line_2: str | None = None,
        city: str | None = None,
        state: str | None = None,
        zip_code: str | None = None,
        now: datetime | None = None,
    ) -> "Pharmacy":
        now = now or datetime.now(timezone.utc)

        if not name or not name.strip():
            raise ValidationError("name is required")

        normalized_phone_numbers = tuple(
            number.strip() for number in phone_numbers if number and number.strip()
        )
        normalized_preferred_phone = (
            preferred_phone_number.strip()
            if preferred_phone_number and preferred_phone_number.strip()
            else None
        )

        if normalized_preferred_phone and normalized_phone_numbers:
            if normalized_preferred_phone not in normalized_phone_numbers:
                raise ValidationError(
                    "preferred_phone_number must also appear in phone_numbers"
                )

        return Pharmacy(
            id=PharmacyId.new(),
            name=name.strip(),
            phone_numbers=normalized_phone_numbers,
            preferred_phone_number=normalized_preferred_phone,
            fax_number=fax_number.strip() if fax_number and fax_number.strip() else None,
            address_line_1=address_line_1.strip() if address_line_1 and address_line_1.strip() else None,
            address_line_2=address_line_2.strip() if address_line_2 and address_line_2.strip() else None,
            city=city.strip() if city and city.strip() else None,
            state=state.strip() if state and state.strip() else None,
            zip_code=zip_code.strip() if zip_code and zip_code.strip() else None,
            created_at=now,
            updated_at=now,
        )
