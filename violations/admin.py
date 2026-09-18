from django.contrib import admin

from .models import DormitoryRule, Violation, Warning

admin.site.register(DormitoryRule)
admin.site.register(Warning)
admin.site.register(Violation)
