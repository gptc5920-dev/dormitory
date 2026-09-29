import base64

from django.db.models import Count, Q
from rest_framework import decorators, response, status, viewsets
from rest_framework.parsers import FormParser, MultiPartParser

from accounts.permissions import IsDormitoryManager
from .face_recognition import FaceImageError, FaceModelUnavailable, enroll_face
from .models import Room, Tenant, TenantFace
from .serializers import RoomFilterSerializer, RoomSerializer, TenantFilterSerializer, TenantSerializer


class RoomViewSet(viewsets.ModelViewSet):
    serializer_class = RoomSerializer
    permission_classes = [IsDormitoryManager]

    def get_queryset(self):
        filters = RoomFilterSerializer(data=self.request.query_params)
        filters.is_valid(raise_exception=True)
        queryset = Room.objects.annotate(
            occupancy=Count("tenants", filter=Q(tenants__is_active=True))
        )
        if "active" in filters.validated_data:
            queryset = queryset.filter(is_active=filters.validated_data["active"])
        return queryset.order_by("floor", "number", "pk")


class TenantViewSet(viewsets.ModelViewSet):
    serializer_class = TenantSerializer
    permission_classes = [IsDormitoryManager]

    def get_queryset(self):
        queryset = Tenant.objects.select_related("room", "face").defer("face__photo", "face__embedding")
        filters = TenantFilterSerializer(data=self.request.query_params)
        filters.is_valid(raise_exception=True)
        search = filters.validated_data.get("search", "").strip()
        room = filters.validated_data.get("room")
        active = filters.validated_data.get("active")
        if search:
            queryset = queryset.filter(
                Q(reference__icontains=search) | Q(first_name__icontains=search) |
                Q(last_name__icontains=search) | Q(email__icontains=search)
            )
        if room:
            queryset = queryset.filter(room_id=room)
        if active is not None:
            queryset = queryset.filter(is_active=active)
        return queryset

    @decorators.action(detail=False, methods=["post"], url_path="check-face", parser_classes=[MultiPartParser, FormParser])
    def check_face(self, request):
        upload, error = self._face_upload(request)
        if error:
            return error
        try:
            enroll_face(upload.read())
        except FaceImageError as exc:
            return response.Response({"photo": [str(exc)]}, status=400, headers={"Cache-Control": "no-store"})
        except FaceModelUnavailable as exc:
            return response.Response({"detail": str(exc)}, status=503, headers={"Cache-Control": "no-store"})
        return response.Response({"face_detected": True}, headers={"Cache-Control": "no-store"})

    @staticmethod
    def _face_upload(request):
        headers = {"Cache-Control": "no-store"}
        upload = request.FILES.get("photo")
        if upload is None:
            return None, response.Response({"photo": ["Choose or capture a face photo."]}, status=400, headers=headers)
        if upload.size > 8 * 1024 * 1024:
            return None, response.Response({"photo": ["Face photo must be 8 MB or smaller."]}, status=400, headers=headers)
        if upload.content_type not in {"image/jpeg", "image/png", "image/webp"}:
            return None, response.Response({"photo": ["Use a JPEG, PNG, or WebP image."]}, status=400, headers=headers)
        return upload, None

    @decorators.action(detail=True, methods=["get", "post", "delete"], url_path="face-photo", parser_classes=[MultiPartParser, FormParser])
    def face_photo(self, request, pk=None):
        tenant = self.get_object()
        headers = {"Cache-Control": "no-store"}
        if request.method == "GET":
            if not hasattr(tenant, "face"):
                return response.Response({"detail": "No face photo is enrolled."}, status=404, headers=headers)
            image = base64.b64encode(bytes(tenant.face.photo)).decode("ascii")
            return response.Response({"image": f"data:image/jpeg;base64,{image}"}, headers=headers)
        if request.method == "DELETE":
            if hasattr(tenant, "face"):
                tenant.face.delete()
            return response.Response(status=status.HTTP_204_NO_CONTENT, headers=headers)

        upload, error = self._face_upload(request)
        if error:
            return error
        try:
            photo, embedding = enroll_face(upload.read())
        except FaceImageError as exc:
            return response.Response({"photo": [str(exc)]}, status=400, headers=headers)
        except FaceModelUnavailable as exc:
            return response.Response({"detail": str(exc)}, status=503, headers=headers)
        TenantFace.objects.update_or_create(tenant=tenant, defaults={"photo": photo, "embedding": embedding})
        return response.Response({"has_face_photo": True}, headers=headers)

    @decorators.action(detail=True, methods=["get"])
    def history(self, request, pk=None):
        from violations.serializers import ViolationSerializer, WarningSerializer

        tenant = self.get_object()
        return response.Response({
            "tenant": self.get_serializer(tenant).data,
            "warnings": WarningSerializer(tenant.warnings.select_related("rule", "incident", "issued_by"), many=True, context={"request": request}).data,
            "violations": ViolationSerializer(tenant.violations.select_related("rule", "incident", "recorded_by"), many=True, context={"request": request}).data,
        })
