"""
Tests for service error handling in the inventory module.
This is a specialized test file that focuses on service errors
and bypasses authentication for faster, more reliable tests.
"""

import pytest
import json
from unittest.mock import patch, MagicMock
from rest_framework.test import APIRequestFactory
from rest_framework import status

from pyerp.business_modules.inventory.urls import (
    move_box, add_product_to_box,
)


@pytest.fixture
def api_factory():
    """Return a request factory for API tests."""
    return APIRequestFactory()


@pytest.fixture
def authenticated_request(api_factory):
    """Create a pre-authenticated request object to avoid authentication issues."""
    # Create a request with empty data - will be updated in tests
    request = api_factory.post('/test-url/', data={}, format='json')
    
    # Create a complete mock user that satisfies all Django auth checks
    mock_user = MagicMock()
    mock_user.id = 1
    mock_user.is_authenticated = True
    mock_user.is_active = True
    mock_user.is_anonymous = False
    mock_user.is_staff = True
    mock_user.__str__ = lambda self: "TestUser"
    
    # Set user directly on request
    request.user = mock_user
    
    return request


@pytest.mark.django_db
class TestInventoryServiceErrors:
    """Test class for inventory service error handling."""
    
    # Patch authentication and skip actual authentication checks
    @patch('rest_framework.request.Request._authenticate', return_value=None)
    @patch('pyerp.business_modules.inventory.urls.IsAuthenticated.has_permission', return_value=True)
    @patch('pyerp.business_modules.inventory.urls.Box.objects.get')
    @patch('pyerp.business_modules.inventory.urls.StorageLocation.objects.get')
    @patch('pyerp.business_modules.inventory.urls.InventoryService')
    def test_move_box_service_error(self, mock_service, mock_location_get, 
                                   mock_box_get, mock_auth, mock_authenticate, 
                                   api_factory):
        """Test that move_box correctly handles service exceptions."""
        # Create a request with the test data - create new request instead of modifying fixture
        request = api_factory.post(
            '/test-url/',
            data={'box_id': 1, 'target_location_id': 2},
            format='json'
        )
        
        # Set up user attributes
        mock_user = MagicMock()
        mock_user.id = 1
        mock_user.is_authenticated = True
        mock_user.is_active = True
        mock_user.is_anonymous = False
        request.user = mock_user
        
        # Mock database objects
        mock_box = MagicMock()
        mock_box.id = 1
        mock_box_get.return_value = mock_box
        
        mock_location = MagicMock()
        mock_location.id = 2
        mock_location_get.return_value = mock_location
        
        # Setup service error
        mock_service_instance = MagicMock()
        mock_service_instance.move_box.side_effect = Exception("Test service error")
        mock_service.return_value = mock_service_instance
        
        # Call the view with authentication patched
        with patch('rest_framework.request.Request._authenticate', return_value=None):
            response = move_box(request)
        
        # Complete the response rendering
        response.render()
        
        # Verify error response
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        content = json.loads(response.content)
        assert "Test service error" in content['detail']
    
    @patch('rest_framework.request.Request._authenticate', return_value=None)
    @patch('pyerp.business_modules.inventory.urls.IsAuthenticated.has_permission', return_value=True)
    @patch('pyerp.business_modules.inventory.urls.BoxSlot.objects.get')
    @patch('pyerp.business_modules.products.models.VariantProduct.objects.get')
    @patch('pyerp.business_modules.inventory.urls.InventoryService')
    def test_add_product_to_box_service_error(self, mock_service, mock_product_get, 
                                            mock_slot_get, mock_auth, mock_authenticate,
                                            api_factory):
        """Test that add_product_to_box correctly handles service exceptions."""
        # Create a request with the test data - create new request instead of modifying fixture
        request = api_factory.post(
            '/test-url/',
            data={
                'product_id': 1, 
                'box_slot_id': 2, 
                'quantity': 5
            },
            format='json'
        )
        
        # Set up user attributes
        mock_user = MagicMock()
        mock_user.id = 1
        mock_user.is_authenticated = True
        mock_user.is_active = True
        mock_user.is_anonymous = False
        request.user = mock_user
        
        # Mock database objects
        mock_product = MagicMock()
        mock_product.id = 1
        mock_product_get.return_value = mock_product
        
        mock_slot = MagicMock()
        mock_slot.id = 2
        mock_slot_get.return_value = mock_slot
        
        # Setup service error
        mock_service_instance = MagicMock()
        mock_service_instance.add_product_to_box_slot.side_effect = Exception("Test service error")
        mock_service.return_value = mock_service_instance
        
        # Call the view with authentication patched
        with patch('rest_framework.request.Request._authenticate', return_value=None):
            response = add_product_to_box(request)
        
        # Complete the response rendering
        response.render()
        
        # Verify error response
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        content = json.loads(response.content)
        assert "Test service error" in content['detail'] 