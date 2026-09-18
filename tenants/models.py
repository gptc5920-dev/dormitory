from django.core.exceptions import ValidationError
from django.db import models

from config.references import next_reference


class Room(models.Model):
    number = models.CharField(max_length=20, unique=True)
    floor = models.PositiveSmallIntegerField(default=1)
    capacity = models.PositiveSmallIntegerField(default=4)
    description = models.CharField(max_length=255, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["floor", "number"]

    def __str__(self):
        return f"Room {self.number}"

    def clean(self):
        if self.pk:
            occupied = self.tenants.filter(is_active=True).count()
            if occupied and not self.is_active:
                raise ValidationError({"is_active": "Relocate active tenants before deactivating this room."})
            if self.capacity < occupied:
                raise ValidationError({"capacity": f"Capacity cannot be lower than the current occupancy ({occupied})."})

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)


class Tenant(models.Model):
    reference = models.CharField(max_length=20, unique=True, blank=True, editable=False)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=30, blank=True)
    emergency_contact = models.CharField(max_length=150, blank=True)
    room = models.ForeignKey(Room, on_delete=models.PROTECT, related_name="tenants")
    enrolled_on = models.DateField(auto_now_add=True)
    move_in_date = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ["last_name", "first_name"]

    def __str__(self):
        return f"{self.reference} - {self.first_name} {self.last_name}"

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}".strip()

    def clean(self):
        if self.room_id and self.is_active:
            if not self.room.is_active:
                raise ValidationError({"room": "Active tenants must be assigned to an active room."})
            occupied = Tenant.objects.filter(room_id=self.room_id, is_active=True).exclude(pk=self.pk).count()
            if occupied >= self.room.capacity:
                raise ValidationError({"room": "This room is already at capacity."})

    def save(self, *args, **kwargs):
        if not self.reference:
            self.reference = next_reference(Tenant, "TEN")
        self.full_clean()
        return super().save(*args, **kwargs)
