from unittest.mock import patch

import numpy as np
from rest_framework.test import APITestCase

from accounts.models import User
from .models import CameraSource


class NetworkCameraTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="camera-manager", role=User.Role.MANAGER)
        self.client.force_authenticate(self.user)
        self.url = "rtsp://operator:secret@192.168.1.100:554/stream"
        self.source = CameraSource.objects.create(name="Entrance", location="Lobby", source_type="ip_camera", stream_url=self.url)
        self.endpoint = f"/api/camera-sources/{self.source.pk}/"

    def test_credentials_are_write_only_and_preserved_on_edit(self):
        response = self.client.patch(self.endpoint, {"name": "Front entrance"})
        self.assertEqual(response.status_code, 200)
        self.assertNotIn("stream_url", response.data)
        self.assertTrue(response.data["has_stream_url"])
        self.source.refresh_from_db()
        self.assertEqual(self.source.stream_url, self.url)

    def test_rejects_missing_or_unsupported_streams(self):
        for url in ["", "file:///etc/passwd", "http://localhost", "rtsp://host:bad/stream"]:
            response = self.client.patch(self.endpoint, {"stream_url": url})
            self.assertEqual(response.status_code, 400)

    @patch("monitoring.views.detector.detect")
    @patch("monitoring.views.cv2.VideoCapture")
    def test_preview_and_detection_release_capture(self, capture_type, detect):
        capture = capture_type.return_value
        capture.read.return_value = (True, np.zeros((16, 16, 3), dtype=np.uint8))
        detect.return_value = []
        response = self.client.post(self.endpoint + "snapshot/", {"detect": False}, format="json")
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.data["image"].startswith("data:image/jpeg;base64,"))
        detect.assert_not_called()
        capture.release.assert_called_once()
        response = self.client.post(self.endpoint + "snapshot/", {"detect": True}, format="json")
        self.assertEqual(response.status_code, 200)
        detect.assert_called_once()

    @patch("monitoring.views.cv2.VideoCapture")
    def test_unreachable_camera_and_access_controls(self, capture_type):
        capture_type.return_value.open.return_value = False
        response = self.client.post(self.endpoint + "snapshot/")
        self.assertEqual(response.status_code, 502)
        self.assertNotIn("secret", str(response.data))
        capture_type.return_value.release.assert_called_once()
        self.source.is_enabled = False
        self.source.save()
        self.assertEqual(self.client.post(self.endpoint + "snapshot/").status_code, 400)
        self.client.force_authenticate(None)
        self.assertIn(self.client.post(self.endpoint + "snapshot/").status_code, [401, 403])
