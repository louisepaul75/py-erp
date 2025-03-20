"""
Tests for the core API views module.
"""
import pytest
import json
from django.test import RequestFactory
from django.contrib.auth.models import User, AnonymousUser
from unittest.mock import patch, MagicMock
from pyerp.core.views import (
    UserProfileView, 
    DashboardSummaryView, 
    SystemSettingsView
)
from pyerp.core.models import UserPreference
from rest_framework.test import force_authenticate


@pytest.fixture
def user():
    """Create a test user."""
    return User.objects.create_user(
        username='testuser',
        email='test@example.com',
        password='password123',
        first_name='Test',
        last_name='User',
        is_staff=False
    )


@pytest.fixture
def admin_user():
    """Create a test admin user."""
    return User.objects.create_user(
        username='adminuser',
        email='admin@example.com',
        password='admin123',
        first_name='Admin',
        last_name='User',
        is_staff=True,
        is_superuser=True
    )


@pytest.fixture
def rf():
    """Request factory fixture."""
    return RequestFactory()


class TestUserProfileView:
    """Tests for the UserProfileView."""

    def test_get_user_profile(self, rf, user):
        """Test retrieving the user profile."""
        # Create a preference for the user
        UserPreference.objects.create(
            user=user,
            key='theme',
            value='dark'
        )
        
        view = UserProfileView.as_view()
        request = rf.get('/api/profile/')
        force_authenticate(request, user=user)
        response = view(request)
        
        assert response.status_code == 200
        assert 'profile' in response.data
        assert 'preferences' in response.data
        assert response.data['preferences'][0]['key'] == 'theme'
        assert response.data['preferences'][0]['value'] == 'dark'

    def test_update_user_profile(self, rf, user):
        """Test updating the user profile."""
        view = UserProfileView.as_view()
        
        # Create initial preference
        UserPreference.objects.create(
            user=user,
            key='theme',
            value='light'
        )
        
        # Update preferences
        request_data = {
            'preferences': [
                {'key': 'theme', 'value': 'dark'},
                {'key': 'sidebar', 'value': 'collapsed'}
            ]
        }
        
        request = rf.patch(
            '/api/profile/',
            data=json.dumps(request_data),
            content_type='application/json'
        )
        force_authenticate(request, user=user)
        response = view(request)
        
        assert response.status_code == 200
        
        # Verify preferences were updated
        preferences = UserPreference.objects.filter(user=user)
        assert preferences.count() == 2
        
        # Find the theme preference
        theme_pref = next((p for p in preferences if p.key == 'theme'), None)
        assert theme_pref is not None
        assert theme_pref.value == 'dark'
        
        # Find the sidebar preference
        sidebar_pref = next((p for p in preferences if p.key == 'sidebar'), None)
        assert sidebar_pref is not None
        assert sidebar_pref.value == 'collapsed'


class TestDashboardSummaryView:
    """Tests for the DashboardSummaryView."""

    @patch('pyerp.core.views.DashboardSummaryView._get_dashboard_data')
    def test_get_dashboard_summary(self, mock_get_data, rf, user):
        """Test retrieving the dashboard summary."""
        mock_get_data.return_value = {
            'recent_activity': [],
            'statistics': {'orders': 10, 'revenue': 1000}
        }
        
        view = DashboardSummaryView.as_view()
        request = rf.get('/api/dashboard/')
        force_authenticate(request, user=user)
        response = view(request)
        
        assert response.status_code == 200
        assert 'statistics' in response.data
        assert 'recent_activity' in response.data
        assert response.data['statistics']['orders'] == 10


class TestSystemSettingsView:
    """Tests for the SystemSettingsView."""

    @patch('pyerp.core.views.SystemSettingsView._get_system_settings')
    def test_get_system_settings_staff(self, mock_get_settings, rf, admin_user):
        """Test retrieving system settings as staff user."""
        mock_get_settings.return_value = {
            'app_version': '1.0.0',
            'environment': 'test',
            'database': 'sqlite'
        }
        
        view = SystemSettingsView.as_view()
        request = rf.get('/api/settings/')
        force_authenticate(request, user=admin_user)
        response = view(request)
        
        assert response.status_code == 200
        assert 'app_version' in response.data
        assert 'environment' in response.data

    def test_get_system_settings_non_staff(self, rf, user):
        """Test retrieving system settings as non-staff user."""
        view = SystemSettingsView.as_view()
        request = rf.get('/api/settings/')
        force_authenticate(request, user=user)
        response = view(request)
        
        assert response.status_code == 403

    @patch('pyerp.core.views.SystemSettingsView._update_system_settings')
    def test_update_system_settings_superuser(self, mock_update_settings, rf, admin_user):
        """Test updating system settings as superuser."""
        mock_update_settings.return_value = True
        
        view = SystemSettingsView.as_view()
        request_data = {
            'maintenance_mode': True,
            'system_message': 'System under maintenance'
        }
        
        request = rf.patch(
            '/api/settings/',
            data=json.dumps(request_data),
            content_type='application/json'
        )
        force_authenticate(request, user=admin_user)
        response = view(request)
        
        assert response.status_code == 200
        mock_update_settings.assert_called_once_with(request_data) 