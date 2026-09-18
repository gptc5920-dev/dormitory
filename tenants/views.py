from django.db.models import Count, Q
from rest_framework import decorators, response, viewsets

from accounts.permissions import IsDormitoryManager
from .models import Room, Tenant
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
        queryset = Tenant.objects.select_related("room").all()
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

    @decorators.action(detail=True, methods=["get"])
    def history(self, request, pk=None):
        from violations.serializers import ViolationSerializer, WarningSerializer

        tenant = self.get_object()
        return response.Response({
            "tenant": self.get_serializer(tenant).data,
            "warnings": WarningSerializer(tenant.warnings.select_related("rule", "incident", "issued_by"), many=True, context={"request": request}).data,
            "violations": ViolationSerializer(tenant.violations.select_related("rule", "incident", "recorded_by"), many=True, context={"request": request}).data,
        })
