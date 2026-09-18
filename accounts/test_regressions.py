from django.test import override_settings
from django.utils import timezone
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase

from accounts.models import User
from config.references import next_reference
from monitoring.models import Incident
from tenants.models import Room, Tenant


@override_settings(PASSWORD_HASHERS=["django.contrib.auth.hashers.MD5PasswordHasher"])
class AuditRegressionTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="admin", password="Original123!", role="admin")
        self.token = Token.objects.create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.token.key}")

    def test_password_change_revokes_token(self):
        response = self.client.patch(f"/api/users/{self.user.pk}/", {"password": "Changed123!"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.client.get("/api/auth/me/").status_code, 401)
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password("Changed123!"))

    def test_nonfinite_confidence_is_rejected_without_saving(self):
        incident = Incident.objects.create(incident_type="manual", confidence=0.5)
        for value in ["NaN", "Infinity", "-Infinity"]:
            with self.subTest(value=value):
                response = self.client.patch(f"/api/incidents/{incident.pk}/", {"confidence": value})
                self.assertEqual(response.status_code, 400)
                incident.refresh_from_db()
                self.assertEqual(incident.confidence, 0.5)

    def test_date_bounds_and_effective_report_range(self):
        for endpoint in ["/api/incidents/", "/api/reports/summary/"]:
            for field in ["date_from", "date_to"]:
                for value in ["0001-01-01", "9999-12-31"]:
                    with self.subTest(endpoint=endpoint, field=field, value=value):
                        self.assertEqual(self.client.get(endpoint, {field: value}).status_code, 400)
        self.assertEqual(self.client.get("/api/reports/summary/", {"date_from": "9998-01-01"}).status_code, 400)
        response = self.client.get("/api/reports/summary/", {"date_to": "0002-01-01"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["date_from"], response.data["date_to"])

    def test_occupied_room_deactivation_and_ordered_pagination(self):
        room = Room.objects.create(number="101")
        tenant = Tenant.objects.create(first_name="Test", last_name="Tenant", room=room)
        self.assertEqual(self.client.patch(f"/api/rooms/{room.pk}/", {"is_active": False}).status_code, 400)
        self.assertEqual(self.client.patch(f"/api/tenants/{tenant.pk}/", {"phone": "123"}).status_code, 200)
        import warnings
        from django.core.paginator import UnorderedObjectListWarning
        with warnings.catch_warnings():
            warnings.simplefilter("error", UnorderedObjectListWarning)
            self.assertEqual(self.client.get("/api/rooms/", {"page_size": 1}).status_code, 200)
        tenant.is_active = False
        tenant.save()
        self.assertEqual(self.client.patch(f"/api/rooms/{room.pk}/", {"is_active": False}).status_code, 200)

    def test_numeric_references_and_reserved_numbers(self):
        stem = f"INC-{timezone.localdate().year}-"
        for suffix in ["9999", "10000"]:
            Incident.objects.create(reference=stem + suffix, incident_type="manual")
        self.assertEqual(next_reference(Incident, "INC"), stem + "10001")
        self.assertEqual(next_reference(Incident, "INC"), stem + "10002")
