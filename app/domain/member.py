from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, timezone
from uuid import UUID, uuid4

from app.domain.errors import ValidationError


@dataclass(frozen=True)
class MemberId:
    value: UUID

    @staticmethod
    def new() -> "MemberId":
        return MemberId(uuid4())


@dataclass
class Member:
    id: MemberId
    health_plan_member_id: str
    first_name: str
    last_name: str
    birth_date: date | None
    sex: str | None
    phone_number: str | None
    preferred_contact_method: str | None
    preferred_language: str | None
    supported_languages: tuple[str, ...]
    address_line_1: str | None
    address_line_2: str | None
    city: str | None
    state: str | None
    zip_code: str | None
    pbp: str | None
    low_income_subsidy_level: str | None
    active_status: str | None
    created_at: datetime
    updated_at: datetime

    @staticmethod
    def create(
        *,
        health_plan_member_id: str,
        first_name: str,
        last_name: str,
        birth_date: date | None = None,
        sex: str | None = None,
        phone_number: str | None = None,
        preferred_contact_method: str | None = None,
        preferred_language: str | None = None,
        supported_languages: tuple[str, ...] = (),
        address_line_1: str | None = None,
        address_line_2: str | None = None,
        city: str | None = None,
        state: str | None = None,
        zip_code: str | None = None,
        pbp: str | None = None,
        low_income_subsidy_level: str | None = None,
        active_status: str | None = None,
        now: datetime | None = None,
    ) -> "Member":
        now = now or datetime.now(timezone.utc)

        if not health_plan_member_id or not health_plan_member_id.strip():
            raise ValidationError("health_plan_member_id is required")

        if not first_name or not first_name.strip():
            raise ValidationError("first_name is required")

        if not last_name or not last_name.strip():
            raise ValidationError("last_name is required")

        normalized_languages = tuple(
            language.strip()
            for language in supported_languages
            if language and language.strip()
        )
        normalized_preferred_language = (
            preferred_language.strip() if preferred_language and preferred_language.strip() else None
        )

        if (
            normalized_preferred_language
            and normalized_languages
            and normalized_preferred_language not in normalized_languages
        ):
            raise ValidationError(
                "preferred_language must also appear in supported_languages"
            )

        return Member(
            id=MemberId.new(),
            health_plan_member_id=health_plan_member_id.strip(),
            first_name=first_name.strip(),
            last_name=last_name.strip(),
            birth_date=birth_date,
            sex=sex.strip() if sex and sex.strip() else None,
            phone_number=phone_number.strip() if phone_number and phone_number.strip() else None,
            preferred_contact_method=(
                preferred_contact_method.strip()
                if preferred_contact_method and preferred_contact_method.strip()
                else None
            ),
            preferred_language=normalized_preferred_language,
            supported_languages=normalized_languages,
            address_line_1=address_line_1.strip() if address_line_1 and address_line_1.strip() else None,
            address_line_2=address_line_2.strip() if address_line_2 and address_line_2.strip() else None,
            city=city.strip() if city and city.strip() else None,
            state=state.strip() if state and state.strip() else None,
            zip_code=zip_code.strip() if zip_code and zip_code.strip() else None,
            pbp=pbp.strip() if pbp and pbp.strip() else None,
            low_income_subsidy_level=(
                low_income_subsidy_level.strip()
                if low_income_subsidy_level and low_income_subsidy_level.strip()
                else None
            ),
            active_status=active_status.strip() if active_status and active_status.strip() else None,
            created_at=now,
            updated_at=now,
        )
