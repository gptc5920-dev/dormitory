from pathlib import Path
from datetime import date, timedelta
import math
from urllib.parse import urlsplit

from django.conf import settings
from django.utils import timezone
from rest_framework import serializers

from tenants.models import Room, Tenant
from .models import CameraSource, Incident, VideoJob


def _validate_upload_size(upload, limit, label):
    if upload.size > limit:
        size_mb = limit // (1024 * 1024)
        raise serializers.ValidationError(f"{label} must not exceed {size_mb} MB.")
    return upload


class CameraSourceSerializer(serializers.ModelSerializer):
    stream_url = serializers.CharField(write_only=True, required=False, allow_blank=True, max_length=500)
    has_stream_url = serializers.SerializerMethodField()

    def get_has_stream_url(self, obj):
        return bool(obj.stream_url)

    def validate_stream_url(self, value):
        if not value:
            return value
        try:
            parsed = urlsplit(value)
            if parsed.scheme != "rtsp" or not parsed.hostname or any(c.isspace() for c in value):
                raise ValueError
            if parsed.port is not None and not 1 <= parsed.port <= 65535:
                raise ValueError
        except ValueError:
            raise serializers.ValidationError("Enter a valid rtsp:// camera stream URL.")
        return value

    def validate(self, attrs):
        source_type = attrs.get("source_type", getattr(self.instance, "source_type", "webcam"))
        stream_url = attrs.get("stream_url", getattr(self.instance, "stream_url", ""))
        if source_type == "ip_camera" and not stream_url:
            raise serializers.ValidationError({"stream_url": "A Wi-Fi / IP camera requires an RTSP stream URL."})
        if source_type != "ip_camera":
            attrs["stream_url"] = ""
        return attrs

    room_number = serializers.CharField(source="room.number", read_only=True)
    room = serializers.PrimaryKeyRelatedField(
        queryset=Room.objects.filter(is_active=True), required=False, allow_null=True
    )

    class Meta:
        model = CameraSource
        fields = ["id", "name", "source_type", "location", "room", "room_number", "is_enabled", "stream_url", "has_stream_url"]


class IncidentSerializer(serializers.ModelSerializer):
    confidence = serializers.FloatField(required=False, allow_null=True, min_value=0, max_value=1)
    room = serializers.PrimaryKeyRelatedField(
        queryset=Room.objects.filter(is_active=True), required=False, allow_null=True
    )
    source = serializers.PrimaryKeyRelatedField(
        queryset=CameraSource.objects.filter(is_enabled=True), required=False, allow_null=True
    )
    room_number = serializers.CharField(source="room.number", read_only=True, default=None)
    assigned_tenant_name = serializers.CharField(source="assigned_tenant.full_name", read_only=True, default=None)
    assigned_tenant_reference = serializers.CharField(source="assigned_tenant.reference", read_only=True, default=None)
    verified_by_name = serializers.CharField(source="verified_by.get_full_name", read_only=True, default=None)
    source_display = serializers.SerializerMethodField()

    class Meta:
        model = Incident
        fields = [
            "id", "reference", "incident_type", "status", "confidence", "details", "detected_labels",
            "occurred_at", "snapshot", "source", "source_name", "source_display", "room", "room_number",
            "verified_by", "verified_by_name", "verified_at", "assigned_tenant", "assigned_tenant_name",
            "assigned_tenant_reference", "review_notes",
        ]
        read_only_fields = [
            "reference", "status", "verified_by", "verified_at", "assigned_tenant", "occurred_at",
            "detected_labels",
        ]

    def get_source_display(self, obj):
        return obj.source_name or (obj.source.name if obj.source else "Manual")

    def validate_snapshot(self, upload):
        return _validate_upload_size(upload, settings.MAX_IMAGE_UPLOAD_BYTES, "Snapshot")

    def validate_confidence(self, value):
        if value is not None and not math.isfinite(value):
            raise serializers.ValidationError("Confidence must be a finite number between 0 and 1.")
        return value


