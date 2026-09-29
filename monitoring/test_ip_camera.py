import threading
import time
from unittest.mock import patch

import numpy as np
from django.test import SimpleTestCase

from .ip_camera import CameraFrameSession, CameraFrameUnavailable


class FakeCapture:
    def __init__(self):
        self.opens = 0
        self.released = threading.Event()
        self.frame_number = 0

    def open(self, url, backend, options):
        self.opens += 1
        return True

    def read(self):
        time.sleep(0.01)
        self.frame_number += 1
        return True, np.full((16, 16, 3), self.frame_number % 255, dtype=np.uint8)

    def release(self):
        self.released.set()


class CameraFrameSessionTests(SimpleTestCase):
    def test_reuses_connection_and_returns_newest_frame(self):
        capture = FakeCapture()
        session = CameraFrameSession("rtsp://camera/stream")
        with patch("monitoring.ip_camera.cv2.VideoCapture", return_value=capture):
            first = session.get_frame()
            time.sleep(0.05)
            second = session.get_frame()
            self.assertEqual(capture.opens, 1)
            self.assertGreater(int(second[0, 0, 0]), int(first[0, 0, 0]))
            session.close()
            self.assertTrue(capture.released.wait(1))
            with self.assertRaises(CameraFrameUnavailable):
                session.get_frame()
