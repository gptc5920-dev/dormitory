from datetime import datetime, time, timedelta

import cv2
import numpy as np
from django.conf import settings
from django.db.models import Count, Q, Sum
from django.utils import timezone
from rest_framework import decorators, status, viewsets
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.permissions import IsDormitoryManager
from tenants.models import Room, Tenant
from violations.models import DormitoryRule, Violation, Warning
from .detector import detector
from .models import CameraSource, Incident, VideoJob
from .serializers import (
    AssignIncidentSerializer,
    CameraSourceSerializer,
    DetectFrameSerializer,
    IncidentFilterSerializer,
    IncidentSerializer,
    ReportFilterSerializer,
    ReviewIncidentSerializer,
    VideoJobSerializer,
)
from .services import create_detection_incidents, process_video_job


def date_range_bounds(date_from, date_to):
    current_timezone = timezone.get_current_timezone()
    start = timezone.make_aware(datetime.combine(date_from, time.min), current_timezone)
    end = timezone.make_aware(datetime.combine(date_to + timedelta(days=1), time.min), current_timezone)
    return start, end


class CameraSourceViewSet(viewsets.ModelViewSet):
    queryset = CameraSource.objects.select_related("room").all()
    serializer_class = CameraSourceSerializer
    permission_classes = [IsDormitoryManager]


class IncidentViewSet(viewsets.ModelViewSet):
    serializer_class = IncidentSerializer
    permission_classes = [IsDormitoryManager]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get_queryset(self):
        queryset = Incident.objects.select_related("source", "room", "verified_by", "assigned_tenant")
        filters = IncidentFilterSerializer(data=self.request.query_params)
        filters.is_valid(raise_exception=True)
        values = filters.validated_data
        status_value = values.get("status")
        incident_type = values.get("type")
        room = values.get("room")
        date_from = values.get("date_from")
        date_to = values.get("date_to")
        if status_value:
            queryset = queryset.filter(status=status_value)
        if incident_type:
            queryset = queryset.filter(incident_type=incident_type)
        if room:
            queryset = queryset.filter(room_id=room)
        if date_from:
            start, _ = date_range_bounds(date_from, date_from)
            queryset = queryset.filter(occurred_at__gte=start)
        if date_to:
            _, end = date_range_bounds(date_to, date_to)
            queryset = queryset.filter(occurred_at__lt=end)
        return queryset

    @decorators.action(detail=True, methods=["post"])
    def review(self, request, pk=None):
        incident = self.get_object()
        serializer = ReviewIncidentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        if incident.status not in {Incident.Status.NEW, Incident.Status.REVIEWED}:
            return Response({"detail": "Only new or reviewed incidents can be marked reviewed."}, status=status.HTTP_409_CONFLICT)
        incident.status = Incident.Status.REVIEWED
        incident.review_notes = serializer.validated_data.get("notes", incident.review_notes)
        incident.save(update_fields=["status", "review_notes"])
        return Response(self.get_serializer(incident).data)

    @decorators.action(detail=True, methods=["post"])
    def verify(self, request, pk=None):
        incident = self.get_object()
        serializer = ReviewIncidentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        if incident.status not in {Incident.Status.NEW, Incident.Status.REVIEWED}:
            return Response({"detail": "Only new or reviewed incidents can be verified."}, status=status.HTTP_409_CONFLICT)
        incident.status = Incident.Status.VERIFIED
        incident.verified_by = request.user
        incident.verified_at = timezone.now()
        incident.review_notes = serializer.validated_data.get("notes", incident.review_notes)
        incident.save(update_fields=["status", "verified_by", "verified_at", "review_notes"])
        return Response(self.get_serializer(incident).data)

    @decorators.action(detail=True, methods=["post"])
    def dismiss(self, request, pk=None):
        incident = self.get_object()
        serializer = ReviewIncidentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        if incident.status == Incident.Status.ASSIGNED:
            return Response({"detail": "An assigned incident cannot be dismissed."}, status=status.HTTP_409_CONFLICT)
        incident.status = Incident.Status.DISMISSED
        incident.review_notes = serializer.validated_data.get("notes", incident.review_notes)
        incident.save(update_fields=["status", "review_notes"])
        return Response(self.get_serializer(incident).data)

    @decorators.action(detail=True, methods=["post"])
    def assign(self, request, pk=None):
        incident = self.get_object()
        serializer = AssignIncidentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        if incident.status != Incident.Status.VERIFIED:
            return Response({"detail": "A manager must verify the incident before tenant assignment."}, status=status.HTTP_409_CONFLICT)
        tenant = serializer.validated_data["tenant"]
        incident.assigned_tenant = tenant
        incident.status = Incident.Status.ASSIGNED
        incident.review_notes = serializer.validated_data.get("notes", incident.review_notes)
        incident.save(update_fields=["assigned_tenant", "status", "review_notes"])
        return Response(self.get_serializer(incident).data)


