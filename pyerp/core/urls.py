"""
URL Configuration for the Core app.
"""

from django.urls import path

from pyerp.core.views import (
    health_check, 
    UserProfileView, 
    DashboardSummaryView, 
    SystemSettingsView, 
    test_db_error
)

app_name = 'core'

# Core URLs for web interface
urlpatterns = [
    # Health check endpoint
    path('health/', health_check, name='health_check'),
    
    # User profile endpoints
    path('profile/', UserProfileView.as_view(), name='user_profile'),
    
    # Dashboard
    path('', DashboardSummaryView.as_view(), name='dashboard'),
    
    # System settings
    path('settings/', SystemSettingsView.as_view(), name='system_settings'),
    
    # Test endpoint for simulating database errors (for testing middleware)
    path('test-db-error/', test_db_error, name='test_db_error'),
] 