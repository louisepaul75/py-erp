"""
Tests for error handling in the inventory module view functions.
"""

import pytest
import json
from unittest.mock import patch, MagicMock
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status

from pyerp.business_modules.inventory.models import (
    BoxType, StorageLocation, Box, ProductStorage, 
    BoxStorage, BoxSlot
)


@pytest.fixture
def api_client():
    """Return an authenticated API client."""
    client = APIClient()
    # Mock authentication
    return client


@pytest.mark.django_db
class TestInventoryErrorHandling:
    """Test class for inventory error handling."""

    @patch('pyerp.business_modules.inventory.urls.BoxType.objects.all')
    def test_box_types_list_error(self, mock_box_types, api_client, inventory_urls):
        """Test the box_types_list view handles exceptions properly."""
        # Mock an exception
        mock_box_types.side_effect = Exception("Database error")
        
        url = reverse('inventory:box_types_list')
        with patch('pyerp.business_modules.inventory.urls.IsAuthenticated.has_permission', return_value=True):
            response = api_client.get(url)
            
        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        content = json.loads(response.content)
        assert "Failed to fetch box types" in content['detail']

    @patch('pyerp.business_modules.inventory.urls.Box.objects.select_related')
    def test_boxes_list_error(self, mock_select_related, api_client, inventory_urls):
        """Test the boxes_list view handles exceptions properly."""
        # Mock an exception
        mock_select_related.side_effect = Exception("Database error")
        
        url = reverse('inventory:boxes_list')
        with patch('pyerp.business_modules.inventory.urls.IsAuthenticated.has_permission', return_value=True):
            response = api_client.get(url)
            
        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        content = json.loads(response.content)
        assert "Failed to fetch boxes" in content['detail']

    @patch('pyerp.business_modules.inventory.urls.StorageLocation.objects.annotate')
    def test_storage_locations_list_error(self, mock_annotate, api_client, inventory_urls):
        """Test the storage_locations_list view handles exceptions properly."""
        # Mock an exception
        mock_annotate.side_effect = Exception("Database error")
        
        url = reverse('inventory:storage_locations_list')
        with patch('pyerp.business_modules.inventory.urls.IsAuthenticated.has_permission', return_value=True):
            response = api_client.get(url)
            
        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        content = json.loads(response.content)
        assert "Failed to fetch storage locations" in content['detail']

    def test_products_by_location_missing_id(self, api_client, inventory_urls):
        """Test the products_by_location view validates location_id."""
        # Call without location_id
        url = reverse('inventory:products_by_location')
        with patch('pyerp.business_modules.inventory.urls.IsAuthenticated.has_permission', return_value=True):
            response = api_client.get(url)
            
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        content = json.loads(response.content)
        assert "Storage location ID is required" in content['detail']

    @patch('pyerp.business_modules.inventory.urls.ProductStorage.objects.filter')
    def test_products_by_location_error(self, mock_filter, api_client, inventory_urls):
        """Test the products_by_location view handles exceptions properly."""
        # Mock an exception
        mock_filter.side_effect = Exception("Database error")
        
        url = reverse('inventory:products_by_location', args=[1])
        with patch('pyerp.business_modules.inventory.urls.IsAuthenticated.has_permission', return_value=True):
            response = api_client.get(url)
            
        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        content = json.loads(response.content)
        assert "Failed to fetch products by location" in content['detail']

    def test_locations_by_product_missing_id(self, api_client, inventory_urls):
        """Test the locations_by_product view validates product_id."""
        # Call without product_id
        url = reverse('inventory:locations_by_product')
        with patch('pyerp.business_modules.inventory.urls.IsAuthenticated.has_permission', return_value=True):
            response = api_client.get(url)
            
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        content = json.loads(response.content)
        assert "Product ID is required" in content['detail']

    @patch('pyerp.business_modules.inventory.urls.ProductStorage.objects.filter')
    def test_locations_by_product_error(self, mock_filter, api_client, inventory_urls):
        """Test the locations_by_product view handles exceptions properly."""
        # Mock an exception
        mock_filter.side_effect = Exception("Database error")
        
        url = reverse('inventory:locations_by_product', args=[1])
        with patch('pyerp.business_modules.inventory.urls.IsAuthenticated.has_permission', return_value=True):
            response = api_client.get(url)
            
        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        content = json.loads(response.content)
        assert "Failed to fetch locations by product" in content['detail']

    @patch('pyerp.business_modules.inventory.urls.InventoryService')
    def test_move_box_missing_parameters(self, mock_service, api_client, inventory_urls):
        """Test the move_box view validates required parameters."""
        # Missing box_id
        test_data = {
            "location_id": 2,
            "user_id": 1
        }
        
        url = reverse('inventory:move_box')
        with patch('pyerp.business_modules.inventory.urls.IsAuthenticated.has_permission', return_value=True):
            response = api_client.post(url, test_data, format='json')
            
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        content = json.loads(response.content)
        assert "Missing required parameters" in content['detail']

    @patch('pyerp.business_modules.inventory.urls.InventoryService')
    def test_move_box_service_error(self, mock_service, api_client, inventory_urls):
        """Test the move_box view handles service exceptions."""
        # Mock service error
        mock_service_instance = MagicMock()
        mock_service_instance.move_box.side_effect = Exception("Service error")
        mock_service.return_value = mock_service_instance
        
        test_data = {
            "box_id": 1,
            "location_id": 2,
            "user_id": 1
        }
        
        url = reverse('inventory:move_box')
        with patch('pyerp.business_modules.inventory.urls.IsAuthenticated.has_permission', return_value=True):
            response = api_client.post(url, test_data, format='json')
            
        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        content = json.loads(response.content)
        assert "Failed to move box" in content['detail']

    @patch('pyerp.business_modules.inventory.urls.InventoryService')
    def test_add_product_to_box_missing_parameters(self, mock_service, api_client, inventory_urls):
        """Test the add_product_to_box view validates required parameters."""
        # Missing product_id
        test_data = {
            "box_id": 1,
            "slot_id": 2,
            "quantity": 5
        }
        
        url = reverse('inventory:add_product_to_box')
        with patch('pyerp.business_modules.inventory.urls.IsAuthenticated.has_permission', return_value=True):
            response = api_client.post(url, test_data, format='json')
            
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        content = json.loads(response.content)
        assert "Missing required parameters" in content['detail']

    @patch('pyerp.business_modules.inventory.urls.InventoryService')
    def test_add_product_to_box_service_error(self, mock_service, api_client, inventory_urls):
        """Test the add_product_to_box view handles service exceptions."""
        # Mock service error
        mock_service_instance = MagicMock()
        mock_service_instance.add_product_to_box_slot.side_effect = Exception("Service error")
        mock_service.return_value = mock_service_instance
        
        test_data = {
            "box_id": 1,
            "slot_id": 2,
            "product_id": 3,
            "quantity": 5
        }
        
        url = reverse('inventory:add_product_to_box')
        with patch('pyerp.business_modules.inventory.urls.IsAuthenticated.has_permission', return_value=True):
            response = api_client.post(url, test_data, format='json')
            
        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        content = json.loads(response.content)
        assert "Failed to add product to box" in content['detail']

    @patch('pyerp.business_modules.inventory.urls.InventoryService')
    def test_move_product_between_boxes_missing_parameters(self, mock_service, api_client, inventory_urls):
        """Test the move_product_between_boxes view validates required parameters."""
        # Missing target_slot_id
        test_data = {
            "source_box_id": 1,
            "source_slot_id": 2,
            "target_box_id": 3,
            "product_id": 5,
            "quantity": 6
        }
        
        url = reverse('inventory:move_product_between_boxes')
        with patch('pyerp.business_modules.inventory.urls.IsAuthenticated.has_permission', return_value=True):
            response = api_client.post(url, test_data, format='json')
            
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        content = json.loads(response.content)
        assert "Missing required parameters" in content['detail']

    @patch('pyerp.business_modules.inventory.urls.InventoryService')
    def test_move_product_between_boxes_service_error(self, mock_service, api_client, inventory_urls):
        """Test the move_product_between_boxes view handles service exceptions."""
        # Mock service error
        mock_service_instance = MagicMock()
        mock_service_instance.move_product_between_box_slots.side_effect = Exception("Service error")
        mock_service.return_value = mock_service_instance
        
        test_data = {
            "source_box_id": 1,
            "source_slot_id": 2,
            "target_box_id": 3,
            "target_slot_id": 4,
            "product_id": 5,
            "quantity": 6
        }
        
        url = reverse('inventory:move_product_between_boxes')
        with patch('pyerp.business_modules.inventory.urls.IsAuthenticated.has_permission', return_value=True):
            response = api_client.post(url, test_data, format='json')
            
        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        content = json.loads(response.content)
        assert "Failed to move product between boxes" in content['detail']

    @patch('pyerp.business_modules.inventory.urls.InventoryService')
    def test_remove_product_from_box_missing_parameters(self, mock_service, api_client, inventory_urls):
        """Test the remove_product_from_box view validates required parameters."""
        # Missing product_id
        test_data = {
            "box_id": 1,
            "slot_id": 2,
            "quantity": 4
        }
        
        url = reverse('inventory:remove_product_from_box')
        with patch('pyerp.business_modules.inventory.urls.IsAuthenticated.has_permission', return_value=True):
            response = api_client.post(url, test_data, format='json')
            
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        content = json.loads(response.content)
        assert "Missing required parameters" in content['detail']

    @patch('pyerp.business_modules.inventory.urls.InventoryService')
    def test_remove_product_from_box_service_error(self, mock_service, api_client, inventory_urls):
        """Test the remove_product_from_box view handles service exceptions."""
        # Mock service error
        mock_service_instance = MagicMock()
        mock_service_instance.remove_product_from_box_slot.side_effect = Exception("Service error")
        mock_service.return_value = mock_service_instance
        
        test_data = {
            "box_id": 1,
            "slot_id": 2,
            "product_id": 3,
            "quantity": 4
        }
        
        url = reverse('inventory:remove_product_from_box')
        with patch('pyerp.business_modules.inventory.urls.IsAuthenticated.has_permission', return_value=True):
            response = api_client.post(url, test_data, format='json')
            
        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        content = json.loads(response.content)
        assert "Failed to remove product from box" in content['detail'] 