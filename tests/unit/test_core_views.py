"""
Unit tests for core views.

This file demonstrates how to test views in the core module.
"""
import pytest
from unittest.mock import patch, MagicMock
from django.http import JsonResponse
from django.conf import settings

# Mock the Django REST framework imports to avoid metaclass conflict
import sys
from unittest.mock import MagicMock

# Create mock classes for Django REST framework
class MockAPIRequestFactory:
    def get(self, path, format=None, **kwargs):
        request = MagicMock()
        request.method = 'GET'
        request.path = path
        request.query_params = kwargs
        return request
        
    def post(self, path, data=None, format=None, **kwargs):
        request = MagicMock()
        request.method = 'POST'
        request.path = path
        request.data = data or {}
        return request
        
    def put(self, path, data=None, format=None, **kwargs):
        request = MagicMock()
        request.method = 'PUT'
        request.path = path
        request.data = data or {}
        return request

# Mock the status codes
class MockStatus:
    HTTP_200_OK = 200
    HTTP_201_CREATED = 201
    HTTP_204_NO_CONTENT = 204
    HTTP_400_BAD_REQUEST = 400
    HTTP_401_UNAUTHORIZED = 401
    HTTP_403_FORBIDDEN = 403
    HTTP_404_NOT_FOUND = 404
    HTTP_500_INTERNAL_SERVER_ERROR = 500

# Use the mocks instead of the real imports
sys.modules['rest_framework.test'] = MagicMock()
sys.modules['rest_framework.test'].APIRequestFactory = MockAPIRequestFactory
sys.modules['rest_framework'] = MagicMock()
sys.modules['rest_framework'].status = MockStatus

# Now import the views
from pyerp.core.views import health_check, UserProfileView

# Initialize the API request factory
@pytest.fixture
def api_factory():
    """Create an API request factory."""
    return MockAPIRequestFactory()


@pytest.fixture
def mock_user():
    """Create a mock user for testing."""
    user = MagicMock()
    user.id = 1
    user.username = 'testuser'
    user.email = 'test@example.com'
    user.profile = MagicMock()
    user.profile.bio = 'Test bio'
    user.profile.location = 'Test location'
    user.profile.website = 'https://example.com'
    user.profile.save = MagicMock()
    return user


class TestHealthCheckView:
    """Tests for the health_check view."""
    
    @patch('pyerp.core.views.connection')
    def test_health_check_healthy(self, mock_connection, api_factory):
        """Test the health check view when everything is healthy."""
        # Set up the mock connection
        mock_connection.ensure_connection.return_value = None
        
        # Create a request
        request = api_factory.get('/api/health/')
        
        # Call the view
        response = health_check(request)
        
        # Check the response
        assert isinstance(response, JsonResponse)
        assert response.status_code == 200
        
        # Parse the JSON response
        import json
        data = json.loads(response.content.decode('utf-8'))
        
        # Check the response data
        assert data['status'] == 'healthy'
        assert 'database' in data
        assert data['database']['status'] == 'connected'
    
    @patch('pyerp.core.views.connection')
    def test_health_check_db_error(self, mock_connection, api_factory):
        """Test the health check view when the database is not healthy."""
        # Set up the mock connection to raise an exception
        mock_connection.ensure_connection.side_effect = Exception('Database error')
        
        # Create a request
        request = api_factory.get('/api/health/')
        
        # Call the view
        response = health_check(request)
        
        # Check the response
        assert isinstance(response, JsonResponse)
        assert response.status_code == 500
        
        # Parse the JSON response
        import json
        data = json.loads(response.content.decode('utf-8'))
        
        # Check the response data
        assert data['status'] == 'unhealthy'
        assert 'database' in data
        assert data['database']['status'] == 'error'
        assert 'Database error' in data['database']['message']


class TestUserProfileView:
    """Tests for the UserProfileView."""
    
    def test_get_profile(self, api_factory, mock_user):
        """Test getting a user profile."""
        # Create a request
        request = api_factory.get('/api/profile/')
        request.user = mock_user
        
        # Create the view
        view = UserProfileView()
        view.request = request
        
        # Call the get method
        response = view.get(request)
        
        # Check the response
        assert response.status_code == 200
        assert response.data['username'] == 'testuser'
        assert response.data['email'] == 'test@example.com'
        assert response.data['profile']['bio'] == 'Test bio'
        assert response.data['profile']['location'] == 'Test location'
        assert response.data['profile']['website'] == 'https://example.com'
    
    def test_update_profile_valid(self, api_factory, mock_user):
        """Test updating a user profile with valid data."""
        # Create a request with valid data
        data = {
            'email': 'new@example.com',
            'profile': {
                'bio': 'New bio',
                'location': 'New location',
                'website': 'https://new-example.com'
            }
        }
        request = api_factory.put('/api/profile/', data=data)
        request.user = mock_user
        
        # Create the view
        view = UserProfileView()
        view.request = request
        
        # Mock the serializer
        serializer = MagicMock()
        serializer.is_valid.return_value = True
        serializer.validated_data = data
        view.get_serializer = MagicMock(return_value=serializer)
        
        # Call the put method
        response = view.put(request)
        
        # Check the response
        assert response.status_code == 200
        
        # Check that the user was updated
        assert mock_user.email == 'new@example.com'
        assert mock_user.profile.bio == 'New bio'
        assert mock_user.profile.location == 'New location'
        assert mock_user.profile.website == 'https://new-example.com'
        assert mock_user.save.called
        assert mock_user.profile.save.called
    
    def test_update_profile_invalid(self, api_factory, mock_user):
        """Test updating a user profile with invalid data."""
        # Create a request with invalid data
        data = {
            'email': 'invalid-email',
            'profile': {
                'website': 'invalid-url'
            }
        }
        request = api_factory.put('/api/profile/', data=data)
        request.user = mock_user
        
        # Create the view
        view = UserProfileView()
        view.request = request
        
        # Mock the serializer
        serializer = MagicMock()
        serializer.is_valid.return_value = False
        serializer.errors = {
            'email': ['Enter a valid email address.'],
            'profile': {
                'website': ['Enter a valid URL.']
            }
        }
        view.get_serializer = MagicMock(return_value=serializer)
        
        # Call the put method
        response = view.put(request)
        
        # Check the response
        assert response.status_code == 400
        assert 'email' in response.data
        assert 'profile' in response.data
        assert 'website' in response.data['profile']
    
    def test_update_profile_mixed(self, api_factory, mock_user):
        """Test updating a user profile with mixed valid and invalid data."""
        # Create a request with mixed data
        data = {
            'email': 'new@example.com',  # Valid
            'profile': {
                'bio': 'New bio',  # Valid
                'website': 'invalid-url'  # Invalid
            }
        }
        request = api_factory.put('/api/profile/', data=data)
        request.user = mock_user
        
        # Create the view
        view = UserProfileView()
        view.request = request
        
        # Mock the serializer
        serializer = MagicMock()
        serializer.is_valid.return_value = False
        serializer.errors = {
            'profile': {
                'website': ['Enter a valid URL.']
            }
        }
        view.get_serializer = MagicMock(return_value=serializer)
        
        # Call the put method
        response = view.put(request)
        
        # Check the response
        assert response.status_code == 400
        assert 'profile' in response.data
        assert 'website' in response.data['profile']
        
        # Check that the user was not updated
        assert mock_user.email == 'test@example.com'
        assert mock_user.profile.bio == 'Test bio'
        assert not mock_user.save.called
        assert not mock_user.profile.save.called 