"""
Tests for inventory views error handling.
Tests the view functions with mocked services.
"""

import json
import logging
from unittest.mock import patch, MagicMock, Mock
from django.test import TestCase, RequestFactory, override_settings
from rest_framework import status
from django.urls import reverse
from rest_framework.test import APIRequestFactory
from django.contrib.auth.models import User

from pyerp.business_modules.inventory.urls import (
    move_box, add_product_to_box,
)
from pyerp.business_modules.inventory.models import BoxSlot
from pyerp.business_modules.products.models import VariantProduct

# Configure logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
))
logger.addHandler(handler)

class TestInventoryViewsErrorHandling(TestCase):
    """Test class for inventory views with proper error handling."""

    def setUp(self):
        """Set up test data and mocks."""
        logger.info("Setting up test environment")
        self.factory = RequestFactory()
        self.api_factory = APIRequestFactory()
        
        # Create mock user
        self.user = MagicMock()
        self.user.id = 1
        self.user.is_authenticated = True
        self.user.is_active = True
        
        # Skip authentication for all tests
        logger.debug("Setting up authentication patch")
        self.auth_patcher = patch(
            'rest_framework.views.APIView.perform_authentication',
            return_value=None
        )
        self.auth_mock = self.auth_patcher.start()
        
        # Skip permission checking
        logger.debug("Setting up permission patch")
        self.perm_patcher = patch(
            'rest_framework.permissions.IsAuthenticated.has_permission',
            return_value=True
        )
        self.perm_mock = self.perm_patcher.start()
        
        # Patch CSRF checking - RequestFactory doesn't handle CSRF
        logger.debug("Setting up CSRF patch")
        self.csrf_patcher = patch(
            'django.middleware.csrf.CsrfViewMiddleware.process_view',
            return_value=None
        )
        self.csrf_mock = self.csrf_patcher.start()
        logger.info("Test environment setup complete")
    
    def tearDown(self):
        """Clean up patches."""
        logger.info("Cleaning up test environment")
        self.auth_patcher.stop()
        self.perm_patcher.stop()
        self.csrf_patcher.stop()
        logger.info("Test environment cleanup complete")
    
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
        msg = (
            "Box ID and target location ID are required"
        )
        self.assertIn(msg, data['detail'])
    
    @override_settings(MIDDLEWARE=[])
    def test_move_box_service_error(self):
        """Test move_box view handles service exceptions correctly."""
        logger.info("Starting test_move_box_service_error")
        
        # Create a real Django user for authentication
        logger.debug("Creating test user")
        test_user = User.objects.create_user(
            username='testuser',
            password='testpass',
            email='test@example.com'
        )
        
        # Setup mocks
        logger.debug("Setting up mock objects")
        mock_box = MagicMock(spec=['id', 'code'])
        mock_box.id = 1
        mock_box.code = 'BOX001'
        
        mock_location = MagicMock(spec=['id', 'name'])
        mock_location.id = 2
        mock_location.name = 'Test Location'
        
        # Configure service mock to raise exception
        logger.debug("Configuring service mock")
        mock_service = MagicMock()
        mock_service.move_box.side_effect = Exception("Service error")
        
        try:
            # Use separate patch context managers for better cleanup
            logger.debug("Starting patches")
            with patch('pyerp.business_modules.inventory.urls.Box.objects.get',
                    return_value=mock_box) as mock_box_get:
                with patch(
                    'pyerp.business_modules.inventory.urls.StorageLocation.objects.get',
                    return_value=mock_location
                ) as mock_location_get:
                    with patch(
                        'pyerp.business_modules.inventory.urls.InventoryService',
                        return_value=mock_service
                    ):
                        logger.debug("All patches applied")
                        
                        # Use Django's test client
                        logger.debug("Creating test client")
                        client = self.client
                        client.force_login(test_user)
                        
                        # Make the request
                        logger.debug("Making POST request")
                        response = client.post(
                            '/api/inventory/api/move-box/',
                            data=json.dumps({
                                'box_id': 1,
                                'target_location_id': 2
                            }),
                            content_type='application/json'
                        )
                        logger.debug("POST request completed")
                        
                        # Get response content
                        logger.debug("Getting response content")
                        content = response.content.decode('utf-8')
                        logger.debug(f"Raw content: {content}")
                        content = json.loads(content)
                        logger.debug(f"Parsed content: {content}")
                        
                        # Verify response
                        logger.debug("Verifying response")
                        self.assertEqual(
                            response.status_code,
                            status.HTTP_500_INTERNAL_SERVER_ERROR
                        )
                        self.assertIn("Failed to move box", content['detail'])
                        
                        # Verify mocks were called correctly
                        logger.debug("Verifying mock calls")
                        mock_box_get.assert_called_once_with(id=1)
                        mock_location_get.assert_called_once_with(id=2)
                        
                        logger.debug("All assertions completed")
                        
        except Exception as e:
            logger.error(f"Test failed with error: {str(e)}")
            logger.error(f"Error type: {type(e)}")
            import traceback
            logger.error(f"Traceback:\n{traceback.format_exc()}")
            raise
        finally:
            logger.debug("Exiting test_move_box_service_error")
            # Clean up the test user
            test_user.delete()
    
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
        msg = "Product ID, box slot ID, and quantity are required"
        self.assertIn(msg, data['detail'])
    
    def test_add_product_to_box_service_error(self):
        """Test add_product_to_box view handles service exceptions."""
        try:
            # Mock BoxSlot and VariantProduct objects
            box_slot = Mock(spec=BoxSlot)
            box_slot.id = 1
            box_slot.box.id = 1
            box_slot.box.warehouse.id = 1

            variant_product = Mock(spec=VariantProduct)
            variant_product.id = 1

            # Mock the service to raise an error
            box_slot_model = 'pyerp.business_modules.inventory.models.BoxSlot'
            variant_product_path = (
                'pyerp.business_modules.products.models.VariantProduct'
            )
            box_slot_patch = patch(
                f'{box_slot_model}.objects.get',
                return_value=box_slot
            )
            product_patch = patch(
                f'{variant_product_path}.objects.get',
                return_value=variant_product
            )
            service_path = (
                'pyerp.business_modules.inventory.services.InventoryService.'
                'add_product_to_box_slot'
            )
            service_patch = patch(service_path)
            
            with box_slot_patch, product_patch, service_patch as mock_service:
                mock_service.side_effect = ValueError("Test error message")
                
                # Make the request
                response = self.client.post(
                    reverse('inventory:add_product_to_box'),
                    {
                        'box_slot_id': 1,
                        'variant_product_id': 1,
                        'quantity': 1
                    },
                    content_type='application/json'
                )
                
                # Ensure response is rendered
                response.render()
                
                # Verify response
                self.assertEqual(response.status_code, 400)
                data = json.loads(response.content)
                self.assertEqual(data['error'], "Test error message")
                
                # Verify mocks were called correctly
                mock_service.assert_called_once()
        finally:
            # Cleanup any resources if needed
            pass 