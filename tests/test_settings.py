import os
import unittest

from app.settings import get_settings, validate_runtime_settings


class SettingsTests(unittest.TestCase):
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

    def test_postgres_url_is_normalized_for_sqlalchemy(self):
        os.environ["Q4_RESCUE_DATABASE_URL"] = "postgresql://user:pass@localhost:5432/q4_rescue"

        settings = get_settings()

        self.assertEqual(
            settings.sqlalchemy_database_url,
            "postgresql+psycopg://user:pass@localhost:5432/q4_rescue",
        )

    def test_validate_runtime_settings_requires_database_url(self):
        os.environ["Q4_RESCUE_AUTH_ENABLED"] = "false"

        with self.assertRaisesRegex(RuntimeError, "Q4_RESCUE_DATABASE_URL is required"):
            validate_runtime_settings()

    def test_validate_runtime_settings_requires_postgres_url(self):
        os.environ["Q4_RESCUE_AUTH_ENABLED"] = "false"
        os.environ["Q4_RESCUE_DATABASE_URL"] = "mysql://user:pass@localhost:3306/q4_rescue"

        with self.assertRaisesRegex(RuntimeError, "must be a Postgres connection string"):
            validate_runtime_settings()

    def test_validate_runtime_settings_allows_postgres_backend(self):
        os.environ["Q4_RESCUE_AUTH_ENABLED"] = "false"
        os.environ["Q4_RESCUE_DATABASE_URL"] = (
            "postgresql://user:pass@localhost:5432/q4_rescue"
        )

        validate_runtime_settings()

    def test_get_settings_loads_observability_configuration(self):
        os.environ["Q4_RESCUE_DATABASE_URL"] = "postgresql://user:pass@localhost:5432/q4_rescue"
        os.environ["Q4_RESCUE_SERVICE_NAME"] = "q4-rescue-custom"
        os.environ["Q4_RESCUE_SERVICE_VERSION"] = "1.2.3"
        os.environ["Q4_RESCUE_LOG_LEVEL"] = "debug"
        os.environ["Q4_RESCUE_METRICS_ENABLED"] = "false"
        os.environ["Q4_RESCUE_OTEL_ENABLED"] = "true"
        os.environ["Q4_RESCUE_OTEL_EXPORTER_OTLP_ENDPOINT"] = "http://collector:4318/v1/traces"
        os.environ["Q4_RESCUE_OTEL_EXPORTER_OTLP_HEADERS"] = '{"api-key":"secret"}'

        settings = get_settings()

        self.assertEqual(settings.service_name, "q4-rescue-custom")
        self.assertEqual(settings.service_version, "1.2.3")
        self.assertEqual(settings.log_level, "debug")
        self.assertFalse(settings.metrics_enabled)
        self.assertTrue(settings.otel_enabled)
        self.assertEqual(
            settings.otel_exporter_otlp_endpoint,
            "http://collector:4318/v1/traces",
        )
        self.assertEqual(settings.otel_exporter_otlp_headers, {"api-key": "secret"})
