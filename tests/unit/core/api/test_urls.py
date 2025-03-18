import pytest
from django.urls import include, path, reverse, resolve
from rest_framework.test import APITestCase, URLPatternsTestCase

from pyerp.core.views import (
    DashboardSummaryView,
    SystemSettingsView,
    UserProfileView,
    git_branch,
    health_check,
)


class TestCoreApiUrls(APITestCase, URLPatternsTestCase):
    """Test the core API URLs."""
    
    urlpatterns = [
        path('api/', include('pyerp.core.api_urls')),
    ]

    def test_health_check_url(self):
        """Test that the health check URL resolves to the health_check view."""
        url = "/api/health/"
        
        resolver = resolve(url)
        assert resolver.func == health_check
        assert resolver.url_name == "api-health-check"

    def test_git_branch_url(self):
        """Test that the git branch URL resolves to the git_branch view."""
        url = "/api/git/branch/"
        
        resolver = resolve(url)
        assert resolver.func == git_branch
        assert resolver.url_name == "api-git-branch"

    def test_user_profile_url(self):
        """Test that the user profile URL resolves to the UserProfileView."""
        url = "/api/profile/"
        
        resolver = resolve(url)
        assert resolver.func.view_class == UserProfileView
        assert resolver.url_name == "api-user-profile"

    def test_dashboard_summary_url(self):
        """Test that the dashboard summary URL resolves to the DashboardSummaryView."""
        url = "/api/dashboard/"
        
        resolver = resolve(url)
        assert resolver.func.view_class == DashboardSummaryView
        assert resolver.url_name == "api-dashboard-summary"

    def test_system_settings_url(self):
        """Test that the system settings URL resolves to the SystemSettingsView."""
        url = "/api/settings/"
        
        resolver = resolve(url)
        assert resolver.func.view_class == SystemSettingsView
        assert resolver.url_name == "api-system-settings" 