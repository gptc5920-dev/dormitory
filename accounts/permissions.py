from rest_framework.permissions import BasePermission


class IsDormitoryManager(BasePermission):
    message = "Administrator or manager access is required."

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.is_dormitory_manager)