class DetectorStatusView(APIView):
    permission_classes = [IsDormitoryManager]

    def get(self, request):
        return Response(detector.status())


class DetectFrameView(APIView):
    permission_classes = [IsDormitoryManager]
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request):
        serializer = DetectFrameSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        upload = serializer.validated_data["frame"]
        data = np.frombuffer(upload.read(), dtype=np.uint8)
        frame = cv2.imdecode(data, cv2.IMREAD_COLOR)
        if frame is None:
            return Response({"frame": ["The uploaded frame is not a readable image."]}, status=status.HTTP_400_BAD_REQUEST)

        source = serializer.validated_data.get("source")
        room = serializer.validated_data.get("room") or (source.room if source else None)
        source_name = source.name if source else serializer.validated_data["source_name"]
        detections = detector.detect(frame)
        incidents = create_detection_incidents(frame, detections, source_name, room=room, source=source)
        return Response({
            "frame": {"width": int(frame.shape[1]), "height": int(frame.shape[0])},
            "detections": [item.as_dict() for item in detections],
            "incidents_created": IncidentSerializer(incidents, many=True, context={"request": request}).data,
            "cooldown_seconds": settings.DETECTION_COOLDOWN_SECONDS,
            "model": detector.status(),
        })


class VideoJobViewSet(viewsets.ModelViewSet):
    queryset = VideoJob.objects.select_related("room", "created_by")
    serializer_class = VideoJobSerializer
    permission_classes = [IsDormitoryManager]
    parser_classes = [MultiPartParser, FormParser]
    http_method_names = ["get", "post", "delete", "head", "options"]

    def perform_create(self, serializer):
        job = serializer.save(created_by=self.request.user)
        process_video_job(job)


class DashboardSummaryView(APIView):
    permission_classes = [IsDormitoryManager]

    def get(self, request):
        today = timezone.localdate()
        active_tenants = Tenant.objects.filter(is_active=True).count()
        active_rooms = Room.objects.filter(is_active=True)
        room_totals = active_rooms.aggregate(active_rooms=Count("id"), total_beds=Sum("capacity"))
        occupied_beds = Tenant.objects.filter(is_active=True, room__is_active=True).count()
        today_start, today_end = date_range_bounds(today, today)
        incident_counts = Incident.objects.aggregate(
            pending=Count("id", filter=Q(status__in=[Incident.Status.NEW, Incident.Status.REVIEWED])),
            verified=Count("id", filter=Q(status=Incident.Status.VERIFIED)),
            today=Count("id", filter=Q(occurred_at__gte=today_start, occurred_at__lt=today_end)),
        )
        recent = Incident.objects.select_related("room", "assigned_tenant", "verified_by", "source")[:8]
        total_beds = room_totals["total_beds"] or 0
        return Response({
            "active_tenants": active_tenants,
            "active_rooms": room_totals["active_rooms"],
            "total_beds": total_beds,
            "available_beds": max(0, total_beds - occupied_beds),
            "pending_incidents": incident_counts["pending"],
            "verified_incidents": incident_counts["verified"],
            "incidents_today": incident_counts["today"],
            "warnings_total": Warning.objects.count(),
            "violations_total": Violation.objects.count(),
            "recent_incidents": IncidentSerializer(recent, many=True, context={"request": request}).data,
        })


class ReportSummaryView(APIView):
    permission_classes = [IsDormitoryManager]

    def get(self, request):
        serializer = ReportFilterSerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)
        date_to = serializer.validated_data["date_to"]
        date_from = serializer.validated_data["date_from"]
        start, end = date_range_bounds(date_from, date_to)

        incidents = Incident.objects.filter(occurred_at__gte=start, occurred_at__lt=end)
        warnings = Warning.objects.filter(issued_at__gte=start, issued_at__lt=end)
        violations = Violation.objects.filter(recorded_at__gte=start, recorded_at__lt=end)
        group = lambda queryset, field: list(queryset.values(field).annotate(count=Count("id")).order_by(field))
        return Response({
            "date_from": date_from,
            "date_to": date_to,
            "totals": {"incidents": incidents.count(), "warnings": warnings.count(), "violations": violations.count()},
            "incidents_by_type": group(incidents, "incident_type"),
            "incidents_by_status": group(incidents, "status"),
            "warnings_by_rule": list(warnings.values("rule__code", "rule__title").annotate(count=Count("id")).order_by("rule__code")),
            "violations_by_rule": list(violations.values("rule__code", "rule__title").annotate(count=Count("id")).order_by("rule__code")),
        })
