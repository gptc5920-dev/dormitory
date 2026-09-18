from rest_framework import serializers

from .models import Room, Tenant


class RoomSerializer(serializers.ModelSerializer):
    capacity = serializers.IntegerField(min_value=1, max_value=50)
    occupancy = serializers.SerializerMethodField()
    available_beds = serializers.SerializerMethodField()

    class Meta:
        model = Room
        fields = ["id", "number", "floor", "capacity", "description", "is_active", "occupancy", "available_beds"]

    def get_occupancy(self, obj):
        annotated = getattr(obj, "occupancy", None)
        return annotated if annotated is not None else obj.tenants.filter(is_active=True).count()

    def get_available_beds(self, obj):
        return max(0, obj.capacity - self.get_occupancy(obj))

    def validate(self, attrs):
        if self.instance:
            occupancy = getattr(self.instance, "occupancy", None)
            if occupancy is None:
                occupancy = self.instance.tenants.filter(is_active=True).count()
            capacity = attrs.get("capacity", self.instance.capacity)
            if occupancy and not attrs.get("is_active", self.instance.is_active):
                raise serializers.ValidationError({"is_active": "Relocate active tenants before deactivating this room."})
            if capacity < occupancy:
                raise serializers.ValidationError({
                    "capacity": f"Capacity cannot be lower than the current occupancy ({occupancy})."
                })
        return attrs


class TenantSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(read_only=True)
    room_number = serializers.CharField(source="room.number", read_only=True)
    is_active = serializers.BooleanField(required=False, default=True)

    class Meta:
        model = Tenant
        fields = [
            "id", "reference", "first_name", "last_name", "full_name", "email", "phone",
            "emergency_contact", "room", "room_number", "enrolled_on", "move_in_date", "is_active", "notes",
        ]
        read_only_fields = ["reference", "enrolled_on"]

    def validate(self, attrs):
        room = attrs.get("room", getattr(self.instance, "room", None))
        active = attrs.get("is_active", getattr(self.instance, "is_active", True))
        if room and active:
            if not room.is_active:
                raise serializers.ValidationError({"room": "Active tenants must be assigned to an active room."})
            occupied = room.tenants.filter(is_active=True)
            if self.instance:
                occupied = occupied.exclude(pk=self.instance.pk)
            if occupied.count() >= room.capacity:
                raise serializers.ValidationError({"room": "This room is already at capacity."})
        return attrs


class RoomFilterSerializer(serializers.Serializer):
    active = serializers.ChoiceField(choices=("true", "false"), required=False)

    def validate_active(self, value):
        return value == "true"


class TenantFilterSerializer(serializers.Serializer):
    search = serializers.CharField(required=False, allow_blank=True, max_length=150)
    room = serializers.IntegerField(required=False, min_value=1)
    active = serializers.ChoiceField(choices=("true", "false"), required=False)

    def validate_active(self, value):
        return value == "true"
