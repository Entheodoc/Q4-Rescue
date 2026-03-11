import importlib
import os
import sqlite3
import tempfile
import unittest
from pathlib import Path

from fastapi.testclient import TestClient

import app.persistence.db as db


class CaseApiTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.db_path = Path(self.temp_dir.name) / "test.sqlite3"
        os.environ["Q4_RESCUE_DB_PATH"] = str(self.db_path)

        importlib.reload(db)
        self.app_module = importlib.import_module("app.main")
        self.app_module = importlib.reload(self.app_module)
        self.client_cm = TestClient(self.app_module.app)
        self.client = self.client_cm.__enter__()

    def tearDown(self):
        self.client_cm.__exit__(None, None, None)
        os.environ.pop("Q4_RESCUE_DB_PATH", None)
        self.temp_dir.cleanup()

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
        self.assertEqual(len(list_response.json()), 1)

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


class LegacySchemaMigrationTests(unittest.TestCase):
    def test_init_db_migrates_measure_cases_table_to_normalized_model(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            db_path = Path(temp_dir) / "legacy.sqlite3"
            os.environ["Q4_RESCUE_DB_PATH"] = str(db_path)

            try:
                with sqlite3.connect(db_path) as conn:
                    conn.execute(
                        """
                        CREATE TABLE measure_cases (
                            id TEXT PRIMARY KEY,
                            member_id TEXT NOT NULL,
                            measure_type TEXT NOT NULL,
                            year INTEGER NOT NULL,
                            current_pdc REAL NOT NULL,
                            target_pdc REAL NOT NULL,
                            status TEXT NOT NULL,
                            created_at TEXT NOT NULL,
                            updated_at TEXT NOT NULL
                        )
                        """
                    )
                    conn.execute(
                        """
                        INSERT INTO measure_cases (
                            id,
                            member_id,
                            measure_type,
                            year,
                            current_pdc,
                            target_pdc,
                            status,
                            created_at,
                            updated_at
                        )
                        VALUES (
                            'legacy-case-1',
                            'member-123',
                            'STATIN',
                            2026,
                            0.71,
                            0.8,
                            'open',
                            '2026-03-11T00:00:00+00:00',
                            '2026-03-11T00:00:00+00:00'
                        )
                        """
                    )

                importlib.reload(db)
                db.init_db()

                with sqlite3.connect(db_path) as conn:
                    tables = {
                        row[0]
                        for row in conn.execute(
                            "SELECT name FROM sqlite_master WHERE type = 'table'"
                        ).fetchall()
                    }
                    self.assertIn("members", tables)
                    self.assertIn("referrals", tables)
                    self.assertIn("cases", tables)
                    self.assertIn("measures", tables)
                    self.assertNotIn("measure_cases", tables)

                    self.assertEqual(conn.execute("SELECT COUNT(*) FROM members").fetchone()[0], 1)
                    self.assertEqual(conn.execute("SELECT COUNT(*) FROM referrals").fetchone()[0], 1)
                    self.assertEqual(conn.execute("SELECT COUNT(*) FROM cases").fetchone()[0], 1)
                    self.assertEqual(conn.execute("SELECT COUNT(*) FROM measures").fetchone()[0], 1)

                    migrated_measure = conn.execute(
                        "SELECT measure_code, performance_year, pdc FROM measures"
                    ).fetchone()
                    self.assertEqual(migrated_measure[0], "STATIN")
                    self.assertEqual(migrated_measure[1], 2026)
                    self.assertEqual(migrated_measure[2], 0.71)
            finally:
                os.environ.pop("Q4_RESCUE_DB_PATH", None)
