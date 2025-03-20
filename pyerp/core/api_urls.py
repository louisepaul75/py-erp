from django.urls import path

from pyerp.core.views import (
    DashboardSummaryView,
    SystemSettingsView,
    UserProfileView,
    git_branch,
    health_check,
)

# Core API URLs
urlpatterns = [
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
]
