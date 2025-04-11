"""
Tests for the core API views module.
"""
import pytest
import json
from django.test import RequestFactory
from django.contrib.auth.models import User
from unittest.mock import patch
from pyerp.core.views import (
    UserProfileView, 
    DashboardSummaryView, 
    SystemSettingsView
)
from pyerp.core.models import UserPreference
from rest_framework.test import force_authenticate
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from django.conf import settings


@pytest.fixture
def user(db):
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
def admin_user(db):
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


@pytest.mark.core
@pytest.mark.backend
@pytest.mark.api
class TestUserProfileView:
    """Tests for the UserProfileView."""

    def test_get_user_profile(self, rf, user):
        """Test retrieving the user profile."""
        # Create a preference for the user
        UserPreference.objects.create(
            user=user,
            dashboard_config={"theme": "dark"}
        )
        
        view = UserProfileView.as_view()
        request = rf.get('/api/profile/')
        force_authenticate(request, user=user)
        response = view(request)
        
        assert response.status_code == 200
        assert 'profile' in response.data
        assert 'preferences' in response.data
        assert 'dashboard_config' in response.data['preferences']
        assert (
            response.data['preferences']['dashboard_config']['theme'] == 'dark'
        )

    def test_update_user_profile(self, rf, user):
        """Test updating the user profile."""
        view = UserProfileView.as_view()
        
        # Create initial preference
        UserPreference.objects.create(
            user=user,
            dashboard_config={"theme": "light"}
        )
        
        # Update preferences
        request_data = {
            'preferences': {
                'dashboard_config': {
                    'theme': 'dark',
                    'sidebar': 'collapsed'
                }
            }
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
        assert preferences.count() == 1
        
        # Get the preference
        pref = preferences.first()
        assert pref.dashboard_config['theme'] == 'dark'
        assert pref.dashboard_config['sidebar'] == 'collapsed'


@pytest.mark.core
@pytest.mark.backend
@pytest.mark.api
class TestDashboardSummaryView:
    """Tests for the DashboardSummaryView."""

    @patch('pyerp.core.views.DashboardSummaryView.get_dashboard_data')
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


@pytest.mark.core
@pytest.mark.backend
@pytest.mark.api
class TestSystemSettingsView:
    """Tests for the SystemSettingsView."""

    @patch('pyerp.core.views.SystemSettingsView.get_system_settings')
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

    @patch('pyerp.core.views.SystemSettingsView.update_system_settings')
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


@pytest.mark.core
@pytest.mark.backend
@pytest.mark.api
class TestAuthAPIViews:
    """Tests for Authentication related API views (CSRF, Token)."""

    @pytest.fixture
    def api_client(self):
        """APIClient fixture."""
        return APIClient()
    
    @pytest.fixture
    def setup_test_urls(self):
        """Set up test URLs for isolated testing."""
        from django.urls import include, path
        from django.conf.urls.static import static
        
        from django.urls.base import clear_url_caches
        import sys
        
        # Import test URL patterns
        from pyerp.core.tests.api_views_test_urls import urlpatterns as test_urlpatterns
        
        # Store the original ROOT_URLCONF
        from django.conf import settings
        original_urlconf = settings.ROOT_URLCONF
        
        # Set up test URL patterns
        settings.ROOT_URLCONF = 'pyerp.core.tests.api_views_test_urls'
        
        # Clear URL caches
        clear_url_caches()
        
        yield
        
        # Restore original URL conf after test
        settings.ROOT_URLCONF = original_urlconf
        clear_url_caches()
        
        # Clean up any imported modules if needed
        if 'pyerp.core.tests.api_views_test_urls' in sys.modules:
            del sys.modules['pyerp.core.tests.api_views_test_urls']

    def test_csrf_token_view(self, api_client, setup_test_urls):
        """Test the csrf_token view returns a token and sets the cookie."""
        # Use the literal URL path as reverse() is not working reliably
        url = '/api/csrf/'

        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        # Convert the JSON content to Python
        response_data = json.loads(response.content.decode('utf-8'))
        assert 'csrf_token' in response_data
        assert response_data['csrf_token'] is not None
        assert settings.CSRF_COOKIE_NAME in response.cookies

    def test_token_obtain_pair_success(self, api_client, user, setup_test_urls):
        """Test successful token retrieval with valid credentials."""
        # Use the literal URL path as reverse() is not working reliably
        url = '/api/token/'
        data = {
            'username': 'testuser',
            'password': 'password123'
        }
        response = api_client.post(url, data, format='json')

        assert response.status_code == status.HTTP_200_OK
        assert 'access' in response.data
        assert 'refresh' in response.data
        assert response.data['access'] is not None
        assert response.data['refresh'] is not None

    def test_token_obtain_pair_invalid_credentials(self, api_client, user, setup_test_urls):
        """Test token retrieval failure with invalid credentials."""
        # Use the literal URL path as reverse() is not working reliably
        url = '/api/token/'
        data = {
            'username': 'testuser',
            'password': 'wrongpassword'
        }
        response = api_client.post(url, data, format='json')

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert 'access' not in response.data
        assert 'refresh' not in response.data

    def test_token_obtain_pair_missing_credentials(self, api_client, setup_test_urls):
        """Test token retrieval failure with missing credentials."""
        # Use the literal URL path as reverse() is not working reliably
        url = '/api/token/'
        # Missing password
        data_missing_pw = {'username': 'testuser'}
        response_missing_pw = api_client.post(
            url, data_missing_pw, format='json'
        )
        assert response_missing_pw.status_code == status.HTTP_400_BAD_REQUEST

        # Missing username
        data_missing_user = {'password': 'password123'}
        response_missing_user = api_client.post(
            url, data_missing_user, format='json'
        )
        assert response_missing_user.status_code == status.HTTP_400_BAD_REQUEST

        # Missing both
        data_missing_all = {}
        response_missing_all = api_client.post(
            url, data_missing_all, format='json'
        )
        assert response_missing_all.status_code == status.HTTP_400_BAD_REQUEST 