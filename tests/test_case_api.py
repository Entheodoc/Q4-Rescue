import importlib
import json
import os
import unittest

import psycopg
from fastapi.testclient import TestClient

import app.persistence.db as db
from postgres_support import get_test_database_url, reset_database


class CaseApiTests(unittest.TestCase):
    def setUp(self):
        self.database_url = reset_database(get_test_database_url())
        self.auth_token = "test-operator-token"
        self.auth_headers = {
            "Authorization": f"Bearer {self.auth_token}",
            "X-Request-ID": "test-request-id",
        }

        os.environ["Q4_RESCUE_ENV"] = "test"
        os.environ["Q4_RESCUE_DATABASE_URL"] = self.database_url
        os.environ["Q4_RESCUE_AUTH_ENABLED"] = "true"
        os.environ["Q4_RESCUE_AUTH_TOKENS"] = json.dumps(
            {
                self.auth_token: {
                    "subject": "case-operator",
                    "permissions": ["cases:read", "cases:detail", "cases:write"],
                },
                "summary-only-token": {
                    "subject": "case-summary-reader",
                    "permissions": ["cases:read"],
                },
            }
        )

        importlib.reload(db)
        self.app_module = importlib.import_module("app.main")
        self.app_module = importlib.reload(self.app_module)
        self.client_cm = TestClient(self.app_module.app)
        self.client = self.client_cm.__enter__()
        self.client.headers.update(self.auth_headers)

    def tearDown(self):
        self.client_cm.__exit__(None, None, None)
        for variable in (
            "Q4_RESCUE_ENV",
            "Q4_RESCUE_DATABASE_URL",
            "Q4_RESCUE_AUTH_ENABLED",
            "Q4_RESCUE_AUTH_TOKENS",
            "Q4_RESCUE_SERVICE_NAME",
            "Q4_RESCUE_SERVICE_VERSION",
            "Q4_RESCUE_LOG_LEVEL",
            "Q4_RESCUE_METRICS_ENABLED",
            "Q4_RESCUE_OTEL_ENABLED",
            "Q4_RESCUE_OTEL_EXPORTER_OTLP_ENDPOINT",
            "Q4_RESCUE_OTEL_EXPORTER_OTLP_HEADERS",
        ):
            os.environ.pop(variable, None)

    def _archive_case(self, case_id: str) -> None:
        start_response = self.client.put(
            f"/cases/{case_id}/status",
            json={"status": "in_progress"},
        )
        self.assertEqual(start_response.status_code, 200)

        close_response = self.client.put(
            f"/cases/{case_id}/status",
            json={"status": "closed", "closed_reason": "Resolved after outreach"},
        )
        self.assertEqual(close_response.status_code, 200)

        archive_response = self.client.delete(f"/cases/{case_id}")
        self.assertEqual(archive_response.status_code, 204)

    def test_create_list_and_prevent_duplicate_active_case(self):
        payload = {
            "member": {
                "health_plan_member_id": "member-123",
                "first_name": "Maria",
                "last_name": "Lopez",
                "birth_date": "1980-01-15",
                "sex": "F",
                "phone_number": "555-0101",
                "preferred_contact_method": "text",
                "preferred_language": "en",
                "supported_languages": ["en", "es"],
                "address_line_1": "123 Main St",
                "city": "Miami",
                "state": "FL",
                "zip": "33101",
                "pbp": "001",
                "active_status": "active",
            },
            "referral": {
                "referral_source": "payer_file",
                "received_at": "2026-03-11T00:00:00+00:00",
            },
            "case_summary": "Member needs adherence rescue",
            "priority": "high",
            "measures": [
                {
                    "measure_code": "STATIN",
                    "measure_name": "Statin Adherence",
                    "performance_year": 2026,
                    "pdc": 0.72,
                    "actionable_status": "actionable",
                    "target_threshold": 0.8,
                    "medications": [
                        {
                            "medication_name": "Atorvastatin",
                            "display_name": "Atorvastatin 10mg",
                            "providers": [
                                {
                                    "provider": {
                                        "name": "Dr. Smith",
                                        "phone_numbers": ["555-1111"],
                                        "preferred_phone_number": "555-1111",
                                    },
                                    "prescribing_role": "pcp",
                                    "is_current_prescriber": True,
                                    "refill_request_status": "pending",
                                    "contact_for_refills": True,
                                }
                            ],
                            "pharmacies": [
                                {
                                    "pharmacy": {
                                        "name": "CVS",
                                        "phone_numbers": ["555-2222"],
                                        "preferred_phone_number": "555-2222",
                                    },
                                    "pharmacy_status": "ready_for_fill",
                                    "last_fill_date": "2026-02-01",
                                    "next_fill_date": "2026-03-02",
                                    "pickup_date": "2026-02-03",
                                    "last_fill_days_supply": 30,
                                    "refills": [
                                        {
                                            "days_supply": 30,
                                            "expiration_date": "2026-06-01",
                                            "status": "available",
                                        }
                                    ],
                                }
                            ],
                        }
                    ],
                }
            ],
        }

        create_response = self.client.post("/cases/", json=payload)
        self.assertEqual(create_response.status_code, 201)
        created_case = create_response.json()
        self.assertEqual(created_case["member"]["health_plan_member_id"], "member-123")
        self.assertEqual(created_case["referral"]["referral_source"], "payer_file")
        self.assertEqual(created_case["referral"]["case_id"], created_case["id"])
        self.assertEqual(created_case["measures"][0]["measure_code"], "STATIN")
        self.assertEqual(
            created_case["measures"][0]["medications"][0]["providers"][0]["provider"]["name"],
            "Dr. Smith",
        )
        self.assertEqual(
            created_case["measures"][0]["medications"][0]["pharmacies"][0]["refills"][0]["days_supply"],
            30,
        )

        list_response = self.client.get("/cases")
        self.assertEqual(list_response.status_code, 200)
        case_summaries = list_response.json()
        self.assertEqual(len(case_summaries), 1)
        case_summary = case_summaries[0]
        self.assertEqual(case_summary["id"], created_case["id"])
        self.assertEqual(case_summary["measure_count"], 1)
        self.assertEqual(case_summary["member"]["health_plan_member_id"], "member-123")
        self.assertNotIn("measures", case_summary)
        self.assertNotIn("referral", case_summary)

        duplicate_response = self.client.post("/cases/", json=payload)
        self.assertEqual(duplicate_response.status_code, 409)
        self.assertEqual(
            duplicate_response.json()["detail"],
            "Active Case already exists for this member",
        )

    def test_status_update_can_close_case_with_reason(self):
        payload = {
            "member": {
                "health_plan_member_id": "member-456",
                "first_name": "Ana",
                "last_name": "Rivera",
                "preferred_language": "es",
                "supported_languages": ["es"],
            },
            "referral": {
                "referral_source": "manual",
                "received_at": "2026-03-11T00:00:00+00:00",
            },
            "measures": [
                {
                    "measure_code": "DIAB",
                    "measure_name": "Diabetes Medication Adherence",
                    "performance_year": 2026,
                }
            ],
        }

        create_response = self.client.post("/cases/", json=payload)
        self.assertEqual(create_response.status_code, 201)
        case_id = create_response.json()["id"]

        start_response = self.client.put(
            f"/cases/{case_id}/status",
            json={"status": "in_progress"},
        )
        self.assertEqual(start_response.status_code, 200)

        close_response = self.client.put(
            f"/cases/{case_id}/status",
            json={"status": "closed", "closed_reason": "Resolved after outreach"},
        )
        self.assertEqual(close_response.status_code, 200)
        self.assertEqual(close_response.json()["status"], "closed")

        get_response = self.client.get(f"/cases/{case_id}")
        self.assertEqual(get_response.status_code, 200)
        self.assertEqual(get_response.json()["closed_reason"], "Resolved after outreach")

    def test_create_rejects_duplicate_measure_code_year(self):
        payload = {
            "member": {
                "health_plan_member_id": "member-789",
                "first_name": "Luis",
                "last_name": "Perez",
            },
            "referral": {
                "referral_source": "manual",
            },
            "measures": [
                {
                    "measure_code": "STATIN",
                    "measure_name": "Statin Adherence",
                    "performance_year": 2026,
                },
                {
                    "measure_code": " statin ",
                    "measure_name": "Statin Adherence Duplicate",
                    "performance_year": 2026,
                },
            ],
        }

        response = self.client.post("/cases/", json=payload)
        self.assertEqual(response.status_code, 422)

    def test_metrics_endpoint_exposes_http_and_business_metrics(self):
        payload = {
            "member": {
                "health_plan_member_id": "member-metrics-123",
                "first_name": "Ana",
                "last_name": "Rivera",
            },
            "referral": {
                "referral_source": "manual",
            },
            "measures": [
                {
                    "measure_code": "STATIN",
                    "measure_name": "Statin Adherence",
                    "performance_year": 2026,
                }
            ],
        }

        create_response = self.client.post("/cases/", json=payload)
        self.assertEqual(create_response.status_code, 201)
        self.assertIn("X-Trace-ID", create_response.headers)

        metrics_response = self.client.get("/metrics")

        self.assertEqual(metrics_response.status_code, 200)
        self.assertIn("text/plain", metrics_response.headers["content-type"])
        metrics_text = metrics_response.text
        self.assertIn("q4_rescue_http_requests_total", metrics_text)
        self.assertIn('route="/cases/"', metrics_text)
        self.assertIn("q4_rescue_cases_created_total", metrics_text)
        self.assertIn("q4_rescue_service_operation_duration_seconds", metrics_text)
        self.assertIn("q4_rescue_db_operation_duration_seconds", metrics_text)

    def test_case_routes_require_authentication(self):
        self.client.headers.pop("Authorization", None)

        response = self.client.get("/cases")

        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json()["detail"], "Missing Authorization header")

    def test_case_detail_requires_detail_permission(self):
        payload = {
            "member": {
                "health_plan_member_id": "member-detail-123",
                "first_name": "Ana",
                "last_name": "Rivera",
            },
            "referral": {
                "referral_source": "manual",
            },
            "measures": [
                {
                    "measure_code": "STATIN",
                    "measure_name": "Statin Adherence",
                    "performance_year": 2026,
                }
            ],
        }

        create_response = self.client.post("/cases/", json=payload)
        self.assertEqual(create_response.status_code, 201)
        case_id = create_response.json()["id"]

        summary_reader_cm = TestClient(self.app_module.app)
        summary_reader = summary_reader_cm.__enter__()
        summary_reader.headers.update(
            {
                "Authorization": "Bearer summary-only-token",
                "X-Request-ID": "summary-only-request",
            }
        )
        try:
            summary_response = summary_reader.get("/cases")
            self.assertEqual(summary_response.status_code, 200)

            detail_response = summary_reader.get(f"/cases/{case_id}")
            self.assertEqual(detail_response.status_code, 403)
            self.assertIn("cases:detail", detail_response.json()["detail"])
        finally:
            summary_reader_cm.__exit__(None, None, None)

    def test_case_actions_write_audit_events(self):
        payload = {
            "member": {
                "health_plan_member_id": "member-audit-123",
                "first_name": "Luis",
                "last_name": "Perez",
            },
            "referral": {
                "referral_source": "manual",
            },
            "measures": [
                {
                    "measure_code": "STATIN",
                    "measure_name": "Statin Adherence",
                    "performance_year": 2026,
                }
            ],
        }

        create_response = self.client.post("/cases/", json=payload)
        self.assertEqual(create_response.status_code, 201)
        case_id = create_response.json()["id"]

        self.client.get("/cases")
        self.client.get(f"/cases/{case_id}")

        with psycopg.connect(self.database_url) as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT action, resource_id, actor_subject, request_id
                    FROM audit_events
                    ORDER BY created_at ASC
                    """
                )
                audit_rows = cursor.fetchall()

        audit_actions = [row[0] for row in audit_rows]
        self.assertEqual(
            audit_actions,
            ["case.create", "case.list", "case.detail.read"],
        )
        self.assertEqual(audit_rows[0][1], case_id)
        self.assertEqual(audit_rows[0][2], "case-operator")
        self.assertEqual(audit_rows[0][3], "test-request-id")

    def test_repeat_referral_reuses_member_and_preserves_canonical_data_on_sparse_update(self):
        initial_payload = {
            "member": {
                "health_plan_member_id": "member-merge-123",
                "first_name": "Maria",
                "last_name": "Lopez",
                "phone_number": "555-0101",
                "preferred_language": "en",
                "supported_languages": ["en", "es"],
                "address_line_1": "123 Main St",
                "city": "Miami",
                "state": "FL",
                "zip": "33101",
            },
            "referral": {
                "referral_source": "payer_file",
                "received_at": "2026-03-11T00:00:00+00:00",
            },
            "measures": [
                {
                    "measure_code": "STATIN",
                    "measure_name": "Statin Adherence",
                    "performance_year": 2026,
                }
            ],
        }

        first_response = self.client.post("/cases/", json=initial_payload)
        self.assertEqual(first_response.status_code, 201)
        first_case = first_response.json()
        self._archive_case(first_case["id"])

        sparse_followup_payload = {
            "member": {
                "health_plan_member_id": "member-merge-123",
                "first_name": "Maria",
                "last_name": "Lopez",
                "preferred_language": "es",
            },
            "referral": {
                "referral_source": "payer_file",
                "received_at": "2026-04-01T00:00:00+00:00",
            },
            "measures": [
                {
                    "measure_code": "RASA",
                    "measure_name": "RASA Adherence",
                    "performance_year": 2026,
                }
            ],
        }

        second_response = self.client.post("/cases/", json=sparse_followup_payload)
        self.assertEqual(second_response.status_code, 201)
        second_case = second_response.json()

        self.assertEqual(second_case["member"]["member_id"], first_case["member"]["member_id"])
        self.assertEqual(second_case["member"]["phone_number"], "555-0101")
        self.assertEqual(second_case["member"]["preferred_language"], "es")
        self.assertEqual(second_case["member"]["supported_languages"], ["en", "es"])
        self.assertEqual(second_case["member"]["address_line_1"], "123 Main St")
        self.assertEqual(second_case["member"]["city"], "Miami")
        self.assertEqual(second_case["member"]["state"], "FL")
        self.assertEqual(second_case["member"]["zip"], "33101")

    def test_provider_and_pharmacy_records_are_reused_and_preserve_richer_contact_data(self):
        initial_payload = {
            "member": {
                "health_plan_member_id": "member-shared-123",
                "first_name": "Ana",
                "last_name": "Rivera",
            },
            "referral": {
                "referral_source": "payer_file",
                "received_at": "2026-03-11T00:00:00+00:00",
            },
            "measures": [
                {
                    "measure_code": "STATIN",
                    "measure_name": "Statin Adherence",
                    "performance_year": 2026,
                    "medications": [
                        {
                            "medication_name": "Atorvastatin",
                            "providers": [
                                {
                                    "provider": {
                                        "name": "Dr. Shared",
                                        "phone_numbers": ["555-1111", "555-1112"],
                                        "preferred_phone_number": "555-1111",
                                        "fax_number": "555-1119",
                                        "address_line_1": "10 Clinic Way",
                                        "city": "Miami",
                                        "state": "FL",
                                        "zip": "33101",
                                    }
                                }
                            ],
                            "pharmacies": [
                                {
                                    "pharmacy": {
                                        "name": "CVS Shared",
                                        "phone_numbers": ["555-2222", "555-2223"],
                                        "preferred_phone_number": "555-2222",
                                        "fax_number": "555-2229",
                                        "address_line_1": "20 Pharmacy Ave",
                                        "city": "Miami",
                                        "state": "FL",
                                        "zip": "33101",
                                    }
                                }
                            ],
                        }
                    ],
                }
            ],
        }

        first_response = self.client.post("/cases/", json=initial_payload)
        self.assertEqual(first_response.status_code, 201)
        first_case = first_response.json()
        self._archive_case(first_case["id"])

        followup_payload = {
            "member": {
                "health_plan_member_id": "member-shared-123",
                "first_name": "Ana",
                "last_name": "Rivera",
            },
            "referral": {
                "referral_source": "payer_file",
                "received_at": "2026-04-01T00:00:00+00:00",
            },
            "measures": [
                {
                    "measure_code": "RASA",
                    "measure_name": "RASA Adherence",
                    "performance_year": 2026,
                    "medications": [
                        {
                            "medication_name": "Losartan",
                            "providers": [
                                {
                                    "provider": {
                                        "name": "Dr. Shared",
                                    }
                                }
                            ],
                            "pharmacies": [
                                {
                                    "pharmacy": {
                                        "name": "CVS Shared",
                                    }
                                }
                            ],
                        }
                    ],
                }
            ],
        }

        second_response = self.client.post("/cases/", json=followup_payload)
        self.assertEqual(second_response.status_code, 201)
        second_case = second_response.json()

        first_provider = first_case["measures"][0]["medications"][0]["providers"][0]["provider"]
        second_provider = second_case["measures"][0]["medications"][0]["providers"][0]["provider"]
        self.assertEqual(second_provider["provider_id"], first_provider["provider_id"])
        self.assertEqual(second_provider["phone_numbers"], ["555-1111", "555-1112"])
        self.assertEqual(second_provider["preferred_phone_number"], "555-1111")
        self.assertEqual(second_provider["fax_number"], "555-1119")
        self.assertEqual(second_provider["address_line_1"], "10 Clinic Way")

        first_pharmacy = first_case["measures"][0]["medications"][0]["pharmacies"][0]["pharmacy"]
        second_pharmacy = second_case["measures"][0]["medications"][0]["pharmacies"][0]["pharmacy"]
        self.assertEqual(second_pharmacy["pharmacy_id"], first_pharmacy["pharmacy_id"])
        self.assertEqual(second_pharmacy["phone_numbers"], ["555-2222", "555-2223"])
        self.assertEqual(second_pharmacy["preferred_phone_number"], "555-2222")
        self.assertEqual(second_pharmacy["fax_number"], "555-2229")
        self.assertEqual(second_pharmacy["address_line_1"], "20 Pharmacy Ave")

        with psycopg.connect(self.database_url) as conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT COUNT(*) FROM providers")
                provider_count = cursor.fetchone()[0]
                cursor.execute("SELECT COUNT(*) FROM pharmacies")
                pharmacy_count = cursor.fetchone()[0]

        self.assertEqual(provider_count, 1)
        self.assertEqual(pharmacy_count, 1)

    def test_create_is_idempotent_for_repeated_requests_with_same_key(self):
        payload = {
            "member": {
                "health_plan_member_id": "member-idem-123",
                "first_name": "Luis",
                "last_name": "Perez",
            },
            "referral": {
                "referral_source": "manual",
                "received_at": "2026-03-11T00:00:00+00:00",
            },
            "measures": [
                {
                    "measure_code": "STATIN",
                    "measure_name": "Statin Adherence",
                    "performance_year": 2026,
                }
            ],
        }

        first_response = self.client.post(
            "/cases/",
            json=payload,
            headers={**self.auth_headers, "Idempotency-Key": "case-create-123"},
        )
        self.assertEqual(first_response.status_code, 201)
        first_case = first_response.json()

        second_response = self.client.post(
            "/cases/",
            json=payload,
            headers={**self.auth_headers, "Idempotency-Key": "case-create-123"},
        )
        self.assertEqual(second_response.status_code, 201)
        self.assertEqual(second_response.json()["id"], first_case["id"])

        list_response = self.client.get("/cases")
        self.assertEqual(list_response.status_code, 200)
        self.assertEqual(len(list_response.json()), 1)

        with psycopg.connect(self.database_url) as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    "SELECT COUNT(*) FROM idempotency_keys WHERE route = %s AND key = %s",
                    ("POST:/cases", "case-create-123"),
                )
                idempotency_count = cursor.fetchone()[0]

        self.assertEqual(idempotency_count, 1)
