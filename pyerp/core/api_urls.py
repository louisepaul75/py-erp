from django.urls import path, include
from rest_framework import routers

from pyerp.core.views import (
    DashboardSummaryView,
    SystemSettingsView,
    UserProfileView,
    csrf_token,
    git_branch,
    health_check,
    DashboardDataView,
    AuditLogViewSet,
    TagViewSet,
    TaggedItemViewSet,
    NotificationViewSet,
)

app_name = 'core_api'

# Create a router for core API endpoints
router = routers.DefaultRouter()
router.register(r"audit-logs", AuditLogViewSet, basename="auditlog")
router.register(r"tags", TagViewSet, basename="tag")
router.register(r"tagged-items", TaggedItemViewSet, basename="taggeditem")
router.register(r"notifications", NotificationViewSet, basename="notification")

# Core API URLs - non-versioned (for backward compatibility)
urlpatterns = [
    path("csrf/", csrf_token, name="api-csrf-token"),
    path("health/", health_check, name="api-health-check"),
    path("git/branch/", git_branch, name="api-git-branch"),
    path(
        "profile/",
        UserProfileView.as_view(),
        name="api-user-profile",
    ),
    path(
        "dashboard/summary/",
        DashboardSummaryView.as_view(),
        name="api-dashboard-summary",
    ),
    path(
        "settings/",
        SystemSettingsView.as_view(),
        name="api-system-settings",
    ),
    path(
        "dashboard/",
        DashboardDataView.as_view(),
        name="dashboard-data",
    ),
    
    # Include versioned endpoints with a different namespace
    path("v1/", include([
        path("csrf/", csrf_token, name="api-csrf-token-v1"),
        path("health/", health_check, name="api-health-check-v1"),
        path("git/branch/", git_branch, name="api-git-branch-v1"),
        path(
            "profile/",
            UserProfileView.as_view(),
            name="api-user-profile-v1",
        ),
        path(
            "dashboard/summary/",
            DashboardSummaryView.as_view(),
            name="api-dashboard-summary-v1",
        ),
        path(
            "settings/",
            SystemSettingsView.as_view(),
            name="api-system-settings-v1",
        ),
    ])),
]
