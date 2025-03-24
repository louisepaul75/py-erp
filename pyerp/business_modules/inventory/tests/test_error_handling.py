"""
Tests for error handling in the inventory module view functions.
This test file directly calls the view functions instead of using URL routing.
"""

import pytest
import json
from unittest.mock import patch, MagicMock
from rest_framework.test import APIRequestFactory
from rest_framework import status

from pyerp.business_modules.inventory.urls import (
    box_types_list, boxes_list, storage_locations_list,
    products_by_location, locations_by_product,
    move_box, add_product_to_box, 
    move_product_between_boxes, remove_product_from_box
)

# Models are imported for reference but not directly used in tests
# They are patched in the test functions


@pytest.fixture
def api_factory():
    """Return a request factory for API tests."""
    return APIRequestFactory()


@pytest.mark.django_db
class TestInventoryErrorHandlingDirect:
    """Test class for inventory error handling by directly calling view functions."""

    @patch('pyerp.business_modules.inventory.urls.IsAuthenticated.has_permission', return_value=True)
    @patch('pyerp.business_modules.inventory.urls.BoxType.objects.all')
    def test_box_types_list_error(self, mock_box_types, mock_auth, api_factory):
        """Test the box_types_list view handles exceptions properly."""
        # Mock an exception
        mock_box_types.side_effect = Exception("Database error")
        
        # Create a request
        request = api_factory.get('/dummy-url/')
        
        # Call the view directly
        response = box_types_list(request)
        
        # Make sure to render the response before accessing content
        response.render()
        
        # Check the response
        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        content = json.loads(response.content)
        assert "Failed to fetch box types" in content['detail']

    @patch('pyerp.business_modules.inventory.urls.IsAuthenticated.has_permission', return_value=True)
    @patch('pyerp.business_modules.inventory.urls.Box.objects.select_related')
    def test_boxes_list_error(self, mock_select_related, mock_auth, api_factory):
        """Test the boxes_list view handles exceptions properly."""
        # Mock an exception
        mock_select_related.side_effect = Exception("Database error")
        
        # Create a request
        request = api_factory.get('/dummy-url/')
        
        # Call the view directly
        response = boxes_list(request)
        
        # Make sure to render the response before accessing content
        response.render()
        
        # Check the response
        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        content = json.loads(response.content)
        assert "Failed to fetch boxes" in content['detail']

    @patch('pyerp.business_modules.inventory.urls.IsAuthenticated.has_permission', return_value=True)
    @patch('pyerp.business_modules.inventory.urls.StorageLocation.objects.annotate')
    def test_storage_locations_list_error(self, mock_annotate, mock_auth, api_factory):
        """Test the storage_locations_list view handles exceptions properly."""
        # Mock an exception
        mock_annotate.side_effect = Exception("Database error")
        
        # Create a request
        request = api_factory.get('/dummy-url/')
        
        # Call the view directly
        response = storage_locations_list(request)
        
        # Make sure to render the response before accessing content
        response.render()
        
        # Check the response
        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        content = json.loads(response.content)
        assert "Failed to fetch storage locations" in content['detail']

    @patch('pyerp.business_modules.inventory.urls.IsAuthenticated.has_permission', return_value=True)
    def test_products_by_location_missing_id(self, mock_auth, api_factory):
        """Test the products_by_location view validates location_id."""
        # Create a request
        request = api_factory.get('/dummy-url/')
        
        # Call the view directly with no location_id
        response = products_by_location(request)
        
        # Make sure to render the response before accessing content
        response.render()
        
        # The view should handle the missing ID and return a 400 error
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        content = json.loads(response.content)
        assert "Storage location ID is required" in content['detail']

    @patch('pyerp.business_modules.inventory.urls.IsAuthenticated.has_permission', return_value=True)
    @patch('pyerp.business_modules.inventory.urls.ProductStorage.objects.filter')
    def test_products_by_location_error(self, mock_filter, mock_auth, api_factory):
        """Test the products_by_location view handles exceptions properly."""
        # Mock an exception
        mock_filter.side_effect = Exception("Database error")
        
        # Create a request
        request = api_factory.get('/dummy-url/')
        
        # Call the view directly with a location_id
        response = products_by_location(request, location_id=1)
        
        # Make sure to render the response before accessing content
        response.render()
        
        # Check the response
        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        content = json.loads(response.content)
        assert "Failed to fetch products by location" in content['detail']

    @patch('pyerp.business_modules.inventory.urls.IsAuthenticated.has_permission', return_value=True)
    def test_locations_by_product_missing_id(self, mock_auth, api_factory):
        """Test the locations_by_product view validates product_id."""
        # Create a request
        request = api_factory.get('/dummy-url/')
        
        # Call the view directly with no product_id
        response = locations_by_product(request)
        
        # Make sure to render the response before accessing content
        response.render()
        
        # The view should handle the missing ID and return a 400 error
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        content = json.loads(response.content)
        assert "Product ID is required" in content['detail']

    @patch('pyerp.business_modules.inventory.urls.IsAuthenticated.has_permission', return_value=True)
    @patch('pyerp.business_modules.inventory.urls.ProductStorage.objects.filter')
    def test_locations_by_product_error(self, mock_filter, mock_auth, api_factory):
        """Test the locations_by_product view handles exceptions properly."""
        # Mock an exception
        mock_filter.side_effect = Exception("Database error")
        
        # Create a request
        request = api_factory.get('/dummy-url/')
        
        # Call the view directly with a product_id
        response = locations_by_product(request, product_id=1)
        
        # Make sure to render the response before accessing content
        response.render()
        
        # Check the response
        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        content = json.loads(response.content)
        assert "Failed to fetch locations by product" in content['detail']

    @patch('pyerp.business_modules.inventory.urls.IsAuthenticated.has_permission', return_value=True)
    @patch('pyerp.business_modules.inventory.urls.InventoryService')
    def test_move_box_missing_parameters(self, mock_service, mock_auth, api_factory):
        """Test the move_box view validates required parameters."""
        # Create a request with missing box_id
        request = api_factory.post('/dummy-url/', 
                                  data={
                                      "location_id": 2,
                                      "user_id": 1
                                  },
                                  format='json')
        
        # Call the view directly
        response = move_box(request)
        
        # Make sure to render the response before accessing content
        response.render()
        
        # Check the response
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        content = json.loads(response.content)
        assert "Box ID and target location ID are required" in content['detail']

    @patch('pyerp.business_modules.inventory.urls.IsAuthenticated.has_permission', return_value=True)
    @patch('pyerp.business_modules.inventory.urls.Box.objects')
    @patch('pyerp.business_modules.inventory.urls.StorageLocation.objects')
    @patch('pyerp.business_modules.inventory.urls.InventoryService', autospec=True)
    def test_move_box_service_error(self, 
                                    mock_service_class, 
                                    mock_storage_location_objects,
                                    mock_box_objects,
                                    mock_auth,
                                    api_factory):
        """Test the move_box view handles service exceptions."""
        # 1. Setup service exception
        mock_service = mock_service_class.return_value
        mock_service.move_box.side_effect = Exception("Service error")
        
        # 2. Setup mock objects that avoid implicit DB lookups
        mock_box = MagicMock(spec=['id', 'code'])
        mock_box.id = 1
        mock_box.code = 'BOX001'
        
        mock_location = MagicMock(spec=['id', 'name'])
        mock_location.id = 2
        mock_location.name = 'Test Location'
        
        # These return a MagicMock that simulates a DB model
        mock_box_objects.get.return_value = mock_box
        mock_storage_location_objects.get.return_value = mock_location
        
        # 3. Create a request with the minimal required data
        request = api_factory.post(
            '/fake-url/',
            data={'box_id': 1, 'target_location_id': 2},
            format='json'
        )
        
        # 4. Setup complete user mock with all required Django User attributes
        mock_user = MagicMock()
        mock_user.id = 1
        mock_user.is_authenticated = True
        mock_user.is_active = True
        mock_user.is_anonymous = False
        mock_user.__str__ = lambda self: "TestUser"
        
        # Important: Patch request.user property to avoid DRF authentication
        request.user = mock_user
        
        # 5. Skip authentication to avoid Django auth system
        with patch('rest_framework.request.Request._authenticate', return_value=None):
            # Directly test the function under test
            response = move_box(request)
        
        # 6. Complete the response rendering
        response.render()
        
        # 7. Verify the response has the expected error
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        content = json.loads(response.content)
        assert "Service error" in content['detail']
        
        # 8. Verify the mocks were called correctly
        mock_box_objects.get.assert_called_once_with(id=1)
        mock_storage_location_objects.get.assert_called_once_with(id=2)
        mock_service.move_box.assert_called_once()

    @patch('pyerp.business_modules.inventory.urls.IsAuthenticated.has_permission', return_value=True)
    @patch('pyerp.business_modules.inventory.urls.InventoryService')
    def test_add_product_to_box_missing_parameters(self, mock_service, mock_auth, api_factory):
        """Test the add_product_to_box view validates required parameters."""
        # Create a request with missing product_id
        request = api_factory.post('/dummy-url/', 
                                  data={
                                      "box_id": 1,
                                      "slot_id": 2,
                                      "quantity": 5
                                  },
                                  format='json')
        
        # Call the view directly
        response = add_product_to_box(request)
        
        # Make sure to render the response before accessing content
        response.render()
        
        # Check the response - match actual error message
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        content = json.loads(response.content)
        assert "Product ID, box slot ID, and quantity are required" in content['detail']

    @patch('pyerp.business_modules.inventory.urls.IsAuthenticated.has_permission', return_value=True)
    @patch('pyerp.business_modules.inventory.urls.InventoryService')
    @patch('pyerp.business_modules.inventory.urls.BoxSlot.objects.get')
    @patch('pyerp.business_modules.inventory.urls.VariantProduct.objects.get', create=True)
    def test_add_product_to_box_service_error(self, mock_product_get, mock_box_slot_get, 
                                             mock_service, mock_auth, api_factory):
        """Test the add_product_to_box view handles service exceptions."""
        # Create minimal mock objects with only required attributes
        mock_product = MagicMock(id=3)
        mock_box_slot = MagicMock(id=2)
        mock_product_get.return_value = mock_product
        mock_box_slot_get.return_value = mock_box_slot
        
        # Mock service with specific exception
        mock_service_instance = MagicMock()
        mock_service_instance.add_product_to_box_slot.side_effect = Exception("Service error")
        mock_service.return_value = mock_service_instance
        
        # Create a simple request with required parameters
        request = api_factory.post(
            '/dummy-url/', 
            data={
                "product_id": 3,
                "box_slot_id": 2,
                "quantity": 5
            },
            format='json'
        )
        
        # Set user attribute on request to avoid potential lookups
        request.user = MagicMock()
        
        # Call the view directly
        response = add_product_to_box(request)
        
        # Make sure to render the response before accessing content
        response.render()
        
        # In the urls.py, service errors are caught and returned with status 400
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        content = json.loads(response.content)
        assert "Service error" in content['detail']

    @patch('pyerp.business_modules.inventory.urls.IsAuthenticated.has_permission', return_value=True)
    @patch('pyerp.business_modules.inventory.urls.InventoryService')
    def test_move_product_between_boxes_missing_parameters(self, mock_service, mock_auth, api_factory):
        """Test the move_product_between_boxes view validates required parameters."""
        # Create a request with missing target_slot_id
        request = api_factory.post('/dummy-url/', 
                                  data={
                                      "source_box_id": 1,
                                      "source_slot_id": 2,
                                      "target_box_id": 3,
                                      "product_id": 5,
                                      "quantity": 6
                                  },
                                  format='json')
        
        # Call the view directly
        response = move_product_between_boxes(request)
        
        # Make sure to render the response before accessing content
        response.render()
        
        # Check the response - match actual error message
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        content = json.loads(response.content)
        assert "Source box storage ID, target box slot ID, and quantity are required" in content['detail']

    @patch('pyerp.business_modules.inventory.urls.IsAuthenticated.has_permission', return_value=True)
    @patch('pyerp.business_modules.inventory.urls.InventoryService')
    @patch('pyerp.business_modules.inventory.urls.BoxStorage.objects.get')
    @patch('pyerp.business_modules.inventory.urls.BoxSlot.objects.get')
    def test_move_product_between_boxes_service_error(self, mock_box_slot_get, mock_box_storage_get,
                                                    mock_service, mock_auth, api_factory):
        """Test the move_product_between_boxes view handles service exceptions."""
        # Create minimal mock objects with only required attributes
        mock_box_storage = MagicMock(id=1)
        mock_box_slot = MagicMock(id=4)
        mock_box_storage_get.return_value = mock_box_storage
        mock_box_slot_get.return_value = mock_box_slot
        
        # Mock service with specific exception
        mock_service_instance = MagicMock()
        mock_service_instance.move_product_between_box_slots.side_effect = Exception("Service error")
        mock_service.return_value = mock_service_instance
        
        # Create a simple request with required parameters
        request = api_factory.post(
            '/dummy-url/', 
            data={
                "source_box_storage_id": 1,
                "target_box_slot_id": 4,
                "quantity": 6
            },
            format='json'
        )
        
        # Set user attribute on request to avoid potential lookups
        request.user = MagicMock()
        
        # Call the view directly
        response = move_product_between_boxes(request)
        
        # Make sure to render the response before accessing content
        response.render()
        
        # In the urls.py, service errors are caught and returned with status 400
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        content = json.loads(response.content)
        assert "Service error" in content['detail']

    @patch('pyerp.business_modules.inventory.urls.IsAuthenticated.has_permission', return_value=True)
    @patch('pyerp.business_modules.inventory.urls.InventoryService')
    def test_remove_product_from_box_missing_parameters(self, mock_service, mock_auth, api_factory):
        """Test the remove_product_from_box view validates required parameters."""
        # Create a request with missing product_id
        request = api_factory.post('/dummy-url/', 
                                  data={
                                      "box_id": 1,
                                      "slot_id": 2
                                  },
                                  format='json')
        
        # Call the view directly
        response = remove_product_from_box(request)
        
        # Make sure to render the response before accessing content
        response.render()
        
        # Check the response - match actual error message
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        content = json.loads(response.content)
        assert "Box storage ID and quantity are required" in content['detail']

    @patch('pyerp.business_modules.inventory.urls.IsAuthenticated.has_permission', return_value=True)
    @patch('pyerp.business_modules.inventory.urls.InventoryService')
    @patch('pyerp.business_modules.inventory.urls.BoxStorage.objects.get')
    def test_remove_product_from_box_service_error(self, mock_box_storage_get, 
                                                 mock_service, mock_auth, api_factory):
        """Test the remove_product_from_box view handles service exceptions."""
        # Create minimal mock objects with only required attributes
        mock_box_storage = MagicMock(id=1)
        mock_box_storage_get.return_value = mock_box_storage
        
        # Mock service with specific exception
        mock_service_instance = MagicMock()
        mock_service_instance.remove_product_from_box_slot.side_effect = Exception("Service error")
        mock_service.return_value = mock_service_instance
        
        # Create a simple request with required parameters
        request = api_factory.post(
            '/dummy-url/', 
            data={
                "box_storage_id": 1,
                "quantity": 4
            },
            format='json'
        )
        
        # Set user attribute on request to avoid potential lookups
        request.user = MagicMock()
        
        # Call the view directly
        response = remove_product_from_box(request)
        
        # Make sure to render the response before accessing content
        response.render()
        
        # In the urls.py, service errors are caught and returned with status 400
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        content = json.loads(response.content)
        assert "Service error" in content['detail'] 