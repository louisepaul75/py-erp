"""
Tests for URL patterns.

This module tests the URL routing configuration for the core app,
ensuring that all URL patterns are properly registered and resolved.
"""

from django.test import TestCase
from django.urls import reverse, resolve, NoReverseMatch
from django.contrib.auth import get_user_model

from pyerp.core import views, api_urls
from pyerp.core.models import AuditLog

User = get_user_model()


class CoreUrlPatternsTests(TestCase):
    """Tests for core URL patterns."""
    
    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='password123'
        )
        self.client.login(username='testuser', password='password123')
        
    def test_dashboard_url(self):
        """Test the dashboard URL pattern."""
        url = reverse('core:dashboard')
        self.assertEqual(url, '/dashboard/')
        
        resolver = resolve('/dashboard/')
        self.assertEqual(resolver.view_name, 'core:dashboard')
        self.assertEqual(resolver.func.__name__, views.dashboard.__name__)
        
    def test_profile_url(self):
        """Test the profile URL pattern."""
        url = reverse('core:profile')
        self.assertEqual(url, '/profile/')
        
        resolver = resolve('/profile/')
        self.assertEqual(resolver.view_name, 'core:profile')
        self.assertEqual(resolver.func.__name__, views.profile.__name__)
        
    def test_settings_url(self):
        """Test the settings URL pattern."""
        url = reverse('core:settings')
        self.assertEqual(url, '/settings/')
        
        resolver = resolve('/settings/')
        self.assertEqual(resolver.view_name, 'core:settings')
        self.assertEqual(resolver.func.__name__, views.settings.__name__)
        
    def test_url_with_parameters(self):
        """Test URL patterns with parameters."""
        # Test audit log detail URL with ID parameter
        log = AuditLog.objects.create(
            event_type=AuditLog.EventType.LOGIN,
            message="User logged in",
            user=self.user
        )
        
        url = reverse('core:audit_log_detail', kwargs={'pk': log.pk})
        self.assertEqual(url, f'/audit-logs/{log.pk}/')
        
        resolver = resolve(f'/audit-logs/{log.pk}/')
        self.assertEqual(resolver.view_name, 'core:audit_log_detail')
        self.assertEqual(resolver.kwargs['pk'], str(log.pk))
        
    def test_named_url_parameters(self):
        """Test URL patterns with named parameters."""
        # Example: /users/<username>/
        url = reverse('core:user_detail', kwargs={'username': 'testuser'})
        self.assertEqual(url, '/users/testuser/')
        
        resolver = resolve('/users/testuser/')
        self.assertEqual(resolver.view_name, 'core:user_detail')
        self.assertEqual(resolver.kwargs['username'], 'testuser')
        
    def test_api_url_patterns(self):
        """Test API URL patterns."""
        # Test auth token URL
        url = reverse('core_api:token_obtain')
        self.assertEqual(url, '/api/token/')
        
        resolver = resolve('/api/token/')
        self.assertEqual(resolver.view_name, 'core_api:token_obtain')
        
        # Test refresh token URL
        url = reverse('core_api:token_refresh')
        self.assertEqual(url, '/api/token/refresh/')
        
        resolver = resolve('/api/token/refresh/')
        self.assertEqual(resolver.view_name, 'core_api:token_refresh')
        
        # Test API user profile URL
        url = reverse('core_api:user-profile')
        self.assertEqual(url, '/api/user/profile/')
        
        resolver = resolve('/api/user/profile/')
        self.assertEqual(resolver.view_name, 'core_api:user-profile')
        
    def test_nonexistent_url(self):
        """Test that nonexistent URLs raise NoReverseMatch."""
        with self.assertRaises(NoReverseMatch):
            reverse('core:nonexistent_url')
            
    def test_url_response_codes(self):
        """Test response codes for core URLs."""
        # Dashboard should be accessible to logged-in users
        response = self.client.get(reverse('core:dashboard'))
        self.assertEqual(response.status_code, 200)
        
        # Profile should be accessible to logged-in users
        response = self.client.get(reverse('core:profile'))
        self.assertEqual(response.status_code, 200)
        
        # Logout, then test that dashboard redirects to login
        self.client.logout()
        response = self.client.get(reverse('core:dashboard'))
        self.assertEqual(response.status_code, 302)  # Redirect to login
        
    def test_api_auth_requirements(self):
        """Test that API endpoints require authentication."""
        # Logout to test unauthenticated access
        self.client.logout()
        
        # Test user profile API endpoint
        response = self.client.get(reverse('core_api:user-profile'))
        self.assertEqual(response.status_code, 401)  # Unauthorized
        
        # Login and try again
        self.client.login(username='testuser', password='password123')
        response = self.client.get(reverse('core_api:user-profile'))
        self.assertEqual(response.status_code, 200)
        
    def test_url_name_consistency(self):
        """Test that URL naming follows consistent patterns."""
        # Detail views should end with _detail
        self.assertTrue(hasattr(reverse, 'core:user_detail'))
        self.assertTrue(hasattr(reverse, 'core:audit_log_detail'))
        
        # List views should end with _list
        self.assertTrue(hasattr(reverse, 'core:audit_log_list'))
        self.assertTrue(hasattr(reverse, 'core:user_list'))
        
        # API list views should follow DRF conventions
        self.assertTrue(hasattr(reverse, 'core_api:user-list'))
        self.assertTrue(hasattr(reverse, 'core_api:audit-log-list'))
        
        # API detail views should follow DRF conventions
        self.assertTrue(hasattr(reverse, 'core_api:user-detail'))
        self.assertTrue(hasattr(reverse, 'core_api:audit-log-detail')) 