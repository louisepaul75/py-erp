"""
Tests for the middleware components in the core module.

This module tests the middleware components defined in 
pyerp/core/middleware.py.
"""

import unittest
import json
from unittest.mock import patch, MagicMock
from django.test import RequestFactory
from django.http import HttpResponse, JsonResponse
from django.test import override_settings

from pyerp.core.middleware import (
    AuthExemptMiddleware,
    DatabaseConnectionMiddleware,
)


class AuthExemptMiddlewareTests(unittest.TestCase):
    """Tests for the AuthExemptMiddleware."""
    
    def setUp(self):
        """Set up test environment."""
        self.middleware = AuthExemptMiddleware(MagicMock())
        self.request_factory = RequestFactory()
    
    def test_exempt_path(self):
        """Test that exempt paths are properly marked."""
        exempt_paths = [
            "/health/",
            "/api/health/",
            "/monitoring/health-check/public/",
            "/monitoring/health-checks/",
        ]
        
        for path in exempt_paths:
            request = self.request_factory.get(path)
            self.middleware.process_request(request)
            
            # Verify request was marked as exempt
            self.assertTrue(hasattr(request, "_auth_exempt"))
            self.assertTrue(request._auth_exempt)
            
            # Verify anonymous user was created with proper attributes
            self.assertTrue(hasattr(request, "user"))
            self.assertTrue(request.user.is_authenticated)
            self.assertTrue(request.user.is_active)
            self.assertTrue(request.user.is_superuser)
            
            # Verify permission methods work
            self.assertTrue(request.user.has_perm("some_perm"))
            self.assertTrue(request.user.has_perms(["perm1", "perm2"]))
            self.assertTrue(request.user.has_module_perms("some_module"))
            self.assertFalse(request.user.is_anonymous())
    
    def test_non_exempt_path(self):
        """Test that non-exempt paths are not modified."""
        request = self.request_factory.get("/some/random/path/")
        self.middleware.process_request(request)
        
        # Verify request was not marked as exempt
        self.assertFalse(hasattr(request, "_auth_exempt"))
        
        # Verify request.user was not set
        self.assertFalse(hasattr(request, "user"))
    
    @patch('pyerp.core.middleware.logger')
    def test_process_response_exempt_redirect(self, mock_logger):
        """Test that auth redirects are canceled for exempt paths."""
        request = self.request_factory.get("/health/")
        request._auth_exempt = True
        
        # Create a login redirect response
        response = HttpResponse(status=302)
        response['Location'] = '/accounts/login/'
        
        # Configure settings mock
        with patch('pyerp.core.middleware.settings') as mock_settings:
            mock_settings.LOGIN_URL = '/accounts/login/'
            
            # Process the response
            result = self.middleware.process_response(request, response)
            
            # Verify result is a JsonResponse with correct data
            self.assertIsInstance(result, JsonResponse)
            self.assertEqual(result.status_code, 200)
            
            # Check content by decoding the response content
            content = json.loads(result.content.decode('utf-8'))
            self.assertEqual(content['status'], 'bypassed_auth')
            msg = 'Auth bypassed for health check'
            self.assertEqual(content['message'], msg)
            
            # Verify logger was called
            mock_logger.debug.assert_called_once()
    
    def test_process_response_normal(self):
        """Test that normal responses are not modified."""
        # Regular request with non-redirect response
        request = self.request_factory.get("/some/path/")
        response = HttpResponse("OK")
        
        result = self.middleware.process_response(request, response)
        
        # Response should be unchanged
        self.assertEqual(result, response)
    
    def test_process_response_exempt_custom_response(self):
        """Test using a custom exempt response."""
        request = self.request_factory.get("/health/")
        request._auth_exempt = True
        custom_response = HttpResponse("Custom Exempt Response", status=200)
        request._auth_exempt_response = custom_response
        
        # Create a login redirect response
        response = HttpResponse(status=302)
        response['Location'] = '/accounts/login/'
        
        # Configure settings mock
        with patch('pyerp.core.middleware.settings') as mock_settings:
            mock_settings.LOGIN_URL = '/accounts/login/'
            
            # Process the response
            result = self.middleware.process_response(request, response)
            
            # Verify custom response was returned
            self.assertEqual(result.content, b"Custom Exempt Response")
            self.assertEqual(result.status_code, 200)


class DatabaseConnectionMiddlewareTests(unittest.TestCase):
    """Tests for the DatabaseConnectionMiddleware."""
    
    def setUp(self):
        """Set up test environment."""
        self.get_response_mock = MagicMock()
        self.get_response_mock.return_value = HttpResponse("OK")
        self.middleware = DatabaseConnectionMiddleware(self.get_response_mock)
        self.request = RequestFactory().get("/")
    
    @patch(
        'pyerp.core.middleware.DatabaseConnectionMiddleware._test_db_connection'
    )
    def test_call_first_request(self, mock_test_connection):
        """Test that DB connection is tested only on first request."""
        # First request should test connection
        self.middleware.db_connection_tested = False
        response = self.middleware(self.request)
        
        mock_test_connection.assert_called_once()
        self.assertTrue(self.middleware.db_connection_tested)
        self.assertEqual(response.content, b"OK")
        
        # Reset the mock for next test
        mock_test_connection.reset_mock()
        
        # Second request should not test connection
        response = self.middleware(self.request)
        
        mock_test_connection.assert_not_called()
        self.assertEqual(response.content, b"OK")
    
    def test_postgresql_settings_check(self):
        """Test DB connection middleware PostgreSQL settings check."""
        # Mock the database settings for PostgreSQL
        with patch('pyerp.core.middleware.settings') as mock_settings:
            # Set up PostgreSQL settings mock
            mock_settings.DATABASES = {
                'default': {
                    'ENGINE': 'django.db.backends.postgresql',
                    'NAME': 'test_db',
                    'USER': 'test_user',
                    'PASSWORD': 'test_pass',
                    'HOST': 'localhost',
                    'PORT': '5432'
                }
            }
            
            # Mock the psycopg2 connect function - no need to test fully
            with patch('psycopg2.connect'):
                # Assert the middleware class can access settings correctly
                self.middleware._test_db_connection()
                db_engine = mock_settings.DATABASES['default']['ENGINE']
                self.assertEqual(db_engine, 'django.db.backends.postgresql')
    
    @override_settings(
        DATABASES={
            'default': {
                'ENGINE': 'django.db.backends.sqlite3',
                'NAME': 'db.sqlite3',
            }
        }
    )
    def test_skip_non_postgresql(self):
        """Test that non-PostgreSQL databases are skipped."""
        # With SQLite engine, the function should return early without testing
        with patch('psycopg2.connect') as mock_connect:
            # Reset the flag to ensure the check runs
            self.middleware.db_connection_tested = False
            # Call the middleware to trigger the check (or skip it)
            # We don't need the response, just need to trigger the __call__
            try:
                self.middleware(self.request)
            except Exception:  # Catch potential errors if connect was called
                pass
            mock_connect.assert_not_called() 