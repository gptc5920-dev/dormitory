from unittest.mock import Mock, patch

import numpy as np
from django.test import TestCase, override_settings

from accounts.models import User
from .models import VideoJob
from .services import process_video_job


@override_settings(VIDEO_SAMPLE_EVERY_FRAMES=15, VIDEO_MAX_SAMPLED_FRAMES=3)
class VideoJobRegressionTests(TestCase):
    def setUp(self):
        self.user = User.objects.create(username="video-manager", role="manager")
        self.job = VideoJob.objects.create(video="test.mp4", created_by=self.user)
        self.capture = Mock()
        self.capture.isOpened.return_value = True

    def process(self):
        with patch("monitoring.services.cv2.VideoCapture", return_value=self.capture), patch(
            "monitoring.services.detector.detect", return_value=[]
        ) as detect:
            process_video_job(self.job)
        self.job.refresh_from_db()
        return detect

    def test_short_video_analyzes_first_frame(self):
        frame = np.zeros((16, 16, 3), dtype=np.uint8)
        self.capture.read.side_effect = [(True, frame), (False, None)]
        detect = self.process()
        self.assertEqual(self.job.status, VideoJob.Status.COMPLETED)
        self.assertEqual(self.job.frames_processed, 1)
        detect.assert_called_once()
        self.capture.release.assert_called_once()

    def test_video_without_decodable_frames_fails(self):
        self.capture.read.return_value = (False, None)
        self.process()
        self.assertEqual(self.job.status, VideoJob.Status.FAILED)
        self.assertTrue(self.job.error)
        self.assertIsNotNone(self.job.completed_at)
        self.capture.release.assert_called_once()

    def test_unopenable_video_releases_capture(self):
        self.capture.isOpened.return_value = False
        self.process()
        self.assertEqual(self.job.status, VideoJob.Status.FAILED)
        self.capture.release.assert_called_once()

    def test_capture_initialization_failure_marks_job_failed(self):
        with patch("monitoring.services.cv2.VideoCapture", side_effect=RuntimeError("Cannot open video")):
            process_video_job(self.job)
        self.job.refresh_from_db()
        self.assertEqual(self.job.status, VideoJob.Status.FAILED)
        self.assertIsNotNone(self.job.completed_at)

    def test_sampling_respects_frame_limit(self):
        frame = np.zeros((16, 16, 3), dtype=np.uint8)
        self.capture.read.return_value = (True, frame)
        detect = self.process()
        self.assertEqual(detect.call_count, 3)
        self.assertEqual(self.job.frames_processed, 3)
        self.assertEqual(self.capture.read.call_count, 31)
