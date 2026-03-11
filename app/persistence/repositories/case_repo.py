import json
import sqlite3
from datetime import datetime, timezone
from uuid import UUID, uuid4

from app.domain.case import Case, CaseId, CaseStatus
from app.domain.errors import ConflictError
from app.domain.measure import Measure
from app.domain.medication import Medication
from app.domain.medication_pharmacy import MedicationPharmacy, RefillDetail
from app.domain.medication_provider import MedicationProvider
from app.domain.member import Member
from app.domain.pharmacy import Pharmacy
from app.domain.provider import Provider
from app.domain.referral import Referral
from app.shared.clock import utc_now


ACTIVE_CASE_STATUSES = (
    CaseStatus.OPEN.value,
    CaseStatus.IN_PROGRESS.value,
    CaseStatus.ON_HOLD.value,
)


class CaseRepository:
    def __init__(self, conn: sqlite3.Connection):
        self.conn = conn

    def exists_active_case(self, health_plan_member_id: str) -> bool:
        cursor = self.conn.cursor()
        cursor.execute(
            """
            SELECT 1
            FROM cases
            INNER JOIN members ON members.id = cases.member_id
            WHERE members.health_plan_member_id = ?
              AND cases.status IN (?, ?, ?)
            LIMIT 1
            """,
            (health_plan_member_id.strip(), *ACTIVE_CASE_STATUSES),
        )
        return cursor.fetchone() is not None

    def create(self, payload: dict) -> dict:
        member_payload = payload["member"]

        if self.exists_active_case(member_payload["health_plan_member_id"]):
            raise ConflictError("Active Case already exists for this member")

        now = utc_now()

        try:
            with self.conn:
                member_record = self._upsert_member(member_payload, now)

                referral = self._build_referral(
                    member_record=member_record,
                    member_payload=member_payload,
                    referral_payload=payload["referral"],
                    now=now,
                )
                case = Case.create(
                    member_id=UUID(member_record["id"]),
                    referral_id=referral.id.value,
                    case_summary=payload.get("case_summary"),
                    priority=payload.get("priority"),
                    now=now,
                )

                self._insert_referral(referral)
                self._insert_case(case)
                self._link_referral_to_case(referral_id=referral.id.value, case_id=case.id.value)

                for measure_payload in payload["measures"]:
                    measure = Measure.create(
                        case_id=case.id.value,
                        measure_code=measure_payload["measure_code"],
                        measure_name=measure_payload["measure_name"],
                        performance_year=measure_payload["performance_year"],
                        pdc=measure_payload.get("pdc"),
                        actionable_status=measure_payload.get("actionable_status"),
                        critical_by_date=measure_payload.get("critical_by_date"),
                        target_threshold=measure_payload.get("target_threshold"),
                        source_system=measure_payload.get("source_system"),
                        source_measure_id=measure_payload.get("source_measure_id"),
                        now=now,
                    )
                    self._insert_measure(measure)

                    for medication_payload in measure_payload.get("medications", []):
                        medication = Medication.create(
                            measure_id=measure.id.value,
                            medication_name=medication_payload["medication_name"],
                            display_name=medication_payload.get("display_name"),
                            now=now,
                        )
                        self._insert_medication(medication)
                        self._insert_medication_providers(
                            medication.id.value,
                            medication_payload.get("providers", []),
                            now,
                        )
                        self._insert_medication_pharmacies(
                            medication.id.value,
                            medication_payload.get("pharmacies", []),
                            now,
                        )
        except sqlite3.IntegrityError as exc:
            if "idx_cases_member_active" in str(exc):
                raise ConflictError("Active Case already exists for this member") from exc
            raise

        return self.get_case_graph(case.id.value)

    def list_all(self) -> list[dict]:
        rows = self.conn.execute(
            "SELECT id FROM cases ORDER BY created_at DESC"
        ).fetchall()
        return [self.get_case_graph(UUID(row["id"])) for row in rows]

    def get_by_id(self, case_id: UUID) -> Case | None:
        row = self.conn.execute("SELECT * FROM cases WHERE id = ?", (str(case_id),)).fetchone()
        if not row:
            return None
        return self._row_to_domain(row)

    def get_case_graph(self, case_id: UUID) -> dict | None:
        case_row = self.conn.execute("SELECT * FROM cases WHERE id = ?", (str(case_id),)).fetchone()
        if not case_row:
            return None

        member_row = self.conn.execute(
            "SELECT * FROM members WHERE id = ?",
            (case_row["member_id"],),
        ).fetchone()
        referral_row = self.conn.execute(
            "SELECT * FROM referrals WHERE id = ?",
            (case_row["referral_id"],),
        ).fetchone()

        return {
            "id": case_row["id"],
            "status": case_row["status"],
            "case_summary": case_row["case_summary"],
            "priority": case_row["priority"],
            "opened_at": case_row["opened_at"],
            "closed_at": case_row["closed_at"],
            "archived_at": case_row["archived_at"],
            "closed_reason": case_row["closed_reason"],
            "created_at": case_row["created_at"],
            "updated_at": case_row["updated_at"],
            "member": self._serialize_member(member_row),
            "referral": self._serialize_referral(referral_row),
            "measures": self._serialize_measures(case_row["id"]),
            "barriers": self._serialize_barriers(case_row["id"]),
            "tasks": self._serialize_tasks(case_row["id"]),
        }

    def update(self, case: Case) -> None:
        self.conn.execute(
            """
            UPDATE cases
            SET status = ?,
                opened_at = ?,
                closed_at = ?,
                archived_at = ?,
                closed_reason = ?,
                case_summary = ?,
                priority = ?,
                updated_at = ?
            WHERE id = ?
            """,
            (
                case.status.value,
                case.opened_at.isoformat(),
                case.closed_at.isoformat() if case.closed_at else None,
                case.archived_at.isoformat() if case.archived_at else None,
                case.closed_reason,
                case.case_summary,
                case.priority,
                case.updated_at.isoformat(),
                str(case.id.value),
            ),
        )
        self.conn.commit()

    def _upsert_member(self, payload: dict, now: datetime) -> dict:
        row = self.conn.execute(
            "SELECT * FROM members WHERE health_plan_member_id = ?",
            (payload["health_plan_member_id"].strip(),),
        ).fetchone()

        if row:
            self.conn.execute(
                """
                UPDATE members
                SET first_name = ?,
                    last_name = ?,
                    birth_date = ?,
                    sex = ?,
                    phone_number = ?,
                    preferred_contact_method = ?,
                    preferred_language = ?,
                    supported_languages = ?,
                    address_line_1 = ?,
                    address_line_2 = ?,
                    city = ?,
                    state = ?,
                    zip = ?,
                    pbp = ?,
                    low_income_subsidy_level = ?,
                    active_status = ?,
                    updated_at = ?
                WHERE id = ?
                """,
                (
                    payload["first_name"].strip(),
                    payload["last_name"].strip(),
                    payload.get("birth_date").isoformat() if payload.get("birth_date") else None,
                    self._normalize_string(payload.get("sex")),
                    self._normalize_string(payload.get("phone_number")),
                    self._normalize_string(payload.get("preferred_contact_method")),
                    self._normalize_string(payload.get("preferred_language")),
                    json.dumps(payload.get("supported_languages", [])),
                    self._normalize_string(payload.get("address_line_1")),
                    self._normalize_string(payload.get("address_line_2")),
                    self._normalize_string(payload.get("city")),
                    self._normalize_string(payload.get("state")),
                    self._normalize_string(payload.get("zip")),
                    self._normalize_string(payload.get("pbp")),
                    self._normalize_string(payload.get("low_income_subsidy_level")),
                    self._normalize_string(payload.get("active_status")),
                    now.isoformat(),
                    row["id"],
                ),
            )
            return self.conn.execute(
                "SELECT * FROM members WHERE id = ?",
                (row["id"],),
            ).fetchone()

        member = Member.create(
            health_plan_member_id=payload["health_plan_member_id"],
            first_name=payload["first_name"],
            last_name=payload["last_name"],
            birth_date=payload.get("birth_date"),
            sex=payload.get("sex"),
            phone_number=payload.get("phone_number"),
            preferred_contact_method=payload.get("preferred_contact_method"),
            preferred_language=payload.get("preferred_language"),
            supported_languages=tuple(payload.get("supported_languages", [])),
            address_line_1=payload.get("address_line_1"),
            address_line_2=payload.get("address_line_2"),
            city=payload.get("city"),
            state=payload.get("state"),
            zip_code=payload.get("zip"),
            pbp=payload.get("pbp"),
            low_income_subsidy_level=payload.get("low_income_subsidy_level"),
            active_status=payload.get("active_status"),
            now=now,
        )
        self.conn.execute(
            """
            INSERT INTO members (
                id,
                health_plan_member_id,
                first_name,
                last_name,
                birth_date,
                sex,
                phone_number,
                preferred_contact_method,
                preferred_language,
                supported_languages,
                address_line_1,
                address_line_2,
                city,
                state,
                zip,
                pbp,
                low_income_subsidy_level,
                active_status,
                created_at,
                updated_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                str(member.id.value),
                member.health_plan_member_id,
                member.first_name,
                member.last_name,
                member.birth_date.isoformat() if member.birth_date else None,
                member.sex,
                member.phone_number,
                member.preferred_contact_method,
                member.preferred_language,
                json.dumps(list(member.supported_languages)),
                member.address_line_1,
                member.address_line_2,
                member.city,
                member.state,
                member.zip_code,
                member.pbp,
                member.low_income_subsidy_level,
                member.active_status,
                member.created_at.isoformat(),
                member.updated_at.isoformat(),
            ),
        )
        return self.conn.execute(
            "SELECT * FROM members WHERE id = ?",
            (str(member.id.value),),
        ).fetchone()

    def _build_referral(
        self,
        *,
        member_record: sqlite3.Row,
        member_payload: dict,
        referral_payload: dict,
        now: datetime,
    ) -> Referral:
        snapshot_supported_languages = referral_payload.get("snapshot_supported_languages")
        if snapshot_supported_languages is None:
            snapshot_supported_languages = member_payload.get("supported_languages", [])

        return Referral.create(
            member_id=UUID(member_record["id"]),
            received_at=referral_payload.get("received_at") or now,
            referral_source=referral_payload["referral_source"],
            source_record_id=referral_payload.get("source_record_id"),
            referral_reason=referral_payload.get("referral_reason"),
            referral_notes=referral_payload.get("referral_notes"),
            snapshot_health_plan_member_id=(
                referral_payload.get("snapshot_health_plan_member_id")
                or member_payload["health_plan_member_id"]
            ),
            snapshot_first_name=(
                referral_payload.get("snapshot_first_name") or member_payload["first_name"]
            ),
            snapshot_last_name=(
                referral_payload.get("snapshot_last_name") or member_payload["last_name"]
            ),
            snapshot_birth_date=(
                referral_payload.get("snapshot_birth_date") or member_payload.get("birth_date")
            ),
            snapshot_phone_number=(
                referral_payload.get("snapshot_phone_number") or member_payload.get("phone_number")
            ),
            snapshot_preferred_language=(
                referral_payload.get("snapshot_preferred_language")
                or member_payload.get("preferred_language")
            ),
            snapshot_supported_languages=tuple(snapshot_supported_languages),
            snapshot_address_line_1=(
                referral_payload.get("snapshot_address_line_1")
                or member_payload.get("address_line_1")
            ),
            snapshot_address_line_2=(
                referral_payload.get("snapshot_address_line_2")
                or member_payload.get("address_line_2")
            ),
            snapshot_city=referral_payload.get("snapshot_city") or member_payload.get("city"),
            snapshot_state=referral_payload.get("snapshot_state") or member_payload.get("state"),
            snapshot_zip=referral_payload.get("snapshot_zip") or member_payload.get("zip"),
            snapshot_pbp=referral_payload.get("snapshot_pbp") or member_payload.get("pbp"),
            snapshot_low_income_subsidy_level=(
                referral_payload.get("snapshot_low_income_subsidy_level")
                or member_payload.get("low_income_subsidy_level")
            ),
            snapshot_active_status=(
                referral_payload.get("snapshot_active_status")
                or member_payload.get("active_status")
            ),
            now=now,
        )

    def _insert_referral(self, referral: Referral) -> None:
        self.conn.execute(
            """
            INSERT INTO referrals (
                id,
                member_id,
                case_id,
                received_at,
                referral_source,
                source_record_id,
                referral_reason,
                referral_notes,
                snapshot_health_plan_member_id,
                snapshot_first_name,
                snapshot_last_name,
                snapshot_birth_date,
                snapshot_phone_number,
                snapshot_preferred_language,
                snapshot_supported_languages,
                snapshot_address_line_1,
                snapshot_address_line_2,
                snapshot_city,
                snapshot_state,
                snapshot_zip,
                snapshot_pbp,
                snapshot_low_income_subsidy_level,
                snapshot_active_status,
                created_at,
                updated_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                str(referral.id.value),
                str(referral.member_id),
                str(referral.case_id) if referral.case_id else None,
                referral.received_at.isoformat(),
                referral.referral_source,
                referral.source_record_id,
                referral.referral_reason,
                referral.referral_notes,
                referral.snapshot_health_plan_member_id,
                referral.snapshot_first_name,
                referral.snapshot_last_name,
                referral.snapshot_birth_date.isoformat() if referral.snapshot_birth_date else None,
                referral.snapshot_phone_number,
                referral.snapshot_preferred_language,
                json.dumps(list(referral.snapshot_supported_languages)),
                referral.snapshot_address_line_1,
                referral.snapshot_address_line_2,
                referral.snapshot_city,
                referral.snapshot_state,
                referral.snapshot_zip,
                referral.snapshot_pbp,
                referral.snapshot_low_income_subsidy_level,
                referral.snapshot_active_status,
                referral.created_at.isoformat(),
                referral.updated_at.isoformat(),
            ),
        )

    def _link_referral_to_case(self, *, referral_id: UUID, case_id: UUID) -> None:
        self.conn.execute(
            """
            UPDATE referrals
            SET case_id = ?,
                updated_at = ?
            WHERE id = ?
            """,
            (str(case_id), utc_now().isoformat(), str(referral_id)),
        )

    def _insert_case(self, case: Case) -> None:
        self.conn.execute(
            """
            INSERT INTO cases (
                id,
                member_id,
                referral_id,
                status,
                opened_at,
                closed_at,
                archived_at,
                closed_reason,
                case_summary,
                priority,
                created_at,
                updated_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                str(case.id.value),
                str(case.member_id),
                str(case.referral_id),
                case.status.value,
                case.opened_at.isoformat(),
                case.closed_at.isoformat() if case.closed_at else None,
                case.archived_at.isoformat() if case.archived_at else None,
                case.closed_reason,
                case.case_summary,
                case.priority,
                case.created_at.isoformat(),
                case.updated_at.isoformat(),
            ),
        )

    def _insert_measure(self, measure: Measure) -> None:
        self.conn.execute(
            """
            INSERT INTO measures (
                id,
                case_id,
                measure_code,
                measure_name,
                performance_year,
                pdc,
                status,
                actionable_status,
                identified_at,
                opened_at,
                closed_at,
                closure_reason,
                critical_by_date,
                target_threshold,
                source_system,
                source_measure_id,
                created_at,
                updated_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                str(measure.id.value),
                str(measure.case_id),
                measure.measure_code,
                measure.measure_name,
                measure.performance_year,
                measure.pdc,
                measure.status.value,
                measure.actionable_status,
                measure.identified_at.isoformat(),
                measure.opened_at.isoformat() if measure.opened_at else None,
                measure.closed_at.isoformat() if measure.closed_at else None,
                measure.closure_reason,
                measure.critical_by_date.isoformat() if measure.critical_by_date else None,
                measure.target_threshold,
                measure.source_system,
                measure.source_measure_id,
                measure.created_at.isoformat(),
                measure.updated_at.isoformat(),
            ),
        )

    def _insert_medication(self, medication: Medication) -> None:
        self.conn.execute(
            """
            INSERT INTO medications (
                id,
                measure_id,
                medication_name,
                display_name,
                created_at,
                updated_at
            )
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                str(medication.id.value),
                str(medication.measure_id),
                medication.medication_name,
                medication.display_name,
                medication.created_at.isoformat(),
                medication.updated_at.isoformat(),
            ),
        )

    def _insert_medication_providers(
        self,
        medication_id: UUID,
        providers: list[dict],
        now: datetime,
    ) -> None:
        for provider_payload in providers:
            provider_row = self._get_or_create_provider(provider_payload["provider"], now)
            medication_provider = MedicationProvider.create(
                medication_id=medication_id,
                provider_id=UUID(provider_row["id"]),
                prescribing_role=provider_payload.get("prescribing_role"),
                is_current_prescriber=provider_payload.get("is_current_prescriber", False),
                last_prescribed_at=provider_payload.get("last_prescribed_at"),
                refill_request_status=provider_payload.get("refill_request_status"),
                provider_notes=provider_payload.get("provider_notes"),
                contact_for_refills=provider_payload.get("contact_for_refills", False),
                now=now,
            )
            self.conn.execute(
                """
                INSERT INTO medication_providers (
                    id,
                    medication_id,
                    provider_id,
                    prescribing_role,
                    is_current_prescriber,
                    last_prescribed_at,
                    refill_request_status,
                    provider_notes,
                    contact_for_refills,
                    created_at,
                    updated_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    str(medication_provider.id.value),
                    str(medication_provider.medication_id),
                    str(medication_provider.provider_id),
                    medication_provider.prescribing_role,
                    int(medication_provider.is_current_prescriber),
                    medication_provider.last_prescribed_at.isoformat()
                    if medication_provider.last_prescribed_at
                    else None,
                    medication_provider.refill_request_status,
                    medication_provider.provider_notes,
                    int(medication_provider.contact_for_refills),
                    medication_provider.created_at.isoformat(),
                    medication_provider.updated_at.isoformat(),
                ),
            )

    def _insert_medication_pharmacies(
        self,
        medication_id: UUID,
        pharmacies: list[dict],
        now: datetime,
    ) -> None:
        for pharmacy_payload in pharmacies:
            pharmacy_row = self._get_or_create_pharmacy(pharmacy_payload["pharmacy"], now)
            refill_details = tuple(
                RefillDetail(
                    days_supply=refill["days_supply"],
                    expiration_date=refill.get("expiration_date"),
                    status=self._normalize_string(refill.get("status")),
                )
                for refill in pharmacy_payload.get("refills", [])
            )
            medication_pharmacy = MedicationPharmacy.create(
                medication_id=medication_id,
                pharmacy_id=UUID(pharmacy_row["id"]),
                pharmacy_status=pharmacy_payload.get("pharmacy_status"),
                last_fill_date=pharmacy_payload.get("last_fill_date"),
                next_fill_date=pharmacy_payload.get("next_fill_date"),
                pickup_date=pharmacy_payload.get("pickup_date"),
                last_fill_days_supply=pharmacy_payload.get("last_fill_days_supply"),
                refills=refill_details,
                now=now,
            )
            self.conn.execute(
                """
                INSERT INTO medication_pharmacies (
                    id,
                    medication_id,
                    pharmacy_id,
                    pharmacy_status,
                    last_fill_date,
                    next_fill_date,
                    pickup_date,
                    last_fill_days_supply,
                    created_at,
                    updated_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    str(medication_pharmacy.id.value),
                    str(medication_pharmacy.medication_id),
                    str(medication_pharmacy.pharmacy_id),
                    medication_pharmacy.pharmacy_status,
                    medication_pharmacy.last_fill_date.isoformat()
                    if medication_pharmacy.last_fill_date
                    else None,
                    medication_pharmacy.next_fill_date.isoformat()
                    if medication_pharmacy.next_fill_date
                    else None,
                    medication_pharmacy.pickup_date.isoformat()
                    if medication_pharmacy.pickup_date
                    else None,
                    medication_pharmacy.last_fill_days_supply,
                    medication_pharmacy.created_at.isoformat(),
                    medication_pharmacy.updated_at.isoformat(),
                ),
            )
            for refill in medication_pharmacy.refills:
                refill_id = str(uuid4())
                self.conn.execute(
                    """
                    INSERT INTO medication_pharmacy_refills (
                        id,
                        medication_pharmacy_id,
                        days_supply,
                        expiration_date,
                        status,
                        created_at
                    )
                    VALUES (?, ?, ?, ?, ?, ?)
                    """,
                    (
                        refill_id,
                        str(medication_pharmacy.id.value),
                        refill.days_supply,
                        refill.expiration_date.isoformat() if refill.expiration_date else None,
                        refill.status,
                        now.isoformat(),
                    ),
                )

    def _get_or_create_provider(self, payload: dict, now: datetime) -> sqlite3.Row:
        normalized_name = payload["name"].strip()
        preferred_phone = self._normalize_string(payload.get("preferred_phone_number"))
        fax_number = self._normalize_string(payload.get("fax_number"))
        row = self.conn.execute(
            """
            SELECT *
            FROM providers
            WHERE lower(name) = lower(?)
              AND COALESCE(preferred_phone_number, '') = COALESCE(?, '')
              AND COALESCE(fax_number, '') = COALESCE(?, '')
            LIMIT 1
            """,
            (normalized_name, preferred_phone, fax_number),
        ).fetchone()

        if row:
            self.conn.execute(
                """
                UPDATE providers
                SET phone_numbers = ?,
                    preferred_phone_number = ?,
                    fax_number = ?,
                    address_line_1 = ?,
                    address_line_2 = ?,
                    city = ?,
                    state = ?,
                    zip = ?,
                    updated_at = ?
                WHERE id = ?
                """,
                (
                    json.dumps(payload.get("phone_numbers", [])),
                    preferred_phone,
                    fax_number,
                    self._normalize_string(payload.get("address_line_1")),
                    self._normalize_string(payload.get("address_line_2")),
                    self._normalize_string(payload.get("city")),
                    self._normalize_string(payload.get("state")),
                    self._normalize_string(payload.get("zip")),
                    now.isoformat(),
                    row["id"],
                ),
            )
            return self.conn.execute("SELECT * FROM providers WHERE id = ?", (row["id"],)).fetchone()

        provider = Provider.create(
            name=normalized_name,
            phone_numbers=tuple(payload.get("phone_numbers", [])),
            preferred_phone_number=preferred_phone,
            fax_number=fax_number,
            address_line_1=payload.get("address_line_1"),
            address_line_2=payload.get("address_line_2"),
            city=payload.get("city"),
            state=payload.get("state"),
            zip_code=payload.get("zip"),
            now=now,
        )
        self.conn.execute(
            """
            INSERT INTO providers (
                id,
                name,
                phone_numbers,
                preferred_phone_number,
                fax_number,
                address_line_1,
                address_line_2,
                city,
                state,
                zip,
                created_at,
                updated_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                str(provider.id.value),
                provider.name,
                json.dumps(list(provider.phone_numbers)),
                provider.preferred_phone_number,
                provider.fax_number,
                provider.address_line_1,
                provider.address_line_2,
                provider.city,
                provider.state,
                provider.zip_code,
                provider.created_at.isoformat(),
                provider.updated_at.isoformat(),
            ),
        )
        return self.conn.execute("SELECT * FROM providers WHERE id = ?", (str(provider.id.value),)).fetchone()

    def _get_or_create_pharmacy(self, payload: dict, now: datetime) -> sqlite3.Row:
        normalized_name = payload["name"].strip()
        preferred_phone = self._normalize_string(payload.get("preferred_phone_number"))
        fax_number = self._normalize_string(payload.get("fax_number"))
        row = self.conn.execute(
            """
            SELECT *
            FROM pharmacies
            WHERE lower(name) = lower(?)
              AND COALESCE(preferred_phone_number, '') = COALESCE(?, '')
              AND COALESCE(fax_number, '') = COALESCE(?, '')
            LIMIT 1
            """,
            (normalized_name, preferred_phone, fax_number),
        ).fetchone()

        if row:
            self.conn.execute(
                """
                UPDATE pharmacies
                SET phone_numbers = ?,
                    preferred_phone_number = ?,
                    fax_number = ?,
                    address_line_1 = ?,
                    address_line_2 = ?,
                    city = ?,
                    state = ?,
                    zip = ?,
                    updated_at = ?
                WHERE id = ?
                """,
                (
                    json.dumps(payload.get("phone_numbers", [])),
                    preferred_phone,
                    fax_number,
                    self._normalize_string(payload.get("address_line_1")),
                    self._normalize_string(payload.get("address_line_2")),
                    self._normalize_string(payload.get("city")),
                    self._normalize_string(payload.get("state")),
                    self._normalize_string(payload.get("zip")),
                    now.isoformat(),
                    row["id"],
                ),
            )
            return self.conn.execute("SELECT * FROM pharmacies WHERE id = ?", (row["id"],)).fetchone()

        pharmacy = Pharmacy.create(
            name=normalized_name,
            phone_numbers=tuple(payload.get("phone_numbers", [])),
            preferred_phone_number=preferred_phone,
            fax_number=fax_number,
            address_line_1=payload.get("address_line_1"),
            address_line_2=payload.get("address_line_2"),
            city=payload.get("city"),
            state=payload.get("state"),
            zip_code=payload.get("zip"),
            now=now,
        )
        self.conn.execute(
            """
            INSERT INTO pharmacies (
                id,
                name,
                phone_numbers,
                preferred_phone_number,
                fax_number,
                address_line_1,
                address_line_2,
                city,
                state,
                zip,
                created_at,
                updated_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                str(pharmacy.id.value),
                pharmacy.name,
                json.dumps(list(pharmacy.phone_numbers)),
                pharmacy.preferred_phone_number,
                pharmacy.fax_number,
                pharmacy.address_line_1,
                pharmacy.address_line_2,
                pharmacy.city,
                pharmacy.state,
                pharmacy.zip_code,
                pharmacy.created_at.isoformat(),
                pharmacy.updated_at.isoformat(),
            ),
        )
        return self.conn.execute("SELECT * FROM pharmacies WHERE id = ?", (str(pharmacy.id.value),)).fetchone()

    def _serialize_member(self, row: sqlite3.Row) -> dict:
        return {
            "member_id": row["id"],
            "health_plan_member_id": row["health_plan_member_id"],
            "first_name": row["first_name"],
            "last_name": row["last_name"],
            "birth_date": row["birth_date"],
            "sex": row["sex"],
            "phone_number": row["phone_number"],
            "preferred_contact_method": row["preferred_contact_method"],
            "preferred_language": row["preferred_language"],
            "supported_languages": self._parse_json_array(row["supported_languages"]),
            "address_line_1": row["address_line_1"],
            "address_line_2": row["address_line_2"],
            "city": row["city"],
            "state": row["state"],
            "zip": row["zip"],
            "pbp": row["pbp"],
            "low_income_subsidy_level": row["low_income_subsidy_level"],
            "active_status": row["active_status"],
            "created_at": row["created_at"],
            "updated_at": row["updated_at"],
        }

    def _serialize_referral(self, row: sqlite3.Row) -> dict:
        return {
            "referral_id": row["id"],
            "member_id": row["member_id"],
            "case_id": row["case_id"],
            "received_at": row["received_at"],
            "referral_source": row["referral_source"],
            "source_record_id": row["source_record_id"],
            "referral_reason": row["referral_reason"],
            "referral_notes": row["referral_notes"],
            "snapshot_health_plan_member_id": row["snapshot_health_plan_member_id"],
            "snapshot_first_name": row["snapshot_first_name"],
            "snapshot_last_name": row["snapshot_last_name"],
            "snapshot_birth_date": row["snapshot_birth_date"],
            "snapshot_phone_number": row["snapshot_phone_number"],
            "snapshot_preferred_language": row["snapshot_preferred_language"],
            "snapshot_supported_languages": self._parse_json_array(
                row["snapshot_supported_languages"]
            ),
            "snapshot_address_line_1": row["snapshot_address_line_1"],
            "snapshot_address_line_2": row["snapshot_address_line_2"],
            "snapshot_city": row["snapshot_city"],
            "snapshot_state": row["snapshot_state"],
            "snapshot_zip": row["snapshot_zip"],
            "snapshot_pbp": row["snapshot_pbp"],
            "snapshot_low_income_subsidy_level": row["snapshot_low_income_subsidy_level"],
            "snapshot_active_status": row["snapshot_active_status"],
            "created_at": row["created_at"],
            "updated_at": row["updated_at"],
        }

    def _serialize_measures(self, case_id: str) -> list[dict]:
        rows = self.conn.execute(
            "SELECT * FROM measures WHERE case_id = ? ORDER BY created_at ASC",
            (case_id,),
        ).fetchall()
        measures = []
        for row in rows:
            measures.append(
                {
                    "measure_id": row["id"],
                    "measure_code": row["measure_code"],
                    "measure_name": row["measure_name"],
                    "performance_year": row["performance_year"],
                    "pdc": row["pdc"],
                    "status": row["status"],
                    "actionable_status": row["actionable_status"],
                    "identified_at": row["identified_at"],
                    "opened_at": row["opened_at"],
                    "closed_at": row["closed_at"],
                    "closure_reason": row["closure_reason"],
                    "critical_by_date": row["critical_by_date"],
                    "target_threshold": row["target_threshold"],
                    "source_system": row["source_system"],
                    "source_measure_id": row["source_measure_id"],
                    "created_at": row["created_at"],
                    "updated_at": row["updated_at"],
                    "medications": self._serialize_medications(row["id"]),
                }
            )
        return measures

    def _serialize_medications(self, measure_id: str) -> list[dict]:
        rows = self.conn.execute(
            "SELECT * FROM medications WHERE measure_id = ? ORDER BY created_at ASC",
            (measure_id,),
        ).fetchall()
        medications = []
        for row in rows:
            medications.append(
                {
                    "medication_id": row["id"],
                    "medication_name": row["medication_name"],
                    "display_name": row["display_name"],
                    "created_at": row["created_at"],
                    "updated_at": row["updated_at"],
                    "providers": self._serialize_medication_providers(row["id"]),
                    "pharmacies": self._serialize_medication_pharmacies(row["id"]),
                }
            )
        return medications

    def _serialize_medication_providers(self, medication_id: str) -> list[dict]:
        rows = self.conn.execute(
            """
            SELECT
                mp.id AS medication_provider_id,
                mp.provider_id AS linked_provider_id,
                mp.prescribing_role,
                mp.is_current_prescriber,
                mp.last_prescribed_at,
                mp.refill_request_status,
                mp.provider_notes,
                mp.contact_for_refills,
                mp.created_at AS medication_provider_created_at,
                mp.updated_at AS medication_provider_updated_at,
                p.id AS provider_entity_id,
                p.name AS provider_name,
                p.phone_numbers AS provider_phone_numbers,
                p.preferred_phone_number AS provider_preferred_phone_number,
                p.fax_number AS provider_fax_number,
                p.address_line_1 AS provider_address_line_1,
                p.address_line_2 AS provider_address_line_2,
                p.city AS provider_city,
                p.state AS provider_state,
                p.zip AS provider_zip
            FROM medication_providers AS mp
            INNER JOIN providers AS p ON p.id = mp.provider_id
            WHERE mp.medication_id = ?
            ORDER BY mp.created_at ASC
            """,
            (medication_id,),
        ).fetchall()
        providers = []
        for row in rows:
            providers.append(
                {
                    "medication_provider_id": row["medication_provider_id"],
                    "prescribing_role": row["prescribing_role"],
                    "is_current_prescriber": bool(row["is_current_prescriber"]),
                    "last_prescribed_at": row["last_prescribed_at"],
                    "refill_request_status": row["refill_request_status"],
                    "provider_notes": row["provider_notes"],
                    "contact_for_refills": bool(row["contact_for_refills"]),
                    "created_at": row["medication_provider_created_at"],
                    "updated_at": row["medication_provider_updated_at"],
                    "provider": {
                        "provider_id": row["provider_entity_id"],
                        "name": row["provider_name"],
                        "phone_numbers": self._parse_json_array(row["provider_phone_numbers"]),
                        "preferred_phone_number": row["provider_preferred_phone_number"],
                        "fax_number": row["provider_fax_number"],
                        "address_line_1": row["provider_address_line_1"],
                        "address_line_2": row["provider_address_line_2"],
                        "city": row["provider_city"],
                        "state": row["provider_state"],
                        "zip": row["provider_zip"],
                    },
                }
            )
        return providers

    def _serialize_medication_pharmacies(self, medication_id: str) -> list[dict]:
        rows = self.conn.execute(
            """
            SELECT
                mp.id AS medication_pharmacy_id,
                mp.pharmacy_id AS linked_pharmacy_id,
                mp.pharmacy_status,
                mp.last_fill_date,
                mp.next_fill_date,
                mp.pickup_date,
                mp.last_fill_days_supply,
                mp.created_at AS medication_pharmacy_created_at,
                mp.updated_at AS medication_pharmacy_updated_at,
                p.id AS pharmacy_entity_id,
                p.name AS pharmacy_name,
                p.phone_numbers AS pharmacy_phone_numbers,
                p.preferred_phone_number AS pharmacy_preferred_phone_number,
                p.fax_number AS pharmacy_fax_number,
                p.address_line_1 AS pharmacy_address_line_1,
                p.address_line_2 AS pharmacy_address_line_2,
                p.city AS pharmacy_city,
                p.state AS pharmacy_state,
                p.zip AS pharmacy_zip
            FROM medication_pharmacies AS mp
            INNER JOIN pharmacies AS p ON p.id = mp.pharmacy_id
            WHERE mp.medication_id = ?
            ORDER BY mp.created_at ASC
            """,
            (medication_id,),
        ).fetchall()
        pharmacies = []
        for row in rows:
            refill_rows = self.conn.execute(
                """
                SELECT *
                FROM medication_pharmacy_refills
                WHERE medication_pharmacy_id = ?
                ORDER BY created_at ASC
                """,
                (row["medication_pharmacy_id"],),
            ).fetchall()
            pharmacies.append(
                {
                    "medication_pharmacy_id": row["medication_pharmacy_id"],
                    "pharmacy_status": row["pharmacy_status"],
                    "last_fill_date": row["last_fill_date"],
                    "next_fill_date": row["next_fill_date"],
                    "pickup_date": row["pickup_date"],
                    "last_fill_days_supply": row["last_fill_days_supply"],
                    "created_at": row["medication_pharmacy_created_at"],
                    "updated_at": row["medication_pharmacy_updated_at"],
                    "refills": [
                        {
                            "refill_id": refill_row["id"],
                            "days_supply": refill_row["days_supply"],
                            "expiration_date": refill_row["expiration_date"],
                            "status": refill_row["status"],
                            "created_at": refill_row["created_at"],
                        }
                        for refill_row in refill_rows
                    ],
                    "pharmacy": {
                        "pharmacy_id": row["pharmacy_entity_id"],
                        "name": row["pharmacy_name"],
                        "phone_numbers": self._parse_json_array(row["pharmacy_phone_numbers"]),
                        "preferred_phone_number": row["pharmacy_preferred_phone_number"],
                        "fax_number": row["pharmacy_fax_number"],
                        "address_line_1": row["pharmacy_address_line_1"],
                        "address_line_2": row["pharmacy_address_line_2"],
                        "city": row["pharmacy_city"],
                        "state": row["pharmacy_state"],
                        "zip": row["pharmacy_zip"],
                    },
                }
            )
        return pharmacies

    def _serialize_barriers(self, case_id: str) -> list[dict]:
        rows = self.conn.execute(
            "SELECT * FROM barriers WHERE case_id = ? ORDER BY created_at ASC",
            (case_id,),
        ).fetchall()
        return [
            {
                "barrier_id": row["id"],
                "barrier_type": row["barrier_type"],
                "title": row["title"],
                "status": row["status"],
                "severity": row["severity"],
                "description": row["description"],
                "identified_at": row["identified_at"],
                "resolved_at": row["resolved_at"],
                "created_at": row["created_at"],
                "updated_at": row["updated_at"],
            }
            for row in rows
        ]

    def _serialize_tasks(self, case_id: str) -> list[dict]:
        rows = self.conn.execute(
            "SELECT * FROM tasks WHERE case_id = ? ORDER BY created_at ASC",
            (case_id,),
        ).fetchall()
        return [
            {
                "task_id": row["id"],
                "task_type": row["task_type"],
                "title": row["title"],
                "status": row["status"],
                "priority": row["priority"],
                "related_measure_ids": self._parse_json_array(row["related_measure_ids"]),
                "related_medication_ids": self._parse_json_array(row["related_medication_ids"]),
                "barrier_id": row["barrier_id"],
                "description": row["description"],
                "due_at": row["due_at"],
                "completed_at": row["completed_at"],
                "cancelled_at": row["cancelled_at"],
                "outcome": row["outcome"],
                "assigned_to": row["assigned_to"],
                "assigned_queue": row["assigned_queue"],
                "created_at": row["created_at"],
                "updated_at": row["updated_at"],
            }
            for row in rows
        ]

    def _row_to_domain(self, row: sqlite3.Row) -> Case:
        return Case(
            id=CaseId(UUID(row["id"])),
            member_id=UUID(row["member_id"]),
            referral_id=UUID(row["referral_id"]),
            status=CaseStatus(row["status"]),
            opened_at=datetime.fromisoformat(row["opened_at"]),
            closed_at=datetime.fromisoformat(row["closed_at"]) if row["closed_at"] else None,
            archived_at=datetime.fromisoformat(row["archived_at"]) if row["archived_at"] else None,
            closed_reason=row["closed_reason"],
            case_summary=row["case_summary"],
            priority=row["priority"],
            created_at=datetime.fromisoformat(row["created_at"]),
            updated_at=datetime.fromisoformat(row["updated_at"]),
        )

    @staticmethod
    def _parse_json_array(value: str | None) -> list:
        if not value:
            return []
        return json.loads(value)

    @staticmethod
    def _normalize_string(value: str | None) -> str | None:
        if value is None:
            return None
        stripped = value.strip()
        return stripped or None
