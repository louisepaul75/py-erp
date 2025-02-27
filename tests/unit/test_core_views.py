"""
Unit tests for core views.

This file demonstrates how to test views in the core module.
"""
import pytest
from unittest.mock import patch, MagicMock
from django.http import JsonResponse
from django.conf import settings
from rest_framework.test import APIRequestFactory
from rest_framework import status

from pyerp.core.views import health_check, UserProfileView

# Initialize the API request factory
@pytest.fixture
def api_factory():
    """Create an API request factory."""
    return APIRequestFactory()

@pytest.fixture
def mock_user():
    """Create a mock authenticated user."""
    user = MagicMock()
    user.id = 1
    user.username = "testuser"
    user.email = "test@example.com"
    user.first_name = "Test"
    user.last_name = "User"
    user.is_staff = False
    user.is_superuser = False
    user.date_joined = "2023-01-01T00:00:00Z"
    return user


class TestHealthCheckView:
    """Tests for the health_check view."""
    
    @patch('pyerp.core.views.connection')
    def test_health_check_healthy(self, mock_connection, api_factory):
        """Test health check when everything is working."""
        # Configure the mock
        mock_cursor = MagicMock()
        mock_connection.cursor.return_value.__enter__.return_value = mock_cursor
        mock_cursor.execute.return_value = None
        mock_cursor.fetchone.return_value = (1,)
        
        # Create request and get response
        request = api_factory.get('/health/')
        response = health_check(request)
        
        # Assert response is correct
        assert isinstance(response, JsonResponse)
        assert response.status_code == status.HTTP_200_OK
        
        # Parse the JSON response
        response_data = response.json()
        assert response_data['status'] == 'healthy'
        assert response_data['database'] == 'ok'
        assert 'version' in response_data
        assert 'environment' in response_data
    
    @patch('pyerp.core.views.connection')
    def test_health_check_db_error(self, mock_connection, api_factory):
        """Test health check when database is not working."""
        # Configure the mock to raise an exception
        mock_connection.cursor.return_value.__enter__.side_effect = Exception("DB Connection Error")
        
        # Create request and get response
        request = api_factory.get('/health/')
        response = health_check(request)
        
        # Assert response is correct
        assert isinstance(response, JsonResponse)
        assert response.status_code == status.HTTP_503_SERVICE_UNAVAILABLE
        
        # Parse the JSON response
        response_data = response.json()
        assert response_data['status'] == 'unhealthy'
        assert response_data['database'] == 'error'


class TestUserProfileView:
    """Tests for the UserProfileView."""
    
    def test_get_profile(self, api_factory, mock_user):
        """Test retrieving a user profile."""
        # Create a GET request
        request = api_factory.get('/api/profile/')
        request.user = mock_user
        
        # Get the response
        view = UserProfileView.as_view()
        response = view(request)
        
        # Assert response is correct
        assert response.status_code == status.HTTP_200_OK
        assert response.data['id'] == mock_user.id
        assert response.data['username'] == mock_user.username
        assert response.data['email'] == mock_user.email
        assert response.data['first_name'] == mock_user.first_name
        assert response.data['last_name'] == mock_user.last_name
        assert response.data['is_staff'] == mock_user.is_staff
        assert response.data['is_superuser'] == mock_user.is_superuser
        assert 'date_joined' in response.data
    
    def test_update_profile_valid(self, api_factory, mock_user):
        """Test updating a user profile with valid data."""
        # Create a PATCH request with valid data
        update_data = {
            'first_name': 'Updated',
            'last_name': 'Name',
            'email': 'updated@example.com'
        }
        request = api_factory.patch('/api/profile/', update_data, format='json')
        request.user = mock_user
        request.data = update_data  # Manually add data since we're not using the full DRF stack
        
        # Get the response
        view = UserProfileView.as_view()
        response = view(request)
        
        # Assert response is correct
        assert response.status_code == status.HTTP_200_OK
        assert 'message' in response.data
        assert 'updated_fields' in response.data
        assert len(response.data['updated_fields']) == 3
        
        # Assert user was updated
        assert mock_user.first_name == 'Updated'
        assert mock_user.last_name == 'Name'
        assert mock_user.email == 'updated@example.com'
        assert mock_user.save.called
    
    def test_update_profile_invalid(self, api_factory, mock_user):
        """Test updating a user profile with invalid fields."""
        # Create a PATCH request with invalid data
        update_data = {
            'username': 'hacker',  # Not allowed to be updated
            'is_staff': True,      # Not allowed to be updated
        }
        request = api_factory.patch('/api/profile/', update_data, format='json')
        request.user = mock_user
        request.data = update_data  # Manually add data since we're not using the full DRF stack
        
        # Get the response
        view = UserProfileView.as_view()
        response = view(request)
        
        # Assert response is correct
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'message' in response.data
        
        # Assert user was not updated
        assert mock_user.username != 'hacker'
        assert mock_user.is_staff is False
        assert not mock_user.save.called
    
    def test_update_profile_mixed(self, api_factory, mock_user):
        """Test updating a user profile with mixed valid and invalid fields."""
        # Create a PATCH request with mixed data
        update_data = {
            'first_name': 'Valid',
            'username': 'invalid',  # Not allowed to be updated
        }
        request = api_factory.patch('/api/profile/', update_data, format='json')
        request.user = mock_user
        request.data = update_data  # Manually add data since we're not using the full DRF stack
        
        # Get the response
        view = UserProfileView.as_view()
        response = view(request)
        
        # Assert response is correct
        assert response.status_code == status.HTTP_200_OK
        assert 'message' in response.data
        assert 'updated_fields' in response.data
        assert len(response.data['updated_fields']) == 1
        assert 'first_name' in response.data['updated_fields']
        
        # Assert only valid fields were updated
        assert mock_user.first_name == 'Valid'
        assert mock_user.username == 'testuser'  # Unchanged
        assert mock_user.save.called 