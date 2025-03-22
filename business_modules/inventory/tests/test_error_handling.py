"""
Tests for error handling in the inventory module view functions.
This test file directly calls the view functions instead of using URL routing.
"""

import pytest
import json
from unittest.mock import patch, MagicMock
from django.http import HttpRequest
from rest_framework.test import APIRequestFactory
from rest_framework import status

from pyerp.business_modules.inventory.urls import (
    box_types_list, boxes_list, storage_locations_list,
    products_by_location, locations_by_product,
    move_box, add_product_to_box, 
    move_product_between_boxes, remove_product_from_box
)

from pyerp.business_modules.inventory.models import (
    BoxType, StorageLocation, Box, ProductStorage, 
    BoxStorage, BoxSlot
)


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
        
        # Check the response
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        content = json.loads(response.content)
        assert "Missing required parameters" in content['detail']

    @patch('pyerp.business_modules.inventory.urls.IsAuthenticated.has_permission', return_value=True)
    @patch('pyerp.business_modules.inventory.urls.InventoryService')
    def test_move_box_service_error(self, mock_service, mock_auth, api_factory):
        """Test the move_box view handles service exceptions."""
        # Mock service error
        mock_service_instance = MagicMock()
        mock_service_instance.move_box.side_effect = Exception("Service error")
        mock_service.return_value = mock_service_instance
        
        # Create a request with all required parameters
        request = api_factory.post('/dummy-url/', 
                                  data={
                                      "box_id": 1,
                                      "location_id": 2,
                                      "user_id": 1
                                  },
                                  format='json')
        
        # Call the view directly
        response = move_box(request)
        
        # Check the response
        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        content = json.loads(response.content)
        assert "Failed to move box" in content['detail']

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
        
        # Check the response
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        content = json.loads(response.content)
        assert "Missing required parameters" in content['detail']

    @patch('pyerp.business_modules.inventory.urls.IsAuthenticated.has_permission', return_value=True)
    @patch('pyerp.business_modules.inventory.urls.InventoryService')
    def test_add_product_to_box_service_error(self, mock_service, mock_auth, api_factory):
        """Test the add_product_to_box view handles service exceptions."""
        # Mock service error
        mock_service_instance = MagicMock()
        mock_service_instance.add_product_to_box_slot.side_effect = Exception("Service error")
        mock_service.return_value = mock_service_instance
        
        # Create a request with all required parameters
        request = api_factory.post('/dummy-url/', 
                                  data={
                                      "box_id": 1,
                                      "slot_id": 2,
                                      "product_id": 3,
                                      "quantity": 5
                                  },
                                  format='json')
        
        # Call the view directly
        response = add_product_to_box(request)
        
        # Check the response
        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        content = json.loads(response.content)
        assert "Failed to add product to box" in content['detail']

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
        
        # Check the response
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        content = json.loads(response.content)
        assert "Missing required parameters" in content['detail']

    @patch('pyerp.business_modules.inventory.urls.IsAuthenticated.has_permission', return_value=True)
    @patch('pyerp.business_modules.inventory.urls.InventoryService')
    def test_move_product_between_boxes_service_error(self, mock_service, mock_auth, api_factory):
        """Test the move_product_between_boxes view handles service exceptions."""
        # Mock service error
        mock_service_instance = MagicMock()
        mock_service_instance.move_product_between_box_slots.side_effect = Exception("Service error")
        mock_service.return_value = mock_service_instance
        
        # Create a request with all required parameters
        request = api_factory.post('/dummy-url/', 
                                  data={
                                      "source_box_id": 1,
                                      "source_slot_id": 2,
                                      "target_box_id": 3,
                                      "target_slot_id": 4,
                                      "product_id": 5,
                                      "quantity": 6
                                  },
                                  format='json')
        
        # Call the view directly
        response = move_product_between_boxes(request)
        
        # Check the response
        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        content = json.loads(response.content)
        assert "Failed to move product between boxes" in content['detail']

    @patch('pyerp.business_modules.inventory.urls.IsAuthenticated.has_permission', return_value=True)
    @patch('pyerp.business_modules.inventory.urls.InventoryService')
    def test_remove_product_from_box_missing_parameters(self, mock_service, mock_auth, api_factory):
        """Test the remove_product_from_box view validates required parameters."""
        # Create a request with missing product_id
        request = api_factory.post('/dummy-url/', 
                                  data={
                                      "box_id": 1,
                                      "slot_id": 2,
                                      "quantity": 3
                                  },
                                  format='json')
        
        # Call the view directly
        response = remove_product_from_box(request)
        
        # Check the response
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        content = json.loads(response.content)
        assert "Missing required parameters" in content['detail']

    @patch('pyerp.business_modules.inventory.urls.IsAuthenticated.has_permission', return_value=True)
    @patch('pyerp.business_modules.inventory.urls.InventoryService')
    def test_remove_product_from_box_service_error(self, mock_service, mock_auth, api_factory):
        """Test the remove_product_from_box view handles service exceptions."""
        # Mock service error
        mock_service_instance = MagicMock()
        mock_service_instance.remove_product_from_box_slot.side_effect = Exception("Service error")
        mock_service.return_value = mock_service_instance
        
        # Create a request with all required parameters
        request = api_factory.post('/dummy-url/', 
                                  data={
                                      "box_id": 1,
                                      "slot_id": 2,
                                      "product_id": 3,
                                      "quantity": 4
                                  },
                                  format='json')
        
        # Call the view directly
        response = remove_product_from_box(request)
        
        # Check the response
        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        content = json.loads(response.content)
        assert "Failed to remove product from box" in content['detail'] 