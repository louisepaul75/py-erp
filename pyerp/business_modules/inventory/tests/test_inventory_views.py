"""
Tests for inventory views error handling.
Tests the view functions with mocked services.
"""

import json
from unittest.mock import patch, MagicMock
from django.test import TestCase, RequestFactory
from rest_framework import status

from pyerp.business_modules.inventory.urls import (
    move_box, add_product_to_box,
)


class TestInventoryViewsErrorHandling(TestCase):
    """Test class for inventory views with proper error handling."""

    def setUp(self):
        """Set up test data and mocks."""
        self.factory = RequestFactory()
        
        # Create mock user
        self.user = MagicMock()
        self.user.id = 1
        self.user.is_authenticated = True
        self.user.is_active = True
        
        # Skip authentication for all tests
        self.auth_patcher = patch(
            'rest_framework.views.APIView.perform_authentication',
            return_value=None
        )
        self.auth_patcher.start()
        
        # Skip permission checking
        self.perm_patcher = patch(
            'rest_framework.permissions.IsAuthenticated.has_permission',
            return_value=True
        )
        self.perm_patcher.start()
        
        # Patch CSRF checking - RequestFactory doesn't handle CSRF
        self.csrf_patcher = patch(
            'django.middleware.csrf.CsrfViewMiddleware.process_view',
            return_value=None
        )
        self.csrf_patcher.start()
    
    def tearDown(self):
        """Clean up patches."""
        self.auth_patcher.stop()
        self.perm_patcher.stop()
        self.csrf_patcher.stop()
    
    def test_move_box_missing_parameters(self):
        """Test move_box view handles missing parameters correctly."""
        # Create request with missing parameters
        request = self.factory.post(
            '/api/move-box/',
            data={'target_location_id': 2},
            content_type='application/json'
        )
        request.user = self.user
        
        # Mark the request as CSRF exempt
        request._dont_enforce_csrf_checks = True
        
        # Call the view
        response = move_box(request)
        
        # Render the response so content is available
        response.render()
        
        # Check the response
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        data = json.loads(response.content)
        self.assertIn("Box ID and target location ID are required", data['detail'])
    
    @patch('pyerp.business_modules.inventory.urls.Box.objects.get')
    @patch('pyerp.business_modules.inventory.urls.StorageLocation.objects.get')
    @patch('pyerp.business_modules.inventory.urls.InventoryService')
    def test_move_box_service_error(
            self, mock_service, mock_location_get, mock_box_get):
        """Test move_box view handles service exceptions correctly."""
        # Create request with valid parameters
        request = self.factory.post(
            '/api/move-box/',
            data={'box_id': 1, 'target_location_id': 2},
            content_type='application/json'
        )
        request.user = self.user
        
        # Mark the request as CSRF exempt
        request._dont_enforce_csrf_checks = True
        
        # Set up mocks
        mock_box = MagicMock()
        mock_box.id = 1
        mock_box_get.return_value = mock_box
        
        mock_location = MagicMock()
        mock_location.id = 2
        mock_location_get.return_value = mock_location
        
        # Setup service to raise an exception
        mock_service_instance = MagicMock()
        error_message = "Box capacity exceeded in location"
        mock_service_instance.move_box.side_effect = ValueError(error_message)
        mock_service.return_value = mock_service_instance
        
        # Call the view
        response = move_box(request)
        
        # Render the response so content is available
        response.render()
        
        # Check the response
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        data = json.loads(response.content)
        self.assertIn(error_message, data['detail'])
    
    def test_add_product_to_box_missing_parameters(self):
        """Test add_product_to_box view handles missing parameters."""
        # Create request with missing parameters
        request = self.factory.post(
            '/api/add-product-to-box/',
            data={'product_id': 1, 'quantity': 5},
            content_type='application/json'
        )
        request.user = self.user
        
        # Mark the request as CSRF exempt
        request._dont_enforce_csrf_checks = True
        
        # Call the view
        response = add_product_to_box(request)
        
        # Render the response so content is available
        response.render()
        
        # Check the response
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        data = json.loads(response.content)
        self.assertIn(
            "Product ID, box slot ID, and quantity are required",
            data['detail']
        )
    
    @patch('pyerp.business_modules.inventory.urls.BoxSlot.objects.get')
    @patch('pyerp.business_modules.products.models.VariantProduct.objects.get')
    @patch('pyerp.business_modules.inventory.urls.InventoryService')
    def test_add_product_to_box_service_error(
            self, mock_service, mock_product_get, mock_slot_get):
        """Test add_product_to_box view handles service exceptions."""
        # Create request with valid parameters
        request = self.factory.post(
            '/api/add-product-to-box/',
            data=json.dumps({
                'product_id': 1,
                'box_slot_id': 2,
                'quantity': 5
            }),
            content_type='application/json'
        )
        request.user = self.user
        
        # Mark the request as CSRF exempt
        request._dont_enforce_csrf_checks = True
        
        # Set up mocks with minimal required attributes to avoid DB access
        mock_product = MagicMock(spec=['id', '__str__'])
        mock_product.id = 1
        mock_product.__str__.return_value = "Test Product"
        mock_product_get.return_value = mock_product
        
        mock_slot = MagicMock(spec=['id', 'box', 'slot_code'])
        mock_slot.id = 2
        mock_slot.slot_code = "SLOT001"
        mock_slot.box = MagicMock(spec=['code'])
        mock_slot.box.code = "BOX001"
        mock_slot_get.return_value = mock_slot
        
        # Create a standalone mock service rather than using the class
        error_message = "Slot capacity exceeded"
        mock_service_instance = MagicMock()
        mock_service_instance.add_product_to_box_slot.side_effect = (
            ValueError(error_message)
        )
        mock_service.return_value = mock_service_instance
        
        # Call the view
        response = add_product_to_box(request)
        
        # Verify mocks were called correctly
        mock_product_get.assert_called_once_with(id=1)
        mock_slot_get.assert_called_once_with(id=2)
        
        # Render the response so content is available
        response.render()
        
        # Check the response
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        data = json.loads(response.content)
        self.assertIn(error_message, data['detail']) 