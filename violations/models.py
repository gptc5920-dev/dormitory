from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models

from config.references import next_reference


class DormitoryRule(models.Model):
    class Severity(models.TextChoices):
        LOW = "low", "Low"
        MEDIUM = "medium", "Medium"
        HIGH = "high", "High"
        CRITICAL = "critical", "Critical"

    code = models.CharField(max_length=20, unique=True)
    title = models.CharField(max_length=160)
    category = models.CharField(max_length=80)
    description = models.TextField()
    severity = models.CharField(max_length=20, choices=Severity.choices, default=Severity.MEDIUM)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["code"]

    def __str__(self):
        return f"{self.code} - {self.title}"

    def save(self, *args, **kwargs):
        self.code = self.code.strip().upper()
        self.full_clean()
        return super().save(*args, **kwargs)


class Warning(models.Model):
    reference = models.CharField(max_length=20, unique=True, blank=True, editable=False)
    tenant = models.ForeignKey("tenants.Tenant", on_delete=models.PROTECT, related_name="warnings")
    rule = models.ForeignKey(DormitoryRule, on_delete=models.PROTECT, related_name="warnings")
    incident = models.ForeignKey("monitoring.Incident", on_delete=models.SET_NULL, null=True, blank=True, related_name="warnings")
    message = models.TextField()
    issued_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="warnings_issued")
    issued_at = models.DateTimeField(auto_now_add=True, db_index=True)
    acknowledged = models.BooleanField(default=False)

    class Meta:
        ordering = ["-issued_at"]

    def clean(self):
        if self.incident_id:
            if self.incident.status != "assigned":
                raise ValidationError({"incident": "The incident must be verified and assigned first."})
            if self.incident.assigned_tenant_id != self.tenant_id:
                raise ValidationError({"tenant": "Tenant must match the incident assignment."})

    def save(self, *args, **kwargs):
        if not self.reference:
            self.reference = next_reference(Warning, "WRN")
        self.full_clean()
        return super().save(*args, **kwargs)

    def __str__(self):
        return self.reference


class Violation(models.Model):
    reference = models.CharField(max_length=20, unique=True, blank=True, editable=False)
    tenant = models.ForeignKey("tenants.Tenant", on_delete=models.PROTECT, related_name="violations")
    rule = models.ForeignKey(DormitoryRule, on_delete=models.PROTECT, related_name="violations")
    incident = models.ForeignKey("monitoring.Incident", on_delete=models.SET_NULL, null=True, blank=True, related_name="violations")
    description = models.TextField()
    action_taken = models.CharField(max_length=255, blank=True)
    evidence = models.ImageField(upload_to="violations/%Y/%m/", blank=True)
    recorded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="violations_recorded")
    recorded_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ["-recorded_at"]

    def clean(self):
        if self.incident_id:
            if self.incident.status != "assigned":
                raise ValidationError({"incident": "The incident must be verified and assigned first."})
            if self.incident.assigned_tenant_id != self.tenant_id:
                raise ValidationError({"tenant": "Tenant must match the incident assignment."})

    def save(self, *args, **kwargs):
        if not self.reference:
            self.reference = next_reference(Violation, "VIO")
        self.full_clean()
        return super().save(*args, **kwargs)

    def __str__(self):
        return self.reference
