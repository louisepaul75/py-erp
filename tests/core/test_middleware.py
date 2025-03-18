"""
Tests for core middlewares in the pyERP system.
"""

import json
from unittest.mock import patch, MagicMock, PropertyMock

from django.conf import settings
from django.db.utils import OperationalError
from django.http import HttpResponse, JsonResponse
from django.test import TestCase, RequestFactory, override_settings

from pyerp.core.middleware import (
    DatabaseConnectionMiddleware,
    AuthExemptMiddleware
)


class TestDatabaseConnectionMiddleware(TestCase):
    """
    Tests for the DatabaseConnectionMiddleware which handles database errors.
    """

    def setUp(self):
        """Set up test data."""
        self.factory = RequestFactory()
        self.middleware = DatabaseConnectionMiddleware(
            self._get_response
        )

    def _get_response(self, request):
        """Mock get_response function that returns a simple HttpResponse."""
        return HttpResponse("Test response")

    def test_normal_request_flow(self):
        """Test that normal requests pass through the middleware."""
        request = self.factory.get('/some-path/')
        response = self.middleware(request)
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content.decode(), "Test response")

    def test_health_check_endpoint(self):
        """Test the health check endpoint response."""
        request = self.factory.get('/health/')
        
        with patch('django.db.connection') as mock_connection:
            # Mock successful database connection
            mock_connection.cursor.return_value.__enter__.return_value = MagicMock()
            
            response = self.middleware(request)
            
            # Verify response
            self.assertEqual(response.status_code, 200)
            self.assertIsInstance(response, JsonResponse)
            
            # Parse response data
            response_data = json.loads(response.content)
            self.assertEqual(response_data['status'], 'healthy')
            self.assertEqual(response_data['database']['status'], 'connected')

    def test_health_check_with_db_error(self):
        """Test health check response when database has errors."""
        request = self.factory.get('/health/')
        
        with patch('django.db.connection') as mock_connection:
            # Mock database connection error
            error_msg = "Test DB error"
            mock_connection.cursor.return_value.__enter__.side_effect = \
                OperationalError(error_msg)
            
            response = self.middleware(request)
            
            # Verify response
            self.assertEqual(response.status_code, 503)
            self.assertIsInstance(response, JsonResponse)
            
            # Parse response data
            response_data = json.loads(response.content)
            self.assertEqual(response_data['status'], 'unhealthy')
            self.assertEqual(response_data['database']['status'], 'error')
            self.assertIn(error_msg, response_data['database']['message'])

    def test_static_file_paths(self):
        """Test that static file paths are handled correctly."""
        static_paths = [
            '/static/css/style.css',
            '/media/images/logo.png',
            '/assets/js/script.js',
            '/favicon.ico',
        ]
        
        for path in static_paths:
            request = self.factory.get(path)
            response = self.middleware(request)
            
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.content.decode(), "Test response")

    def test_db_error_handling_for_regular_paths(self):
        """Test database error handling for regular paths."""
        request = self.factory.get('/some-path/')
        
        # Mock get_response to raise a database error
        def error_response(_):
            raise OperationalError("Test error")
            
        error_middleware = DatabaseConnectionMiddleware(error_response)
        
        response = error_middleware(request)
        
        # Verify error response
        self.assertEqual(response.status_code, 503)
        self.assertEqual(response.content.decode(), "Database connection error")

    def test_db_error_handling_for_api_paths(self):
        """Test database error handling for API paths."""
        request = self.factory.get('/api/some-endpoint/')
        
        # Mock get_response to raise a database error
        def error_response(_):
            raise OperationalError("Test error")
            
        error_middleware = DatabaseConnectionMiddleware(error_response)
        
        response = error_middleware(request)
        
        # Verify error response format for API
        self.assertEqual(response.status_code, 503)
        self.assertIsInstance(response, JsonResponse)
        
        response_data = json.loads(response.content)
        self.assertEqual(response_data['error'], "Database connection error")

    @patch('os.environ.get')
    @patch('pyerp.core.middleware.settings', spec=settings)
    def test_health_check_environment_info(self, mock_settings, mock_env_get):
        """Test that environment info is included in health check."""
        # Mock settings and environment variables
        mock_settings.DJANGO_SETTINGS_MODULE = 'pyerp.settings.production'
        mock_settings.APP_VERSION = '1.2.3'
        
        request = self.factory.get('/health/')
        
        with patch('django.db.connection'):
            response = self.middleware(request)
            
            # Verify environment info
            response_data = json.loads(response.content)
            self.assertEqual(response_data['environment'], 'production')
            self.assertEqual(response_data['version'], '1.2.3')

    @patch('os.environ.get')
    @patch('pyerp.core.middleware.settings', spec=settings)
    def test_health_check_missing_settings(self, mock_settings, mock_env_get):
        """Test health check with missing settings."""
        # Remove DJANGO_SETTINGS_MODULE attribute to trigger fallback
        type(mock_settings).DJANGO_SETTINGS_MODULE = PropertyMock(
            side_effect=AttributeError
        )
        # Configure APP_VERSION to be string, not MagicMock
        type(mock_settings).APP_VERSION = PropertyMock(return_value="1.0.0")
        mock_env_get.return_value = 'pyerp.settings.test'
        
        request = self.factory.get('/health/')
        
        with patch('django.db.connection'):
            response = self.middleware(request)
            
            # Verify environment fallback worked
            response_data = json.loads(response.content)
            self.assertEqual(response_data['environment'], 'test')


