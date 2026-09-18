from datetime import timedelta

import cv2
import numpy as np
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import override_settings
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from accounts.models import User
from tenants.models import Room, Tenant
from violations.models import DormitoryRule, Violation, Warning
from .detector import Detection, LightweightDetector
from .models import DetectionCooldown, Incident
from .services import cooldown_allows


@override_settings(PASSWORD_HASHERS=["django.contrib.auth.hashers.MD5PasswordHasher"])
class MainWorkflowTests(APITestCase):
    def setUp(self):
        self.manager = User.objects.create_user(username="manager", password="StrongPass123!", role=User.Role.MANAGER)
        self.room = Room.objects.create(number="101", capacity=2)
        self.tenant = Tenant.objects.create(first_name="Alex", last_name="Rivera", room=self.room)
        self.rule = DormitoryRule.objects.create(code="R-001", title="No prohibited containers", category="Safety", description="Test rule")

    def authenticate(self):
        response = self.client.post("/api/auth/login/", {"username": "manager", "password": "StrongPass123!"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {response.data['token']}")

    def test_login_and_complete_incident_workflow(self):
        self.authenticate()
        created = self.client.post("/api/incidents/", {"incident_type": "manual", "details": "Noise after quiet hours", "room": self.room.id})
        self.assertEqual(created.status_code, status.HTTP_201_CREATED)
        incident_id = created.data["id"]

        blocked = self.client.post(f"/api/incidents/{incident_id}/assign/", {"tenant": self.tenant.id})
        self.assertEqual(blocked.status_code, status.HTTP_409_CONFLICT)
        verified = self.client.post(f"/api/incidents/{incident_id}/verify/", {"notes": "Checked by manager"})
        self.assertEqual(verified.status_code, status.HTTP_200_OK)
        assigned = self.client.post(f"/api/incidents/{incident_id}/assign/", {"tenant": self.tenant.id})
        self.assertEqual(assigned.status_code, status.HTTP_200_OK)

        warning = self.client.post("/api/warnings/", {
            "tenant": self.tenant.id, "rule": self.rule.id, "incident": incident_id, "message": "First warning",
        })
        self.assertEqual(warning.status_code, status.HTTP_201_CREATED)
        violation = self.client.post("/api/violations/", {
            "tenant": self.tenant.id, "rule": self.rule.id, "incident": incident_id,
            "description": "Verified violation", "action_taken": "Counselling",
        })
        self.assertEqual(violation.status_code, status.HTTP_201_CREATED)
        history = self.client.get(f"/api/tenants/{self.tenant.id}/history/")
        self.assertEqual(len(history.data["warnings"]), 1)
        self.assertEqual(len(history.data["violations"]), 1)

    def test_reference_numbers_are_created(self):
        incident = Incident.objects.create(incident_type=Incident.Type.MANUAL)
        warning = Warning.objects.create(tenant=self.tenant, rule=self.rule, message="Test", issued_by=self.manager)
        incident.status = Incident.Status.ASSIGNED
        incident.assigned_tenant = self.tenant
        incident.verified_by = self.manager
        incident.verified_at = timezone.now()
        incident.save()
        violation = Violation.objects.create(tenant=self.tenant, rule=self.rule, incident=incident, description="Test", recorded_by=self.manager)
        self.assertRegex(self.tenant.reference, r"^TEN-\d{4}-\d{4}$")
        self.assertRegex(incident.reference, r"^INC-\d{4}-\d{4}$")
        self.assertRegex(warning.reference, r"^WRN-\d{4}-\d{4}$")
        self.assertRegex(violation.reference, r"^VIO-\d{4}-\d{4}$")

    @override_settings(DETECTION_COOLDOWN_SECONDS=60)
    def test_duplicate_detection_cooldown(self):
        self.assertTrue(cooldown_allows("camera:1:person"))
        self.assertFalse(cooldown_allows("camera:1:person"))
        cooldown = DetectionCooldown.objects.get(key="camera:1:person")
        cooldown.last_triggered_at = timezone.now() - timedelta(seconds=61)
        cooldown.save()
        self.assertTrue(cooldown_allows("camera:1:person"))

    def test_room_capacity_is_enforced_by_api(self):
        self.authenticate()
        Tenant.objects.create(first_name="Sam", last_name="Lee", room=self.room)
        response = self.client.post("/api/tenants/", {"first_name": "Taylor", "last_name": "Kim", "room": self.room.id})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_invalid_filters_and_date_ranges_return_400(self):
        self.authenticate()
        paths = [
            "/api/incidents/?room=not-a-number",
            "/api/incidents/?status=unknown",
            "/api/warnings/?tenant=not-a-number",
            "/api/reports/summary/?date_from=not-a-date",
            "/api/reports/summary/?date_from=2026-08-20&date_to=2026-08-01",
        ]
        for path in paths:
            with self.subTest(path=path):
                self.assertEqual(self.client.get(path).status_code, status.HTTP_400_BAD_REQUEST)

    def test_inactive_relations_and_invalid_confidence_are_rejected(self):
        self.authenticate()
        inactive_room = Room.objects.create(number="Closed", capacity=2, is_active=False)
        tenant_response = self.client.post(
            "/api/tenants/", {"first_name": "Inactive", "last_name": "Room", "room": inactive_room.id}
        )
        self.assertEqual(tenant_response.status_code, status.HTTP_400_BAD_REQUEST)

        self.rule.is_active = False
        self.rule.save()
        warning = self.client.post(
            "/api/warnings/",
            {"tenant": self.tenant.id, "rule": self.rule.id, "message": "Should be blocked"},
        )
        self.assertEqual(warning.status_code, status.HTTP_400_BAD_REQUEST)

        incident = self.client.post(
            "/api/incidents/", {"incident_type": "manual", "confidence": 1.5, "details": "Invalid"}
        )
        self.assertEqual(incident.status_code, status.HTTP_400_BAD_REQUEST)

    def test_occupied_room_cannot_be_shrunk_or_deleted(self):
        self.authenticate()
        Tenant.objects.create(first_name="Sam", last_name="Lee", room=self.room)
        update = self.client.patch(f"/api/rooms/{self.room.id}/", {"capacity": 1})
        self.assertEqual(update.status_code, status.HTTP_400_BAD_REQUEST)
        delete = self.client.delete(f"/api/rooms/{self.room.id}/")
        self.assertEqual(delete.status_code, status.HTTP_409_CONFLICT)

    @override_settings(MAX_FRAME_UPLOAD_BYTES=4)
    def test_frame_upload_size_is_limited(self):
        self.authenticate()
        upload = SimpleUploadedFile("large.jpg", b"too-large", content_type="image/jpeg")
        response = self.client.post("/api/monitoring/detect-frame/", {"frame": upload}, format="multipart")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("frame", response.data)

    def test_frame_detection_saves_snapshot_and_suppresses_duplicate(self):
        self.authenticate()
        frame = np.zeros((240, 320, 3), dtype=np.uint8)
        frame[60:160, 90:190] = (0, 140, 255)
        encoded, image = cv2.imencode(".jpg", frame)
        self.assertTrue(encoded)

        def upload():
            return SimpleUploadedFile("cue.jpg", image.tobytes(), content_type="image/jpeg")

        first = self.client.post(
            "/api/monitoring/detect-frame/",
            {"frame": upload(), "room": self.room.id, "source_name": "Test camera"},
            format="multipart",
        )
        self.assertEqual(first.status_code, status.HTTP_200_OK)
        self.assertEqual(first.data["frame"], {"width": 320, "height": 240})
        self.assertIn("possible_fire", [item["incident_type"] for item in first.data["detections"]])
        self.assertEqual(len(first.data["incidents_created"]), 1)
        incident = Incident.objects.get(pk=first.data["incidents_created"][0]["id"])
        self.assertTrue(incident.snapshot.name)

        duplicate = self.client.post(
            "/api/monitoring/detect-frame/",
            {"frame": upload(), "room": self.room.id, "source_name": "Test camera"},
            format="multipart",
        )
        self.assertEqual(duplicate.status_code, status.HTTP_200_OK)
        self.assertEqual(duplicate.data["incidents_created"], [])

    def test_detection_deduplication_preserves_separate_objects(self):
        detections = [
            Detection("person", "person", 0.91, (10, 10, 80, 180), "yolo"),
            Detection("person", "person", 0.70, (12, 12, 78, 178), "yolo"),
            Detection("person", "person", 0.84, (150, 15, 220, 180), "yolo"),
        ]

        result = LightweightDetector._deduplicate(detections)

        self.assertEqual(len(result), 2)
        self.assertEqual([item.confidence for item in result], [0.91, 0.84])
