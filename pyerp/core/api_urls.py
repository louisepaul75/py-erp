from django.urls import path, include
from rest_framework import routers

from pyerp.core.views import (
    DashboardSummaryView,
    SystemSettingsView,
    UserProfileView,
    csrf_token,
    git_branch,
    health_check,
)

# Create a router for core API endpoints
router = routers.DefaultRouter()

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
