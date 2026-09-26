from unittest.mock import patch
from concurrent.futures import ThreadPoolExecutor
import os
from pathlib import Path
import runpy

from django.core.exceptions import ImproperlyConfigured
from django.db import OperationalError, connections
from django.test import SimpleTestCase, TransactionTestCase, skipUnlessDBFeature
from rest_framework.test import APITestCase

from config.references import next_reference
from monitoring.models import Incident


class HealthCheckTests(APITestCase):
    def test_health_is_available_without_login(self):
        result = self.client.get("/api/health/")
        self.assertEqual(result.status_code, 200)
        self.assertEqual(result.json(), {"status": "ok"})

    def test_database_failure_is_unhealthy_without_leaking_details(self):
        with patch("config.health.connection.cursor", side_effect=OperationalError("private database details")):
            result = self.client.get("/api/health/")
        self.assertEqual(result.status_code, 503)
        self.assertEqual(result.json(), {"status": "unavailable"})


class ProductionSettingsTests(SimpleTestCase):
    def read_settings(self, **environment):
        with patch.dict(os.environ, environment, clear=True):
            return runpy.run_path(str(Path(__file__).resolve().parents[1] / "config" / "settings.py"))

    def test_mysql_is_default_and_strict(self):
        database = self.read_settings()["DATABASES"]["default"]
        self.assertEqual(database["ENGINE"], "django.db.backends.mysql")
        self.assertEqual(database["OPTIONS"]["charset"], "utf8mb4")
        self.assertIn("STRICT_TRANS_TABLES", database["OPTIONS"]["init_command"])

    def test_local_database_defaults_and_environment_precedence(self):
        with patch.object(Path, "is_file", return_value=True), patch.object(
            Path, "read_text", return_value='{"USER":"root","PORT":"3307","PASSWORD":""}'
        ):
            database = self.read_settings()["DATABASES"]["default"]
            self.assertEqual(database["USER"], "root")
            self.assertEqual(database["PORT"], "3307")
            self.assertEqual(database["PASSWORD"], "")
            overridden = self.read_settings(MYSQL_USER="custom", MYSQL_PORT="3308")["DATABASES"]["default"]
            self.assertEqual(overridden["USER"], "custom")
            self.assertEqual(overridden["PORT"], "3308")

    def test_production_ignores_local_database_file(self):
        with patch.object(Path, "read_text") as read_local:
            database = self.read_settings(DJANGO_DEBUG="0", DJANGO_SECRET_KEY="x" * 64)["DATABASES"]["default"]
            read_local.assert_not_called()
            self.assertEqual(database["USER"], "dormitory")
            self.assertEqual(database["PORT"], "3306")

    def test_production_requires_secret_and_mysql(self):
        with self.assertRaises(ImproperlyConfigured):
            self.read_settings(DJANGO_DEBUG="0")
        with self.assertRaises(ImproperlyConfigured):
            self.read_settings(DJANGO_DEBUG="0", DJANGO_SECRET_KEY="x" * 64, DB_ENGINE="sqlite")
        settings = self.read_settings(DJANGO_DEBUG="0", DJANGO_SECRET_KEY="x" * 64)
        self.assertTrue(settings["SESSION_COOKIE_SECURE"])
        self.assertTrue(settings["CSRF_COOKIE_SECURE"])
        self.assertTrue(settings["SECURE_SSL_REDIRECT"])


class MySQLReferenceTests(TransactionTestCase):
    @skipUnlessDBFeature("has_select_for_update")
    def test_concurrent_reference_reservations_are_unique(self):
        def reserve(_):
            try:
                return next_reference(Incident, "INC")
            finally:
                connections.close_all()

        with ThreadPoolExecutor(max_workers=4) as executor:
            references = list(executor.map(reserve, range(20)))
        self.assertEqual(len(set(references)), 20)
