from datetime import date, datetime

from pydantic import BaseModel, Field, model_validator


class MemberInput(BaseModel):
    health_plan_member_id: str
    first_name: str
    last_name: str
    birth_date: date | None = None
    sex: str | None = None
    phone_number: str | None = None
    preferred_contact_method: str | None = None
    preferred_language: str | None = None
    supported_languages: list[str] = Field(default_factory=list)
    address_line_1: str | None = None
    address_line_2: str | None = None
    city: str | None = None
    state: str | None = None
    zip: str | None = None
    pbp: str | None = None
    low_income_subsidy_level: str | None = None
    active_status: str | None = None


class ReferralInput(BaseModel):
    received_at: datetime | None = None
    referral_source: str
    source_record_id: str | None = None
    referral_reason: str | None = None
    referral_notes: str | None = None
    snapshot_health_plan_member_id: str | None = None
    snapshot_first_name: str | None = None
    snapshot_last_name: str | None = None
    snapshot_birth_date: date | None = None
    snapshot_phone_number: str | None = None
    snapshot_preferred_language: str | None = None
    snapshot_supported_languages: list[str] | None = None
    snapshot_address_line_1: str | None = None
    snapshot_address_line_2: str | None = None
    snapshot_city: str | None = None
    snapshot_state: str | None = None
    snapshot_zip: str | None = None
    snapshot_pbp: str | None = None
    snapshot_low_income_subsidy_level: str | None = None
    snapshot_active_status: str | None = None


class ProviderIdentityInput(BaseModel):
    name: str
    phone_numbers: list[str] = Field(default_factory=list)
    preferred_phone_number: str | None = None
    fax_number: str | None = None
    address_line_1: str | None = None
    address_line_2: str | None = None
    city: str | None = None
    state: str | None = None
    zip: str | None = None


class MedicationProviderInput(BaseModel):
    provider: ProviderIdentityInput
    prescribing_role: str | None = None
    is_current_prescriber: bool = False
    last_prescribed_at: datetime | None = None
    refill_request_status: str | None = None
    provider_notes: str | None = None
    contact_for_refills: bool = False


class RefillInput(BaseModel):
    days_supply: int = Field(gt=0)
    expiration_date: date | None = None
    status: str | None = None


class PharmacyIdentityInput(BaseModel):
    name: str
    phone_numbers: list[str] = Field(default_factory=list)
    preferred_phone_number: str | None = None
    fax_number: str | None = None
    address_line_1: str | None = None
    address_line_2: str | None = None
    city: str | None = None
    state: str | None = None
    zip: str | None = None


class MedicationPharmacyInput(BaseModel):
    pharmacy: PharmacyIdentityInput
    pharmacy_status: str | None = None
    last_fill_date: date | None = None
    next_fill_date: date | None = None
    pickup_date: date | None = None
    last_fill_days_supply: int | None = Field(default=None, gt=0)
    refills: list[RefillInput] = Field(default_factory=list)


class MedicationInput(BaseModel):
    medication_name: str
    display_name: str | None = None
    providers: list[MedicationProviderInput] = Field(default_factory=list)
    pharmacies: list[MedicationPharmacyInput] = Field(default_factory=list)

    @model_validator(mode="after")
    def validate_provider_relationships(self) -> "MedicationInput":
        current_prescribers = sum(1 for provider in self.providers if provider.is_current_prescriber)
        if current_prescribers > 1:
            raise ValueError("a medication may have at most one current prescriber")

        refill_contacts = sum(1 for provider in self.providers if provider.contact_for_refills)
        if refill_contacts > 1:
            raise ValueError("a medication may have at most one refill-contact provider")

        return self


class MeasureInput(BaseModel):
    measure_code: str
    measure_name: str
    performance_year: int
    pdc: float | None = Field(default=None, ge=0.0, le=1.0)
    actionable_status: str | None = None
    critical_by_date: datetime | None = None
    target_threshold: float | None = Field(default=None, ge=0.0, le=1.0)
    source_system: str | None = None
    source_measure_id: str | None = None
    medications: list[MedicationInput] = Field(default_factory=list)


class CaseCreate(BaseModel):
    member: MemberInput
    referral: ReferralInput
    case_summary: str | None = None
    priority: str | None = None
    measures: list[MeasureInput] = Field(min_length=1)

    @model_validator(mode="after")
    def validate_measure_uniqueness(self) -> "CaseCreate":
        seen: set[tuple[str, int]] = set()
        for measure in self.measures:
            key = (measure.measure_code.strip().upper(), measure.performance_year)
            if key in seen:
                raise ValueError(
                    "a case may not contain duplicate active measures for the same code and year"
                )
            seen.add(key)

        return self
