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
            "member_id": "member-123",
            "measure_type": "statin",
            "year": 2026,
            "current_pdc": 0.72,
        }

        create_response = self.client.post("/cases/", json=payload)
        self.assertEqual(create_response.status_code, 201)
        created_case = create_response.json()
        self.assertEqual(created_case["measure_type"], "STATIN")

        list_response = self.client.get("/cases")
        self.assertEqual(list_response.status_code, 200)
        self.assertEqual(len(list_response.json()), 1)

        duplicate_response = self.client.post("/cases/", json=payload)
        self.assertEqual(duplicate_response.status_code, 409)
        self.assertEqual(
            duplicate_response.json()["detail"],
            "Active Case already exists for this member/measure/year",
        )


class LegacySchemaMigrationTests(unittest.TestCase):
    def test_init_db_migrates_measure_cases_table_to_cases(self):
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
                            'case-1',
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
                    self.assertIn("cases", tables)
                    self.assertNotIn("measure_cases", tables)

                    count = conn.execute("SELECT COUNT(*) FROM cases").fetchone()[0]
                    self.assertEqual(count, 1)
            finally:
                os.environ.pop("Q4_RESCUE_DB_PATH", None)
