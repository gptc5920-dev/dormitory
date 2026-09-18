from django.core.exceptions import ValidationError
from django.db import connection
from django.db.models import Count, Q
from django.test import TestCase
from django.test.utils import CaptureQueriesContext

from .models import Room, Tenant
from .serializers import RoomSerializer


class TenantModelTests(TestCase):
    def test_room_capacity(self):
        room = Room.objects.create(number="T1", capacity=1)
        Tenant.objects.create(first_name="First", last_name="Tenant", room=room)
        with self.assertRaises(ValidationError):
            Tenant.objects.create(first_name="Second", last_name="Tenant", room=room)

    def test_room_list_uses_annotated_occupancy_without_n_plus_one_queries(self):
        for index in range(5):
            room = Room.objects.create(number=f"Q{index}", capacity=2)
            Tenant.objects.create(first_name="Query", last_name=str(index), room=room)
        queryset = Room.objects.annotate(
            occupancy=Count("tenants", filter=Q(tenants__is_active=True))
        )
        with CaptureQueriesContext(connection) as queries:
            data = RoomSerializer(queryset, many=True).data
        self.assertEqual(len(data), 5)
        self.assertEqual(len(queries), 1)