class AssignIncidentSerializer(serializers.Serializer):
    tenant = serializers.PrimaryKeyRelatedField(queryset=Tenant.objects.filter(is_active=True))
    notes = serializers.CharField(required=False, allow_blank=True)


class ReviewIncidentSerializer(serializers.Serializer):
    notes = serializers.CharField(required=False, allow_blank=True, max_length=2000)


class DetectFrameSerializer(serializers.Serializer):
    frame = serializers.FileField()
    source = serializers.PrimaryKeyRelatedField(
        queryset=CameraSource.objects.filter(is_enabled=True), required=False, allow_null=True
    )
    room = serializers.PrimaryKeyRelatedField(
        queryset=Room.objects.filter(is_active=True), required=False, allow_null=True
    )
    source_name = serializers.CharField(required=False, default="Browser webcam", max_length=160)

    def validate_frame(self, upload):
        content_type = (upload.content_type or "").lower()
        if content_type and not content_type.startswith("image/"):
            raise serializers.ValidationError("The frame must be an image upload.")
        return _validate_upload_size(upload, settings.MAX_FRAME_UPLOAD_BYTES, "Frame")


class SupportedDateField(serializers.DateField):
    def to_internal_value(self, data):
        value = super().to_internal_value(data)
        if not date(2, 1, 1) <= value <= date(9998, 12, 31):
            raise serializers.ValidationError("Use a date between 0002-01-01 and 9998-12-31.")
        return value


class IncidentFilterSerializer(serializers.Serializer):
    status = serializers.ChoiceField(choices=Incident.Status.choices, required=False)
    type = serializers.ChoiceField(choices=Incident.Type.choices, required=False)
    room = serializers.IntegerField(required=False, min_value=1)
    date_from = SupportedDateField(required=False)
    date_to = SupportedDateField(required=False)

    def validate(self, attrs):
        if attrs.get("date_from") and attrs.get("date_to") and attrs["date_from"] > attrs["date_to"]:
            raise serializers.ValidationError({"date_from": "Must be on or before date_to."})
        return attrs


class ReportFilterSerializer(serializers.Serializer):
    date_from = SupportedDateField(required=False)
    date_to = SupportedDateField(required=False)

    def validate(self, attrs):
        attrs.setdefault("date_to", timezone.localdate())
        attrs.setdefault("date_from", max(date(2, 1, 1), attrs["date_to"] - timedelta(days=29)))
        if attrs.get("date_from") and attrs.get("date_to") and attrs["date_from"] > attrs["date_to"]:
            raise serializers.ValidationError({"date_from": "Must be on or before date_to."})
        return attrs


class VideoJobSerializer(serializers.ModelSerializer):
    room = serializers.PrimaryKeyRelatedField(
        queryset=Room.objects.filter(is_active=True), required=False, allow_null=True
    )
    room_number = serializers.CharField(source="room.number", read_only=True, default=None)
    created_by_name = serializers.CharField(source="created_by.get_full_name", read_only=True)

    class Meta:
        model = VideoJob
        fields = [
            "id", "video", "source_name", "room", "room_number", "status", "frames_processed",
            "incidents_created", "error", "created_by", "created_by_name", "created_at", "completed_at",
        ]
        read_only_fields = [
            "status", "frames_processed", "incidents_created", "error", "created_by", "created_at", "completed_at",
        ]

    def validate_video(self, upload):
        allowed_extensions = {".avi", ".m4v", ".mkv", ".mov", ".mp4", ".webm"}
        if Path(upload.name).suffix.lower() not in allowed_extensions:
            raise serializers.ValidationError("Use an MP4, MOV, AVI, MKV, M4V, or WebM video.")
        return _validate_upload_size(upload, settings.MAX_VIDEO_UPLOAD_BYTES, "Video")
