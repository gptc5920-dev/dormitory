from django.contrib import admin

from .models import CameraSource, DetectionCooldown, Incident, VideoJob

admin.site.register(CameraSource)
admin.site.register(Incident)
admin.site.register(DetectionCooldown)
admin.site.register(VideoJob)
