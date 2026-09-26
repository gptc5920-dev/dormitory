from django.http import JsonResponse
from django.urls import reverse
from django.views.decorators.http import require_safe


@require_safe
def index(request):
    return JsonResponse({
        "service": "Smart Dormitory API",
        "api": reverse("api-root"),
        "health": reverse("health"),
        "admin": reverse("admin:index"),
    })
