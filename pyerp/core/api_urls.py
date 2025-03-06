from django.urls import path

from pyerp.core.views import health_check, UserProfileView, DashboardSummaryView, SystemSettingsView  # noqa: E501

# Core API URLs
urlpatterns = [
  # noqa: F841
    path('health/', health_check, name='api-health-check'),
    path('profile/', UserProfileView.as_view(), name='api-user-profile'),
    path('dashboard/', DashboardSummaryView.as_view(), name='api-dashboard-summary'),  # noqa: E501
    path('settings/', SystemSettingsView.as_view(), name='api-system-settings'),  # noqa: E501
  # noqa: E501, F841
]
