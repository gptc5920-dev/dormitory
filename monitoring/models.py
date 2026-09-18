from django.conf import settings
from django.db import models

from config.references import next_reference


class CameraSource(models.Model):
    class SourceType(models.TextChoices):
        WEBCAM = "webcam", "Webcam"
        IP_CAMERA = "ip_camera", "IP camera"
        UPLOAD = "upload", "Uploaded video"

    name = models.CharField(max_length=120)
    source_type = models.CharField(max_length=20, choices=SourceType.choices, default=SourceType.WEBCAM)
    location = models.CharField(max_length=160)
    stream_url = models.CharField(max_length=500, blank=True, help_text="Stored for local integrations; never returned by the API.")
    room = models.ForeignKey("tenants.Room", on_delete=models.SET_NULL, null=True, blank=True, related_name="camera_sources")
    is_enabled = models.BooleanField(default=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class Incident(models.Model):
    class Type(models.TextChoices):
        PERSON = "person", "Person detected"
        BOTTLE = "bottle", "Bottle detected"
        POSSIBLE_SMOKE = "possible_smoke", "Possible smoke"
        POSSIBLE_FIRE = "possible_fire", "Possible fire"
        MANUAL = "manual", "Manual report"
        OTHER = "other", "Other"

    class Status(models.TextChoices):
        NEW = "new", "New"
        REVIEWED = "reviewed", "Reviewed"
        VERIFIED = "verified", "Verified"
        DISMISSED = "dismissed", "Dismissed"
        ASSIGNED = "assigned", "Assigned"

    reference = models.CharField(max_length=20, unique=True, blank=True, editable=False)
    incident_type = models.CharField(max_length=30, choices=Type.choices)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.NEW, db_index=True)
    confidence = models.FloatField(null=True, blank=True)
    details = models.TextField(blank=True)
    detected_labels = models.JSONField(default=list, blank=True)
    occurred_at = models.DateTimeField(auto_now_add=True, db_index=True)
    snapshot = models.ImageField(upload_to="incidents/%Y/%m/", blank=True)
    source = models.ForeignKey(CameraSource, on_delete=models.SET_NULL, null=True, blank=True, related_name="incidents")
    source_name = models.CharField(max_length=160, blank=True)
    room = models.ForeignKey("tenants.Room", on_delete=models.SET_NULL, null=True, blank=True, related_name="incidents")
    verified_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="incidents_verified")
    verified_at = models.DateTimeField(null=True, blank=True)
    assigned_tenant = models.ForeignKey("tenants.Tenant", on_delete=models.SET_NULL, null=True, blank=True, related_name="assigned_incidents")
    review_notes = models.TextField(blank=True)

    class Meta:
        ordering = ["-occurred_at"]

    def save(self, *args, **kwargs):
        if not self.reference:
            self.reference = next_reference(Incident, "INC")
        if self.source_id and not self.source_name:
            self.source_name = self.source.name
        return super().save(*args, **kwargs)

    def __str__(self):
        return self.reference


class DetectionCooldown(models.Model):
    key = models.CharField(max_length=255, unique=True)
    last_triggered_at = models.DateTimeField()


class VideoJob(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        PROCESSING = "processing", "Processing"
        COMPLETED = "completed", "Completed"
        FAILED = "failed", "Failed"

    video = models.FileField(upload_to="uploads/videos/%Y/%m/")
    source_name = models.CharField(max_length=160, default="Uploaded video")
    room = models.ForeignKey("tenants.Room", on_delete=models.SET_NULL, null=True, blank=True, related_name="video_jobs")
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    frames_processed = models.PositiveIntegerField(default=0)
    incidents_created = models.PositiveIntegerField(default=0)
    error = models.TextField(blank=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="video_jobs")
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]
