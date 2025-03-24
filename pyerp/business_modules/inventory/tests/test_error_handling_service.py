"""
Tests for service error handling in the inventory module.
This is a specialized test file that focuses on service errors
and bypasses authentication for faster, more reliable tests.
"""

import pytest
import json
import logging
from unittest.mock import patch, MagicMock
from rest_framework.test import APIRequestFactory
from rest_framework import status

# Set up logger
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)

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
        try:
            logger.debug("Starting test_move_box_service_error test")
            
            # Create a request with the test data - create new request instead of modifying fixture
            logger.debug("Creating API request")
            request = api_factory.post(
                '/api/inventory/move-box/',
                data={'box_id': 1, 'target_location_id': 2},
                format='json'
            )
            logger.debug(f"Created request with path: {request.path}")
            
            # Set up user attributes
            logger.debug("Setting up mock user")
            mock_user = MagicMock()
            mock_user.id = 1
            mock_user.is_authenticated = True
            mock_user.is_active = True
            mock_user.is_anonymous = False
            mock_user.username = "testuser"  # Add username attribute for logging
            request.user = mock_user
            logger.debug("Mock user attached to request")
            
            # Mock database objects
            logger.debug("Setting up mock box")
            mock_box = MagicMock()
            mock_box.id = 1
            mock_box_get.return_value = mock_box
            logger.debug("Mock box setup complete")
            
            logger.debug("Setting up mock location")
            mock_location = MagicMock()
            mock_location.id = 2
            mock_location_get.return_value = mock_location
            logger.debug("Mock location setup complete")
            
            # Setup service error
            logger.debug("Setting up mock service with error")
            mock_service_instance = MagicMock()
            mock_service_instance.move_box.side_effect = Exception("Test service error")
            # Fix the mocking approach - in most Django cases, the service is called directly
            # not through an instance
            mock_service.move_box.side_effect = Exception("Test service error")
            logger.debug(f"Mock service setup complete with: {mock_service}")
            
            # Log the request data for debugging
            logger.debug(f"Request method: {request.method}")
            logger.debug(f"Request body: {request.body}")
            logger.debug(f"Request POST data: {request.POST}")
            logger.debug(f"Request content type: {request.content_type}")
            logger.debug(f"Request path: {request.path}")
            
            # Call the view with authentication patched
            logger.debug("Calling move_box view function")
            with patch('rest_framework.request.Request._authenticate', return_value=None):
                response = move_box(request)
            logger.debug("move_box view function returned")
            
            # Complete the response rendering
            logger.debug("Rendering response")
            response.render()
            logger.debug(f"Response rendered with status code: {response.status_code}")
            
            # Verify error response
            content = json.loads(response.content)
            logger.debug(f"Response content: {content}")
            assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
            assert "Test service error" in content.get('details', '')
            logger.debug("Assertions passed, test complete")
        except Exception as e:
            logger.error(f"Test failed with exception: {str(e)}", exc_info=True)
            raise
    
    @patch('rest_framework.request.Request._authenticate', return_value=None)
    @patch('pyerp.business_modules.inventory.urls.IsAuthenticated.has_permission', return_value=True)
    @patch('pyerp.business_modules.inventory.urls.BoxSlot.objects.get')
    @patch('pyerp.business_modules.products.models.VariantProduct.objects.get')
    @patch('pyerp.business_modules.inventory.urls.InventoryService')
    def test_add_product_to_box_service_error(self, mock_service, mock_product_get, 
                                            mock_slot_get, mock_auth, mock_authenticate,
                                            api_factory):
        """Test that add_product_to_box correctly handles service exceptions."""
        try:
            logger.debug("Starting test_add_product_to_box_service_error test")
            
            # Create a request with the test data - create new request instead of modifying fixture
            logger.debug("Creating API request")
            request = api_factory.post(
                '/api/inventory/add-product-to-box/',
                data={
                    'product_id': 1, 
                    'box_slot_id': 2, 
                    'quantity': 5
                },
                format='json'
            )
            logger.debug(f"Created request with path: {request.path}")
            
            # Set up user attributes
            logger.debug("Setting up mock user")
            mock_user = MagicMock()
            mock_user.id = 1
            mock_user.is_authenticated = True
            mock_user.is_active = True
            mock_user.is_anonymous = False
            mock_user.username = "testuser"  # Add username attribute for logging
            request.user = mock_user
            logger.debug("Mock user attached to request")
            
            # Mock database objects
            logger.debug("Setting up mock product")
            mock_product = MagicMock()
            mock_product.id = 1
            mock_product_get.return_value = mock_product
            logger.debug("Mock product setup complete")
            
            logger.debug("Setting up mock slot")
            mock_slot = MagicMock()
            mock_slot.id = 2
            mock_slot_get.return_value = mock_slot
            logger.debug("Mock slot setup complete")
            
            # Setup service error
            logger.debug("Setting up mock service with error")
            mock_service_instance = MagicMock()
            mock_service_instance.add_product_to_box_slot.side_effect = Exception("Test service error")
            # Fix the mocking approach - in most Django cases, the service is called directly
            # not through an instance
            mock_service.add_product_to_box_slot.side_effect = Exception("Test service error")
            logger.debug(f"Mock service setup complete with: {mock_service}")
            
            # Log the request data for debugging
            logger.debug(f"Request method: {request.method}")
            logger.debug(f"Request body: {request.body}")
            logger.debug(f"Request POST data: {request.POST}")
            logger.debug(f"Request content type: {request.content_type}")
            logger.debug(f"Request path: {request.path}")
            
            # Call the view with authentication patched
            logger.debug("Calling add_product_to_box view function")
            with patch('rest_framework.request.Request._authenticate', return_value=None):
                response = add_product_to_box(request)
            logger.debug("add_product_to_box view function returned")
            
            # Complete the response rendering
            logger.debug("Rendering response")
            response.render()
            logger.debug(f"Response rendered with status code: {response.status_code}")
            
            # Verify error response
            content = json.loads(response.content)
            logger.debug(f"Response content: {content}")
            assert response.status_code == status.HTTP_400_BAD_REQUEST
            assert "Test service error" in content.get('message', '')
            logger.debug("Assertions passed, test complete")
        except Exception as e:
            logger.error(f"Test failed with exception: {str(e)}", exc_info=True)
            raise 