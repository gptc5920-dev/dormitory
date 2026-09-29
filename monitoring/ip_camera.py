"""Keep the latest frame from each active RTSP camera without reconnecting per request."""

import threading
import time

import cv2


IDLE_SECONDS = 12
FRAME_MAX_AGE_SECONDS = 2
FRAME_WAIT_SECONDS = 6
MAX_FRAME_WIDTH = 1280


class CameraFrameUnavailable(RuntimeError):
    pass


class CameraFrameSession:
    def __init__(self, url):
        self.url = url
        self.condition = threading.Condition()
        self.stop_event = threading.Event()
        self.frame = None
        self.frame_at = 0.0
        self.last_requested_at = 0.0
        self.running = False
        self.error = False
        self.closed = False

    def close(self):
        with self.condition:
            self.closed = True
            self.stop_event.set()
            self.condition.notify_all()

    def get_frame(self):
        deadline = time.monotonic() + FRAME_WAIT_SECONDS
        with self.condition:
            if self.closed:
                raise CameraFrameUnavailable("This camera connection has closed.")
            self.last_requested_at = time.monotonic()
            if not self.running:
                self.stop_event.clear()
                self.error = False
                self.running = True
                threading.Thread(target=self._read_frames, daemon=True).start()
            while True:
                now = time.monotonic()
                if self.frame is not None and now - self.frame_at <= FRAME_MAX_AGE_SECONDS:
                    return self.frame.copy()
                if self.error or self.stop_event.is_set() or now >= deadline:
                    raise CameraFrameUnavailable("No current camera frame is available.")
                self.condition.wait(timeout=deadline - now)

    def _read_frames(self):
        try:
            while not self.stop_event.is_set():
                with self.condition:
                    if time.monotonic() - self.last_requested_at > IDLE_SECONDS:
                        break
                capture = None
                try:
                    capture = cv2.VideoCapture()
                    opened = capture.open(self.url, cv2.CAP_FFMPEG, [
                        cv2.CAP_PROP_OPEN_TIMEOUT_MSEC, 5000,
                        cv2.CAP_PROP_READ_TIMEOUT_MSEC, 5000,
                    ])
                    if not opened:
                        raise CameraFrameUnavailable("The RTSP camera could not be opened.")
                    while not self.stop_event.is_set():
                        with self.condition:
                            if time.monotonic() - self.last_requested_at > IDLE_SECONDS:
                                return
                        ok, frame = capture.read()
                        if not ok or frame is None:
                            raise CameraFrameUnavailable("The RTSP camera stopped sending frames.")
                        height, width = frame.shape[:2]
                        if width > MAX_FRAME_WIDTH:
                            frame = cv2.resize(frame, (MAX_FRAME_WIDTH, max(1, round(height * MAX_FRAME_WIDTH / width))))
                        with self.condition:
                            self.frame = frame
                            self.frame_at = time.monotonic()
                            self.error = False
                            self.condition.notify_all()
                except (cv2.error, CameraFrameUnavailable):
                    with self.condition:
                        self.frame = None
                        self.error = True
                        self.condition.notify_all()
                    if self.stop_event.wait(1):
                        break
                finally:
                    if capture is not None:
                        capture.release()
        finally:
            with self.condition:
                self.frame = None
                self.running = False
                self.condition.notify_all()


class CameraFramePool:
    def __init__(self):
        self.lock = threading.Lock()
        self.sessions = {}

    def get_frame(self, source):
        with self.lock:
            session = self.sessions.get(source.pk)
            if session is None or session.url != source.stream_url:
                if session is not None:
                    session.close()
                session = CameraFrameSession(source.stream_url)
                self.sessions[source.pk] = session
        return session.get_frame()

    def remove(self, source_id):
        with self.lock:
            session = self.sessions.pop(source_id, None)
        if session is not None:
            session.close()


camera_frames = CameraFramePool()
