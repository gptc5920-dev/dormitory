"""Private tenant face enrollment and tentative matching for manager review."""

from pathlib import Path
from functools import lru_cache
from threading import Lock

import cv2
import numpy as np
from django.conf import settings

from .models import TenantFace


MODEL_DIR = Path(settings.BASE_DIR) / "face_models"
DETECTOR_MODEL = MODEL_DIR / "face_detection_yunet_2023mar.onnx"
RECOGNIZER_MODEL = MODEL_DIR / "face_recognition_sface_2021dec.onnx"
MIN_MATCH_SCORE = 0.45
MIN_MATCH_MARGIN = 0.05
MAX_IMAGE_SIDE = 1600
_MODEL_LOCK = Lock()


class FaceImageError(ValueError):
    pass


class FaceModelUnavailable(RuntimeError):
    pass


@lru_cache(maxsize=1)
def _models():
    if not DETECTOR_MODEL.is_file() or not RECOGNIZER_MODEL.is_file():
        raise FaceModelUnavailable("Face recognition models are unavailable on this server.")
    try:
        detector = cv2.FaceDetectorYN.create(str(DETECTOR_MODEL), "", (320, 320), 0.9, 0.3, 5000)
        recognizer = cv2.FaceRecognizerSF.create(str(RECOGNIZER_MODEL), "")
    except cv2.error as exc:
        raise FaceModelUnavailable("Face recognition models could not be loaded.") from exc
    return detector, recognizer


def decode_image(content):
    frame = cv2.imdecode(np.frombuffer(content, dtype=np.uint8), cv2.IMREAD_COLOR)
    if frame is None:
        raise FaceImageError("Choose a readable photo in JPEG, PNG, or WebP format.")
    if frame.shape[0] * frame.shape[1] > 12_000_000:
        raise FaceImageError("The photo is too large. Use an image under 12 megapixels.")
    return frame


def _resize(frame):
    height, width = frame.shape[:2]
    scale = min(1.0, MAX_IMAGE_SIDE / max(height, width))
    if scale < 1:
        frame = cv2.resize(frame, (round(width * scale), round(height * scale)))
    return frame, scale


def _faces(frame, detector):
    detector.setInputSize((frame.shape[1], frame.shape[0]))
    _, faces = detector.detect(frame)
    return [] if faces is None else faces


def enroll_face(content):
    frame, _ = _resize(decode_image(content))
    try:
        with _MODEL_LOCK:
            detector, recognizer = _models()
            faces = _faces(frame, detector)
            if len(faces) != 1:
                raise FaceImageError("Use a clear photo with exactly one visible face.")
            embedding = recognizer.feature(recognizer.alignCrop(frame, faces[0])).flatten()
        ok, encoded = cv2.imencode(".jpg", frame, [cv2.IMWRITE_JPEG_QUALITY, 88])
    except cv2.error as exc:
        raise FaceImageError("The face could not be processed. Try a clearer front-facing photo.") from exc
    if not ok or not np.isfinite(embedding).all():
        raise FaceImageError("The face could not be processed. Try a clearer front-facing photo.")
    return encoded.tobytes(), embedding.astype(float).tolist()


def identify_faces(frame):
    gallery = list(TenantFace.objects.filter(tenant__is_active=True).select_related("tenant").defer("photo"))
    resized, scale = _resize(frame)
    results = []
    with _MODEL_LOCK:
        detector, recognizer = _models()
        for face in _faces(resized, detector):
            scores = []
            if gallery:
                try:
                    feature = recognizer.feature(recognizer.alignCrop(resized, face))
                    scores = sorted(
                        ((float(recognizer.match(feature, np.asarray(entry.embedding, dtype=np.float32).reshape(1, -1), cv2.FaceRecognizerSF_FR_COSINE)), entry)
                         for entry in gallery),
                        key=lambda pair: pair[0], reverse=True,
                    )
                except cv2.error:
                    continue
            best_score, best_entry = scores[0] if scores else (0.0, None)
            margin = best_score - scores[1][0] if len(scores) > 1 else 1.0
            matched = best_entry is not None and best_score >= MIN_MATCH_SCORE and margin >= MIN_MATCH_MARGIN
            x, y, width, height = face[:4]
            results.append({
                "box": [round(float(value) / scale) for value in (x, y, x + width, y + height)],
                "status": "possible_match" if matched else "unknown",
                "tenant_id": best_entry.tenant_id if matched else None,
                "tenant_name": best_entry.tenant.full_name if matched else None,
                "tenant_reference": best_entry.tenant.reference if matched else None,
                "match_score": round(best_score, 3) if matched else None,
            })
    return results
