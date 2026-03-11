from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, timezone
from uuid import UUID, uuid4

from app.domain.errors import ValidationError


@dataclass(frozen=True)
class ReferralId:
    value: UUID

    @staticmethod
    def new() -> "ReferralId":
        return ReferralId(uuid4())


@dataclass
class Referral:
    id: ReferralId
    member_id: UUID
    case_id: UUID | None
    received_at: datetime
    referral_source: str
    source_record_id: str | None
    referral_reason: str | None
    referral_notes: str | None
    snapshot_health_plan_member_id: str
    snapshot_first_name: str
    snapshot_last_name: str
    snapshot_birth_date: date | None
    snapshot_phone_number: str | None
    snapshot_preferred_language: str | None
    snapshot_supported_languages: tuple[str, ...]
    snapshot_address_line_1: str | None
    snapshot_address_line_2: str | None
    snapshot_city: str | None
    snapshot_state: str | None
    snapshot_zip: str | None
    snapshot_pbp: str | None
    snapshot_low_income_subsidy_level: str | None
    snapshot_active_status: str | None
    created_at: datetime
    updated_at: datetime

    @staticmethod
    def create(
        *,
        member_id: UUID,
        received_at: datetime,
        referral_source: str,
        snapshot_health_plan_member_id: str,
        snapshot_first_name: str,
        snapshot_last_name: str,
        case_id: UUID | None = None,
        source_record_id: str | None = None,
        referral_reason: str | None = None,
        referral_notes: str | None = None,
        snapshot_birth_date: date | None = None,
        snapshot_phone_number: str | None = None,
        snapshot_preferred_language: str | None = None,
        snapshot_supported_languages: tuple[str, ...] = (),
        snapshot_address_line_1: str | None = None,
        snapshot_address_line_2: str | None = None,
        snapshot_city: str | None = None,
        snapshot_state: str | None = None,
        snapshot_zip: str | None = None,
        snapshot_pbp: str | None = None,
        snapshot_low_income_subsidy_level: str | None = None,
        snapshot_active_status: str | None = None,
        now: datetime | None = None,
    ) -> "Referral":
        now = now or datetime.now(timezone.utc)

        if not referral_source or not referral_source.strip():
            raise ValidationError("referral_source is required")

        if not snapshot_health_plan_member_id or not snapshot_health_plan_member_id.strip():
            raise ValidationError("snapshot_health_plan_member_id is required")

        if not snapshot_first_name or not snapshot_first_name.strip():
            raise ValidationError("snapshot_first_name is required")

        if not snapshot_last_name or not snapshot_last_name.strip():
            raise ValidationError("snapshot_last_name is required")

        return Referral(
            id=ReferralId.new(),
            member_id=member_id,
            case_id=case_id,
            received_at=received_at,
            referral_source=referral_source.strip(),
            source_record_id=source_record_id.strip() if source_record_id and source_record_id.strip() else None,
            referral_reason=referral_reason.strip() if referral_reason and referral_reason.strip() else None,
            referral_notes=referral_notes.strip() if referral_notes and referral_notes.strip() else None,
            snapshot_health_plan_member_id=snapshot_health_plan_member_id.strip(),
            snapshot_first_name=snapshot_first_name.strip(),
            snapshot_last_name=snapshot_last_name.strip(),
            snapshot_birth_date=snapshot_birth_date,
            snapshot_phone_number=(
                snapshot_phone_number.strip()
                if snapshot_phone_number and snapshot_phone_number.strip()
                else None
            ),
            snapshot_preferred_language=(
                snapshot_preferred_language.strip()
                if snapshot_preferred_language and snapshot_preferred_language.strip()
                else None
            ),
            snapshot_supported_languages=tuple(
                language.strip()
                for language in snapshot_supported_languages
                if language and language.strip()
            ),
            snapshot_address_line_1=(
                snapshot_address_line_1.strip()
                if snapshot_address_line_1 and snapshot_address_line_1.strip()
                else None
            ),
            snapshot_address_line_2=(
                snapshot_address_line_2.strip()
                if snapshot_address_line_2 and snapshot_address_line_2.strip()
                else None
            ),
            snapshot_city=snapshot_city.strip() if snapshot_city and snapshot_city.strip() else None,
            snapshot_state=snapshot_state.strip() if snapshot_state and snapshot_state.strip() else None,
            snapshot_zip=snapshot_zip.strip() if snapshot_zip and snapshot_zip.strip() else None,
            snapshot_pbp=snapshot_pbp.strip() if snapshot_pbp and snapshot_pbp.strip() else None,
            snapshot_low_income_subsidy_level=(
                snapshot_low_income_subsidy_level.strip()
                if snapshot_low_income_subsidy_level and snapshot_low_income_subsidy_level.strip()
                else None
            ),
            snapshot_active_status=(
                snapshot_active_status.strip()
                if snapshot_active_status and snapshot_active_status.strip()
                else None
            ),
            created_at=now,
            updated_at=now,
        )
