from django.contrib.auth.models import AbstractUser
from django.db import models


class ReferenceSequence(models.Model):
    key = models.CharField(max_length=80, unique=True)
    value = models.PositiveBigIntegerField(default=0)


class User(AbstractUser):
    class Role(models.TextChoices):
        ADMIN = "admin", "Administrator"
        MANAGER = "manager", "Manager"

    role = models.CharField(max_length=20, choices=Role.choices, default=Role.MANAGER)

    @property
    def is_dormitory_manager(self):
        return self.is_superuser or self.role in {self.Role.ADMIN, self.Role.MANAGER}
