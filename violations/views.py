from rest_framework import viewsets

from accounts.permissions import IsDormitoryManager
from .models import DormitoryRule, Violation, Warning
from .serializers import (
    DormitoryRuleSerializer,
    RecordFilterSerializer,
    RuleFilterSerializer,
    ViolationSerializer,
    WarningSerializer,
)


class DormitoryRuleViewSet(viewsets.ModelViewSet):
    serializer_class = DormitoryRuleSerializer
    permission_classes = [IsDormitoryManager]

    def get_queryset(self):
        queryset = DormitoryRule.objects.all()
        filters = RuleFilterSerializer(data=self.request.query_params)
        filters.is_valid(raise_exception=True)
        active = filters.validated_data.get("active")
        category = filters.validated_data.get("category")
        if active is not None:
            queryset = queryset.filter(is_active=active)
        if category:
            queryset = queryset.filter(category__iexact=category)
        return queryset


class WarningViewSet(viewsets.ModelViewSet):
    serializer_class = WarningSerializer
    permission_classes = [IsDormitoryManager]

    def get_queryset(self):
        queryset = Warning.objects.select_related("tenant", "rule", "incident", "issued_by")
        filters = RecordFilterSerializer(data=self.request.query_params)
        filters.is_valid(raise_exception=True)
        if filters.validated_data.get("tenant"):
            queryset = queryset.filter(tenant_id=filters.validated_data["tenant"])
        if filters.validated_data.get("rule"):
            queryset = queryset.filter(rule_id=filters.validated_data["rule"])
        return queryset

    def perform_create(self, serializer):
        serializer.save(issued_by=self.request.user)


class ViolationViewSet(viewsets.ModelViewSet):
    serializer_class = ViolationSerializer
    permission_classes = [IsDormitoryManager]

    def get_queryset(self):
        queryset = Violation.objects.select_related("tenant", "rule", "incident", "recorded_by")
        filters = RecordFilterSerializer(data=self.request.query_params)
        filters.is_valid(raise_exception=True)
        if filters.validated_data.get("tenant"):
            queryset = queryset.filter(tenant_id=filters.validated_data["tenant"])
        if filters.validated_data.get("rule"):
            queryset = queryset.filter(rule_id=filters.validated_data["rule"])
        return queryset

    def perform_create(self, serializer):
        serializer.save(recorded_by=self.request.user)
