import os
import unittest
from unittest.mock import patch

import psycopg

import app.persistence.db as db
from postgres_support import get_test_database_url, reset_database


class MigrationRuntimeTests(unittest.TestCase):
    def tearDown(self):
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

    def test_init_db_uses_alembic_upgrade_for_postgres(self):
        os.environ["Q4_RESCUE_ENV"] = "test"
        os.environ["Q4_RESCUE_AUTH_ENABLED"] = "false"
        os.environ["Q4_RESCUE_DATABASE_URL"] = (
            "postgresql://user:pass@localhost:5432/q4_rescue"
        )

        with patch("app.persistence.db.upgrade_database") as upgrade_database:
            db.init_db()

        upgrade_database.assert_called_once_with(
            "postgresql+psycopg://user:pass@localhost:5432/q4_rescue"
        )

    def test_init_db_bootstraps_expected_tables_for_postgres(self):
        database_url = reset_database(get_test_database_url())
        os.environ["Q4_RESCUE_ENV"] = "test"
        os.environ["Q4_RESCUE_AUTH_ENABLED"] = "false"
        os.environ["Q4_RESCUE_DATABASE_URL"] = database_url

        db.init_db()

        with psycopg.connect(database_url) as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT table_name
                    FROM information_schema.tables
                    WHERE table_schema = 'public'
                    """
                )
                tables = {row[0] for row in cursor.fetchall()}

        self.assertTrue(
            {
                "members",
                "referrals",
                "cases",
                "measures",
                "providers",
                "pharmacies",
                "audit_events",
                "idempotency_keys",
                "alembic_version",
            }.issubset(tables)
        )
