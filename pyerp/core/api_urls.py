from django.urls import path

from pyerp.core.views import health_check, UserProfileView, DashboardSummaryView, SystemSettingsView

# Core API URLs
urlpatterns = [
    path('health/', health_check, name='api-health-check'),
    path('profile/', UserProfileView.as_view(), name='api-user-profile'),
    path('dashboard/', DashboardSummaryView.as_view(), name='api-dashboard-summary'),
    path('settings/', SystemSettingsView.as_view(), name='api-system-settings'),
] 