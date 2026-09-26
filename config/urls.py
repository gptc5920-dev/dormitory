from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from accounts.views import LoginView, LogoutView, MeView, UserViewSet
from monitoring.views import (
    CameraSourceViewSet,
    DashboardSummaryView,
    DetectFrameView,
    DetectorStatusView,
    IncidentViewSet,
    ReportSummaryView,
    VideoJobViewSet,
)
from tenants.views import RoomViewSet, TenantViewSet
from violations.views import DormitoryRuleViewSet, ViolationViewSet, WarningViewSet
from .health import health
from .views import index


router = DefaultRouter()
router.register("users", UserViewSet, basename="user")
router.register("rooms", RoomViewSet, basename="room")
router.register("tenants", TenantViewSet, basename="tenant")
router.register("rules", DormitoryRuleViewSet, basename="rule")
router.register("incidents", IncidentViewSet, basename="incident")
router.register("warnings", WarningViewSet, basename="warning")
router.register("violations", ViolationViewSet, basename="violation")
router.register("camera-sources", CameraSourceViewSet)
router.register("video-jobs", VideoJobViewSet)

urlpatterns = [
    path("", index, name="backend-index"),
    path("api/health/", health, name="health"),
    path("admin/", admin.site.urls),
    path("api/auth/login/", LoginView.as_view(), name="login"),
    path("api/auth/logout/", LogoutView.as_view(), name="logout"),
    path("api/auth/me/", MeView.as_view(), name="me"),
    path("api/dashboard/summary/", DashboardSummaryView.as_view(), name="dashboard-summary"),
    path("api/reports/summary/", ReportSummaryView.as_view(), name="report-summary"),
    path("api/monitoring/status/", DetectorStatusView.as_view(), name="detector-status"),
    path("api/monitoring/detect-frame/", DetectFrameView.as_view(), name="detect-frame"),
    path("api/", include(router.urls)),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