class TestAuthExemptMiddleware(TestCase):
    """
    Tests for AuthExemptMiddleware which exempts paths from authentication.
    """

    def setUp(self):
        """Set up test data."""
        self.factory = RequestFactory()
        self.middleware = AuthExemptMiddleware(
            self._get_response
        )

    def _get_response(self, request):
        """Mock get_response function that returns a simple HttpResponse."""
        return HttpResponse("Test response")

    def test_auth_exempt_paths(self):
        """Test that specified paths are exempt from authentication."""
        exempt_paths = [
            '/health/',
            '/api/health/',
            '/monitoring/health-check/public/',
            '/monitoring/health-checks/',
        ]
        
        for path in exempt_paths:
            request = self.factory.get(path)
            response = self.middleware(request)
            
            # Check that _auth_exempt flag is set
            self.assertTrue(getattr(request, '_auth_exempt', False))
            
            # Check that a user is added
            self.assertTrue(hasattr(request, 'user'))
            self.assertTrue(request.user.is_authenticated)
            self.assertTrue(request.user.is_active)
            self.assertTrue(request.user.is_superuser)
            
            # Test permission methods
            self.assertTrue(request.user.has_perm('some_perm'))
            self.assertTrue(request.user.has_perms(['perm1', 'perm2']))
            self.assertTrue(request.user.has_module_perms('some_module'))
            self.assertFalse(request.user.is_anonymous())
            
            # Verify response
            self.assertEqual(response.content.decode(), "Test response")

    def test_non_exempt_paths(self):
        """Test that non-exempt paths are not affected."""
        non_exempt_paths = [
            '/api/users/',
            '/products/',
            '/admin/',
        ]
        
        for path in non_exempt_paths:
            request = self.factory.get(path)
            response = self.middleware(request)
            
            # Check that _auth_exempt flag is not set
            self.assertFalse(hasattr(request, '_auth_exempt'))
            
            # User should not be set by this middleware
            self.assertFalse(hasattr(request, 'user'))
            
            # Verify response
            self.assertEqual(response.content.decode(), "Test response")

    @override_settings(LOGIN_URL='/login/')
    def test_auth_exempt_response_handling(self):
        """Test that auth exempt paths don't get redirected to login."""
        request = self.factory.get('/health/')
        request._auth_exempt = True
        
        # Create a redirect response as auth middleware might do
        redirect_response = HttpResponse(status=302)
        redirect_response['Location'] = '/login/?next=/health/'
        
        # Process the response
        response = self.middleware.process_response(
            request, redirect_response
        )
        
        # Verify the redirect was canceled
        self.assertNotEqual(response.status_code, 302)
        self.assertIsInstance(response, JsonResponse)
        
        response_data = json.loads(response.content)
        self.assertEqual(response_data['status'], 'bypassed_auth')

    def test_non_auth_response_handling(self):
        """Test that normal responses pass through unchanged."""
        request = self.factory.get('/api/users/')
        # No _auth_exempt set
        
        original_response = HttpResponse("Test content")
        response = self.middleware.process_response(
            request, original_response
        )
        
        # Verify response is unchanged
        self.assertEqual(response, original_response)
        self.assertEqual(response.content.decode(), "Test content")

    def test_auth_exempt_with_custom_response(self):
        """Test that custom responses are handled correctly."""
        request = self.factory.get('/health/')
        request._auth_exempt = True
        
        custom_response = JsonResponse({'status': 'custom'})
        response = self.middleware.process_response(
            request, custom_response
        )
        
        # Verify custom response is preserved
        self.assertEqual(response, custom_response)
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content)
        self.assertEqual(response_data['status'], 'custom') 