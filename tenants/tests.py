from django.core.exceptions import ValidationError
from django.db import connection
from django.db.models import Count, Q
from django.test import TestCase
from django.test.utils import CaptureQueriesContext
from django.core.files.uploadedfile import SimpleUploadedFile
from unittest.mock import patch
from rest_framework.test import APITestCase
import numpy as np

from accounts.models import User

from .models import Room, Tenant, TenantFace
from .serializers import RoomSerializer
from .face_recognition import FaceImageError, identify_faces


class TenantModelTests(TestCase):
    def test_room_capacity(self):
        room = Room.objects.create(number="T1", capacity=1)
        Tenant.objects.create(first_name="First", last_name="Tenant", room=room)
        with self.assertRaises(ValidationError):
            Tenant.objects.create(first_name="Second", last_name="Tenant", room=room)

    def test_room_list_uses_annotated_occupancy_without_n_plus_one_queries(self):
        for index in range(5):
            room = Room.objects.create(number=f"Q{index}", capacity=2)
            Tenant.objects.create(first_name="Query", last_name=str(index), room=room)
        queryset = Room.objects.annotate(
            occupancy=Count("tenants", filter=Q(tenants__is_active=True))
        )
        with CaptureQueriesContext(connection) as queries:
            data = RoomSerializer(queryset, many=True).data
        self.assertEqual(len(data), 5)
        self.assertEqual(len(queries), 1)


class TenantFaceApiTests(APITestCase):
    def setUp(self):
        self.manager = User.objects.create_user(username="manager", password="StrongPass123!")
        self.tenant = Tenant.objects.create(first_name="Alex", last_name="Rivera", room=Room.objects.create(number="F1"))
        self.url = f"/api/tenants/{self.tenant.pk}/face-photo/"

    def test_face_photo_is_private_and_can_be_replaced_or_removed(self):
        upload = SimpleUploadedFile("face.jpg", b"photo", content_type="image/jpeg")
        self.assertEqual(self.client.post(self.url, {"photo": upload}, format="multipart").status_code, 401)
        self.assertEqual(self.client.get(self.url).status_code, 401)
        self.client.force_authenticate(self.manager)
        with patch("tenants.views.enroll_face", return_value=(b"private-jpeg", [0.1, 0.2])):
            created = self.client.post(self.url, {"photo": SimpleUploadedFile("face.jpg", b"photo", content_type="image/jpeg")}, format="multipart")
        self.assertEqual(created.status_code, 200)
        self.assertEqual(bytes(TenantFace.objects.get(tenant=self.tenant).photo), b"private-jpeg")
        listing = self.client.get("/api/tenants/")
        self.assertTrue(listing.data["results"][0]["has_face_photo"])
        self.assertNotIn("embedding", listing.data["results"][0])
        photo = self.client.get(self.url)
        self.assertEqual(photo.data["image"], "data:image/jpeg;base64,cHJpdmF0ZS1qcGVn")
        self.assertEqual(photo["Cache-Control"], "no-store")
        self.assertEqual(self.client.delete(self.url).status_code, 204)
        self.assertFalse(TenantFace.objects.filter(tenant=self.tenant).exists())

    def test_invalid_upload_does_not_create_face(self):
        self.client.force_authenticate(self.manager)
        bad = SimpleUploadedFile("face.txt", b"not an image", content_type="text/plain")
        response = self.client.post(self.url, {"photo": bad}, format="multipart")
        self.assertEqual(response.status_code, 400)
        self.assertFalse(TenantFace.objects.exists())

    def test_face_check_requires_one_face_and_does_not_enroll(self):
        url = "/api/tenants/check-face/"
        upload = lambda: SimpleUploadedFile("face.jpg", b"photo", content_type="image/jpeg")
        self.assertEqual(self.client.post(url, {"photo": upload()}, format="multipart").status_code, 401)
        self.client.force_authenticate(self.manager)
        with patch("tenants.views.enroll_face", side_effect=FaceImageError("Use a clear photo with exactly one visible face.")):
            invalid = self.client.post(url, {"photo": upload()}, format="multipart")
        self.assertEqual(invalid.status_code, 400)
        self.assertFalse(TenantFace.objects.exists())
        with patch("tenants.views.enroll_face", return_value=(b"private-jpeg", [0.1, 0.2])):
            valid = self.client.post(url, {"photo": upload()}, format="multipart")
        self.assertEqual(valid.status_code, 200)
        self.assertTrue(valid.data["face_detected"])
        self.assertEqual(valid["Cache-Control"], "no-store")
        self.assertFalse(TenantFace.objects.exists())

    def test_each_tenant_can_enroll_a_separate_face(self):
        second = Tenant.objects.create(first_name="Sam", last_name="Lee", room=self.tenant.room)
        self.client.force_authenticate(self.manager)
        for tenant, embedding in ((self.tenant, [0.1, 0.2]), (second, [0.3, 0.4])):
            with patch("tenants.views.enroll_face", return_value=(b"private-jpeg", embedding)):
                result = self.client.post(
                    f"/api/tenants/{tenant.pk}/face-photo/",
                    {"photo": SimpleUploadedFile("face.jpg", b"photo", content_type="image/jpeg")},
                    format="multipart",
                )
            self.assertEqual(result.status_code, 200)
        self.assertEqual(TenantFace.objects.count(), 2)
        self.assertEqual(TenantFace.objects.get(tenant=second).embedding, [0.3, 0.4])

    def test_camera_match_is_only_a_suggestion_for_active_tenants(self):
        TenantFace.objects.create(tenant=self.tenant, photo=b"private", embedding=[0.7, 0.3])
        inactive = Tenant.objects.create(first_name="Inactive", last_name="Resident", room=self.tenant.room, is_active=False)
        TenantFace.objects.create(tenant=inactive, photo=b"private", embedding=[0.9, 0.1])

        class Recognizer:
            def alignCrop(self, frame, face):
                return frame

            def feature(self, frame):
                return np.asarray([[1.0, 0.0]], dtype=np.float32)

            def match(self, feature, embedding, distance_type):
                return float(embedding[0, 0])

        face = np.asarray([[10, 10, 20, 20] + [0] * 11], dtype=np.float32)
        with patch("tenants.face_recognition._models", return_value=(object(), Recognizer())), patch("tenants.face_recognition._faces", return_value=face):
            matches = identify_faces(np.zeros((100, 100, 3), dtype=np.uint8))
        self.assertEqual(matches[0]["status"], "possible_match")
        self.assertEqual(matches[0]["tenant_id"], self.tenant.pk)
        self.assertEqual(matches[0]["box"], [10, 10, 30, 30])
        self.tenant.is_active = False
        self.tenant.save()
        with patch("tenants.face_recognition._models", return_value=(object(), Recognizer())), patch("tenants.face_recognition._faces", return_value=face):
            unknown = identify_faces(np.zeros((100, 100, 3), dtype=np.uint8))
        self.assertEqual(unknown[0]["status"], "unknown")
        self.assertIsNone(unknown[0]["tenant_id"])
