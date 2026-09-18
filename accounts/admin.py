from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User


@admin.register(User)
class DormitoryUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (("Dormitory", {"fields": ("role",)}),)
    add_fieldsets = UserAdmin.add_fieldsets + (("Dormitory", {"fields": ("role",)}),)
