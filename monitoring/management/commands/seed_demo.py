from django.core.management.base import BaseCommand
from django.utils import timezone

from accounts.models import User
from monitoring.models import CameraSource, Incident
from tenants.models import Room, Tenant
from violations.models import DormitoryRule, Violation, Warning


class Command(BaseCommand):
    help = "Create development users, sample rules, rooms, tenants, and reviewed records."

    def handle(self, *args, **options):
        manager, created = User.objects.get_or_create(
            username="manager",
            defaults={"first_name": "Dormitory", "last_name": "Manager", "email": "manager@example.test", "role": User.Role.MANAGER},
        )
        if created:
            manager.set_password("Manager123!")
            manager.save(update_fields=["password"])
        admin_user, created = User.objects.get_or_create(
            username="admin",
            defaults={"first_name": "System", "last_name": "Administrator", "email": "admin@example.test", "role": User.Role.ADMIN, "is_staff": True, "is_superuser": True},
        )
        if created:
            admin_user.set_password("Admin123!")
            admin_user.save(update_fields=["password"])

        room_101, _ = Room.objects.get_or_create(number="101", defaults={"floor": 1, "capacity": 4, "description": "East wing"})
        room_102, _ = Room.objects.get_or_create(number="102", defaults={"floor": 1, "capacity": 3, "description": "East wing"})
        Room.objects.get_or_create(number="201", defaults={"floor": 2, "capacity": 4, "description": "North wing"})

        rules = [
            ("DR-001", "Quiet hours", "Conduct", "Keep noise to a minimum from 10:00 PM to 7:00 AM.", "medium"),
            ("DR-002", "No alcohol containers", "Safety", "Alcoholic drinks and their containers are prohibited in residence areas.", "high"),
            ("DR-003", "Fire safety", "Safety", "Open flames, smoking, and tampering with fire equipment are prohibited.", "critical"),
            ("DR-004", "Guest registration", "Security", "All visitors must be registered and follow guest hours.", "medium"),
        ]
        rule_objects = {}
        for code, title, category, description, severity in rules:
            rule_objects[code], _ = DormitoryRule.objects.get_or_create(
                code=code, defaults={"title": title, "category": category, "description": description, "severity": severity}
            )

        tenant_one, _ = Tenant.objects.get_or_create(
            email="jordan.lee@example.test",
            defaults={"first_name": "Jordan", "last_name": "Lee", "phone": "09170000001", "room": room_101, "move_in_date": timezone.localdate()},
        )
        Tenant.objects.get_or_create(
            email="casey.santos@example.test",
            defaults={"first_name": "Casey", "last_name": "Santos", "phone": "09170000002", "room": room_102, "move_in_date": timezone.localdate()},
        )
        source, _ = CameraSource.objects.get_or_create(
            name="Lobby browser camera", defaults={"source_type": "webcam", "location": "Main lobby", "room": None}
        )
        incident = Incident.objects.filter(details__startswith="Sample verified").first()
        if not incident:
            incident = Incident.objects.create(
                incident_type=Incident.Type.MANUAL,
                details="Sample verified quiet-hours report.",
                source=source,
                status=Incident.Status.ASSIGNED,
                verified_by=manager,
                verified_at=timezone.now(),
                assigned_tenant=tenant_one,
                room=room_101,
                review_notes="Seeded manager verification.",
            )
        Warning.objects.get_or_create(
            tenant=tenant_one, rule=rule_objects["DR-001"], incident=incident,
            defaults={"message": "Please observe quiet hours.", "issued_by": manager},
        )
        Violation.objects.get_or_create(
            tenant=tenant_one, rule=rule_objects["DR-001"], incident=incident,
            defaults={"description": "Verified repeat noise report for demonstration.", "action_taken": "Manager counselling", "recorded_by": manager},
        )
        self.stdout.write(self.style.SUCCESS("Demo data ready. Login: manager / Manager123! or admin / Admin123!"))
