"""
Tests for error handling in the inventory service.
This module tests the InventoryService class directly for proper error behavior.
"""

import pytest
from unittest.mock import patch, MagicMock
from django.test import TestCase

from pyerp.business_modules.inventory.services import InventoryService
from pyerp.business_modules.inventory.models import (
    Box, StorageLocation, BoxSlot, BoxStorage
)

class TestInventoryServiceErrorHandling(TestCase):
    """Test class for inventory service error handling."""
    
    def setUp(self):
        """Set up test data and mocks."""
        # Create mock objects
        self.mock_box = MagicMock(spec=Box)
        self.mock_box.id = 1
        self.mock_box.code = "BOX001"
        
        self.mock_location = MagicMock(spec=StorageLocation)
        self.mock_location.id = 2
        self.mock_location.name = "Test Location"
        
        self.mock_box_slot = MagicMock(spec=BoxSlot)
        self.mock_box_slot.id = 3
        self.mock_box_slot.box = self.mock_box
        
        self.mock_product = MagicMock()
        self.mock_product.id = 4
        self.mock_product.name = "Test Product"
        
        self.mock_user = MagicMock()
        self.mock_user.id = 5
        self.mock_user.username = "testuser"
        
        # Create the service instance
        self.service = InventoryService()
    
    @patch('pyerp.business_modules.inventory.services.BoxStorage.objects.filter')
    def test_move_box_with_permission_error(self, mock_filter):
        """Test that move_box correctly handles permission errors."""
        # Set up the mock to raise a PermissionError
        mock_filter.side_effect = PermissionError("User lacks permission")
        
        # Test the service method raises the appropriate error
        with self.assertRaises(PermissionError):
            self.service.move_box(
                box=self.mock_box,
                target_storage_location=self.mock_location,
                user=self.mock_user
            )
    
    @patch('pyerp.business_modules.inventory.services.BoxStorage.objects.filter')
    def test_move_box_with_value_error(self, mock_filter):
        """Test that move_box correctly handles validation errors."""
        # Set up the mock to raise a ValueError
        mock_filter.side_effect = ValueError("Invalid data")
        
        # Test the service method raises the appropriate error
        with self.assertRaises(ValueError):
            self.service.move_box(
                box=self.mock_box,
                target_storage_location=self.mock_location,
                user=self.mock_user
            )
    
    @patch('pyerp.business_modules.inventory.services.ProductStorage.objects.get_or_create')
    def test_add_product_to_box_with_capacity_error(self, mock_get_or_create):
        """Test that add_product_to_box_slot correctly handles capacity errors."""
        # Set up the mock to raise a ValueError for capacity exceeded
        mock_get_or_create.side_effect = ValueError("Capacity exceeded")
        
        # Test the service method raises the appropriate error
        with self.assertRaises(ValueError):
            self.service.add_product_to_box_slot(
                product=self.mock_product,
                box_slot=self.mock_box_slot,
                quantity=100,  # Large quantity to trigger capacity error
                user=self.mock_user
            )
    
    @patch('pyerp.business_modules.inventory.services.BoxStorage.objects.get_or_create')
    def test_add_product_to_box_with_database_error(self, mock_get_or_create):
        """Test that add_product_to_box_slot correctly handles database errors."""
        # Set up the mock to raise a database error
        mock_get_or_create.side_effect = Exception("Database connection error")
        
        # Test the service method raises the appropriate error
        with self.assertRaises(Exception):
            self.service.add_product_to_box_slot(
                product=self.mock_product,
                box_slot=self.mock_box_slot,
                quantity=5,
                user=self.mock_user
            ) 