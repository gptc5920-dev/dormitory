from pathlib import Path

import cv2
from django.conf import settings
from django.core.files.base import ContentFile
from django.db import transaction
from django.utils import timezone

from .detector import detector
from .models import DetectionCooldown, Incident, VideoJob


@transaction.atomic
def cooldown_allows(key):
    now = timezone.now()
    cooldown, created = DetectionCooldown.objects.select_for_update().get_or_create(
        key=key, defaults={"last_triggered_at": now}
    )
    if created:
        return True
    elapsed = (now - cooldown.last_triggered_at).total_seconds()
    if elapsed < settings.DETECTION_COOLDOWN_SECONDS:
        return False
    cooldown.last_triggered_at = now
    cooldown.save(update_fields=["last_triggered_at"])
    return True


def create_detection_incidents(frame, detections, source_name, room=None, source=None, cooldown_scope="live"):
    accepted = []
    for detection in detections:
        room_key = room.pk if room else "none"
        source_key = source.pk if source else source_name
        key = f"{cooldown_scope}:{source_key}:{room_key}:{detection.incident_type}"
        if cooldown_allows(key):
            accepted.append(detection)
    if not accepted:
        return []

    created = []
    annotated = detector.annotate(frame, detections)
    ok, encoded = cv2.imencode(".jpg", annotated, [cv2.IMWRITE_JPEG_QUALITY, 88])
    for detection in accepted:
        incident = Incident.objects.create(
            incident_type=detection.incident_type,
            confidence=detection.confidence,
            details=f"Automated {detection.label}; method: {detection.method}. Manager verification required.",
            detected_labels=[detection.as_dict()],
            source=source,
            source_name=source_name,
            room=room,
        )
        if ok:
            incident.snapshot.save(f"{incident.reference}.jpg", ContentFile(encoded.tobytes()), save=True)
        created.append(incident)
    return created


def process_video_job(job):
    job.status = VideoJob.Status.PROCESSING
    job.error = ""
    job.save(update_fields=["status", "error"])
    capture = cv2.VideoCapture(str(Path(job.video.path)))
    if not capture.isOpened():
        job.status = VideoJob.Status.FAILED
        job.error = "OpenCV could not open this video. Use a common MP4, AVI, or MOV codec."
        job.completed_at = timezone.now()
        job.save(update_fields=["status", "error", "completed_at"])
        return job

    frame_index = 0
    sampled = 0
    incident_count = 0
    try:
        while sampled < settings.VIDEO_MAX_SAMPLED_FRAMES:
            success, frame = capture.read()
            if not success:
                break
            frame_index += 1
            if frame_index % settings.VIDEO_SAMPLE_EVERY_FRAMES:
                continue
            sampled += 1
            detections = detector.detect(frame)
            incidents = create_detection_incidents(
                frame, detections, job.source_name, room=job.room, cooldown_scope=f"video-{job.pk}"
            )
            incident_count += len(incidents)
        job.status = VideoJob.Status.COMPLETED
    except Exception as exc:
        job.status = VideoJob.Status.FAILED
        job.error = str(exc)
    finally:
        capture.release()
        job.frames_processed = sampled
        job.incidents_created = incident_count
        job.completed_at = timezone.now()
        job.save(update_fields=["status", "error", "frames_processed", "incidents_created", "completed_at"])
    return job
