from django.conf import settings
from rest_framework import serializers

from monitoring.models import Incident
from .models import DormitoryRule, Violation, Warning


class DormitoryRuleSerializer(serializers.ModelSerializer):
    class Meta:
        model = DormitoryRule
        fields = ["id", "code", "title", "category", "description", "severity", "is_active", "created_at"]
        read_only_fields = ["created_at"]

    def validate_code(self, value):
        value = value.strip().upper()
        queryset = DormitoryRule.objects.filter(code__iexact=value)
        if self.instance:
            queryset = queryset.exclude(pk=self.instance.pk)
        if queryset.exists():
            raise serializers.ValidationError("A rule with this code already exists.")
        return value


class WarningSerializer(serializers.ModelSerializer):
    tenant_name = serializers.CharField(source="tenant.full_name", read_only=True)
    tenant_reference = serializers.CharField(source="tenant.reference", read_only=True)
    rule_code = serializers.CharField(source="rule.code", read_only=True)
    rule_title = serializers.CharField(source="rule.title", read_only=True)
    incident_reference = serializers.CharField(source="incident.reference", read_only=True, default=None)
    issued_by_name = serializers.CharField(source="issued_by.get_full_name", read_only=True)

    class Meta:
        model = Warning
        fields = [
            "id", "reference", "tenant", "tenant_name", "tenant_reference", "rule", "rule_code",
            "rule_title", "incident", "incident_reference", "message", "issued_by", "issued_by_name",
            "issued_at", "acknowledged",
        ]
        read_only_fields = ["reference", "issued_by", "issued_at"]

    def validate(self, attrs):
        incident = attrs.get("incident", getattr(self.instance, "incident", None))
        tenant = attrs.get("tenant", getattr(self.instance, "tenant", None))
        rule = attrs.get("rule", getattr(self.instance, "rule", None))
        if (self.instance is None or "tenant" in attrs) and tenant and not tenant.is_active:
            raise serializers.ValidationError({"tenant": "Warnings can only be issued to active tenants."})
        if (self.instance is None or "rule" in attrs) and rule and not rule.is_active:
            raise serializers.ValidationError({"rule": "Warnings must reference an active rule."})
        if incident:
            if incident.status != Incident.Status.ASSIGNED:
                raise serializers.ValidationError({"incident": "Verify and assign the incident before issuing a linked warning."})
            if tenant and incident.assigned_tenant_id != tenant.id:
                raise serializers.ValidationError({"tenant": "Tenant must match the incident assignment."})
        return attrs


class ViolationSerializer(serializers.ModelSerializer):
    tenant_name = serializers.CharField(source="tenant.full_name", read_only=True)
    tenant_reference = serializers.CharField(source="tenant.reference", read_only=True)
    rule_code = serializers.CharField(source="rule.code", read_only=True)
    rule_title = serializers.CharField(source="rule.title", read_only=True)
    incident_reference = serializers.CharField(source="incident.reference", read_only=True, default=None)
    recorded_by_name = serializers.CharField(source="recorded_by.get_full_name", read_only=True)

    class Meta:
        model = Violation
        fields = [
            "id", "reference", "tenant", "tenant_name", "tenant_reference", "rule", "rule_code",
            "rule_title", "incident", "incident_reference", "description", "action_taken", "evidence",
            "recorded_by", "recorded_by_name", "recorded_at",
        ]
        read_only_fields = ["reference", "recorded_by", "recorded_at"]

    def validate(self, attrs):
        incident = attrs.get("incident", getattr(self.instance, "incident", None))
        tenant = attrs.get("tenant", getattr(self.instance, "tenant", None))
        rule = attrs.get("rule", getattr(self.instance, "rule", None))
        if (self.instance is None or "tenant" in attrs) and tenant and not tenant.is_active:
            raise serializers.ValidationError({"tenant": "Violations can only be recorded for active tenants."})
        if (self.instance is None or "rule" in attrs) and rule and not rule.is_active:
            raise serializers.ValidationError({"rule": "Violations must reference an active rule."})
        if incident:
            if incident.status != Incident.Status.ASSIGNED:
                raise serializers.ValidationError({"incident": "Verify and assign the incident before recording a linked violation."})
            if tenant and incident.assigned_tenant_id != tenant.id:
                raise serializers.ValidationError({"tenant": "Tenant must match the incident assignment."})
        return attrs

    def validate_evidence(self, upload):
        if upload.size > settings.MAX_IMAGE_UPLOAD_BYTES:
            size_mb = settings.MAX_IMAGE_UPLOAD_BYTES // (1024 * 1024)
            raise serializers.ValidationError(f"Evidence must not exceed {size_mb} MB.")
        return upload


class RuleFilterSerializer(serializers.Serializer):
    active = serializers.ChoiceField(choices=("true", "false"), required=False)
    category = serializers.CharField(required=False, max_length=80)

    def validate_active(self, value):
        return value == "true"


class RecordFilterSerializer(serializers.Serializer):
    tenant = serializers.IntegerField(required=False, min_value=1)
    rule = serializers.IntegerField(required=False, min_value=1)
