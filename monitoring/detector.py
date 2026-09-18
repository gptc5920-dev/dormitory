from dataclasses import dataclass
from pathlib import Path

import cv2
import numpy as np
from django.conf import settings


@dataclass
class Detection:
    incident_type: str
    label: str
    confidence: float
    box: tuple[int, int, int, int]
    method: str

    def as_dict(self):
        return {
            "incident_type": self.incident_type,
            "label": self.label,
            "confidence": round(float(self.confidence), 3),
            "box": list(self.box),
            "method": self.method,
        }


class LightweightDetector:
    """Lazy Nano-model adapter plus conservative, explicitly heuristic visual cues."""

    LABEL_TYPES = {
        "person": "person",
        "bottle": "bottle",
        "smoke": "possible_smoke",
        "fire": "possible_fire",
        "flame": "possible_fire",
    }

    def __init__(self):
        self.model_path = Path(settings.YOLO_MODEL_PATH)
        self.model = None
        self.load_error = ""
        self.load_attempted = False

    @property
    def has_weights(self):
        return self.model_path.is_file()

    def status(self):
        return {
            "weights_available": self.has_weights,
            "weights_path": str(self.model_path),
            "model_loaded": self.model is not None,
            "load_error": self.load_error,
            "mode": "YOLO Nano + visual-cue heuristics" if self.has_weights else "visual-cue heuristics and manual incidents",
            "stock_model_support": ["person", "bottle"],
            "custom_weight_support": ["smoke", "fire", "flame"],
            "notice": "Smoke/fire visual cues are untrained heuristics unless custom trained weights are supplied; manager verification is required.",
        }

    def _load_model(self):
        if self.load_attempted or not self.has_weights:
            return
        self.load_attempted = True
        try:
            from ultralytics import YOLO

            self.model = YOLO(str(self.model_path))
        except Exception as exc:  # Surface model/runtime problems through the status endpoint.
            self.load_error = str(exc)

    def detect(self, frame):
        self._load_model()
        detections = []
        if self.model is not None:
            detections.extend(self._detect_yolo(frame))
        detections.extend(self._detect_visual_cues(frame))
        return self._deduplicate(detections)

    def _detect_yolo(self, frame):
        found = []
        results = self.model.predict(frame, conf=settings.YOLO_CONFIDENCE, verbose=False, imgsz=640)
        for result in results:
            names = result.names
            for box in result.boxes:
                class_id = int(box.cls[0])
                label = str(names[class_id]).lower().strip()
                incident_type = self.LABEL_TYPES.get(label)
                if not incident_type:
                    continue
                x1, y1, x2, y2 = [int(value) for value in box.xyxy[0].tolist()]
                found.append(Detection(incident_type, label, float(box.conf[0]), (x1, y1, x2, y2), "yolo"))
        return found

    def _detect_visual_cues(self, frame):
        height, width = frame.shape[:2]
        frame_area = max(1, height * width)
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        cues = []

        fire_mask = cv2.inRange(hsv, np.array([0, 150, 190]), np.array([35, 255, 255]))
        fire_mask = cv2.morphologyEx(fire_mask, cv2.MORPH_OPEN, np.ones((5, 5), np.uint8))
        cues.extend(self._contour_cues(fire_mask, frame_area, "possible_fire", "possible fire visual cue", 0.012, 0.30))

        # A diffuse, low-saturation gray region can only be a smoke cue, never a diagnosis.
        smoke_mask = cv2.inRange(hsv, np.array([0, 0, 85]), np.array([180, 38, 210]))
        smoke_mask[int(height * 0.85):, :] = 0
        smoke_mask = cv2.morphologyEx(smoke_mask, cv2.MORPH_OPEN, np.ones((11, 11), np.uint8))
        cues.extend(self._contour_cues(smoke_mask, frame_area, "possible_smoke", "possible smoke visual cue", 0.08, 0.32, max_ratio=0.38))
        return cues

    @staticmethod
    def _contour_cues(mask, frame_area, incident_type, label, min_ratio, base_confidence, max_ratio=0.5):
        found = []
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        for contour in contours:
            area_ratio = cv2.contourArea(contour) / frame_area
            if not min_ratio <= area_ratio <= max_ratio:
                continue
            x, y, w, h = cv2.boundingRect(contour)
            confidence = min(0.7, base_confidence + area_ratio * 2)
            found.append(Detection(incident_type, label, confidence, (x, y, x + w, y + h), "untrained_visual_cue"))
        return found

    @staticmethod
    def _intersection_over_union(first, second):
        x1 = max(first[0], second[0])
        y1 = max(first[1], second[1])
        x2 = min(first[2], second[2])
        y2 = min(first[3], second[3])
        intersection = max(0, x2 - x1) * max(0, y2 - y1)
        if not intersection:
            return 0.0
        first_area = max(0, first[2] - first[0]) * max(0, first[3] - first[1])
        second_area = max(0, second[2] - second[0]) * max(0, second[3] - second[1])
        return intersection / max(1, first_area + second_area - intersection)

    @classmethod
    def _deduplicate(cls, detections, overlap_threshold=0.55):
        """Remove overlapping duplicate cues without hiding separate objects."""
        kept = []
        for detection in sorted(detections, key=lambda item: item.confidence, reverse=True):
            overlaps_existing = any(
                detection.incident_type == existing.incident_type
                and cls._intersection_over_union(detection.box, existing.box) >= overlap_threshold
                for existing in kept
            )
            if not overlaps_existing:
                kept.append(detection)
        return kept

    @staticmethod
    def annotate(frame, detections):
        annotated = frame.copy()
        colors = {"person": (61, 145, 64), "bottle": (214, 142, 34), "possible_smoke": (120, 120, 120), "possible_fire": (35, 80, 220)}
        for detection in detections:
            x1, y1, x2, y2 = detection.box
            color = colors.get(detection.incident_type, (180, 100, 60))
            cv2.rectangle(annotated, (x1, y1), (x2, y2), color, 2)
            text = f"{detection.label} {detection.confidence:.2f}"
            cv2.putText(annotated, text, (x1, max(18, y1 - 6)), cv2.FONT_HERSHEY_SIMPLEX, 0.55, color, 2)
        return annotated


detector = LightweightDetector()
