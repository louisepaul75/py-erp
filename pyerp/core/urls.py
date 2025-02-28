"""
URL Configuration for the Core app.
"""

from django.urls import path

from . import views

app_name = 'core'

urlpatterns = [
    # Health check endpoint
    path('health/', views.health_check, name='health_check'),
    
    # User profile endpoints
    path('users/profile/', views.UserProfileView.as_view(), name='user_profile'),
    
    # Dashboard data endpoints
    path('dashboard/summary/', views.DashboardSummaryView.as_view(), name='dashboard_summary'),
    
    # System settings
    path('settings/', views.SystemSettingsView.as_view(), name='system_settings'),
    
    # Test DB error endpoint (for testing only)
    path('test-db-error/', views.test_db_error, name='test_db_error'),
] 