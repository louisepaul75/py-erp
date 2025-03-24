"""
Tests for mock inventory service functions.
These tests provide better coverage of error handling in services.
"""
import pytest
from unittest.mock import patch, MagicMock
from django.core.exceptions import ValidationError

from pyerp.business_modules.inventory.models import Box, BoxSlot, StorageLocation
from pyerp.business_modules.products.models import VariantProduct
from pyerp.business_modules.inventory.services import InventoryService


@pytest.mark.django_db
class TestInventoryServiceMock:
    """Test class for mocking inventory service functions."""

    def test_move_box_validation_errors(self):
        """Test validation errors when moving a box."""
        # Test with invalid box
        with pytest.raises(ValidationError, match="Box and target location are required"):
            InventoryService.move_box(None, MagicMock())
            
        # Test with invalid location
        with pytest.raises(ValidationError, match="Box and target location are required"):
            InventoryService.move_box(MagicMock(), None)
            
        # Test capacity limit
        with patch.object(Box.objects, 'filter') as mock_filter:
            mock_box = MagicMock()
            mock_location = MagicMock()
            mock_location.capacity = 5
            
            # Set up the filter to return a mock that says there are already 5 boxes
            filter_mock = MagicMock()
            filter_mock.count.return_value = 5
            mock_filter.return_value = filter_mock
            
            with pytest.raises(ValidationError, match="Target location has reached capacity limit"):
                InventoryService.move_box(mock_box, mock_location)

    def test_add_product_to_box_slot_validation_errors(self):
        """Test validation errors when adding a product to a box slot."""
        # Test with invalid product
        with pytest.raises(ValidationError, match="Valid product, box slot, and positive quantity are required"):
            InventoryService.add_product_to_box_slot(None, MagicMock(), 1)
        
        # Test with invalid box slot
        with pytest.raises(ValidationError, match="Valid product, box slot, and positive quantity are required"):
            InventoryService.add_product_to_box_slot(MagicMock(), None, 1)
        
        # Test with invalid quantity
        with pytest.raises(ValidationError, match="Valid product, box slot, and positive quantity are required"):
            InventoryService.add_product_to_box_slot(MagicMock(), MagicMock(), 0)
            
        # Test slot capacity limit
        mock_product = MagicMock()
        mock_slot = MagicMock()
        mock_slot.max_products = 10
        mock_slot.product_count = 8
        
        with pytest.raises(ValidationError, match="Adding 5 items would exceed the slot capacity of 10"):
            InventoryService.add_product_to_box_slot(mock_product, mock_slot, 5)

    def test_move_product_between_box_slots_validation_errors(self):
        """Test validation errors when moving products between box slots."""
        # Test with invalid source
        with pytest.raises(ValidationError, match="Valid source, target, and positive quantity are required"):
            InventoryService.move_product_between_box_slots(None, MagicMock(), 1)
        
        # Test with invalid target
        with pytest.raises(ValidationError, match="Valid source, target, and positive quantity are required"):
            InventoryService.move_product_between_box_slots(MagicMock(), None, 1)
        
        # Test with invalid quantity
        with pytest.raises(ValidationError, match="Valid source, target, and positive quantity are required"):
            InventoryService.move_product_between_box_slots(MagicMock(), MagicMock(), 0)
            
        # Test moving more than available
        mock_source = MagicMock()
        mock_source.quantity = 5
        mock_target = MagicMock()
        
        with pytest.raises(ValidationError, match="Cannot move more than available quantity"):
            InventoryService.move_product_between_box_slots(mock_source, mock_target, 10)
            
        # Test target slot capacity
        mock_source.quantity = 10
        mock_target.max_products = 5
        mock_target.available_space = 3
        
        with pytest.raises(ValidationError, match="Target slot does not have enough capacity"):
            InventoryService.move_product_between_box_slots(mock_source, mock_target, 5)

    def test_remove_product_from_box_slot_validation_errors(self):
        """Test validation errors when removing a product from a box slot."""
        # Test with invalid box storage
        with pytest.raises(ValidationError, match="Valid box storage and positive quantity are required"):
            InventoryService.remove_product_from_box_slot(None, 1)
        
        # Test with invalid quantity
        with pytest.raises(ValidationError, match="Valid box storage and positive quantity are required"):
            InventoryService.remove_product_from_box_slot(MagicMock(), 0)
            
        # Test removing more than available
        mock_storage = MagicMock()
        mock_storage.quantity = 5
        
        with pytest.raises(ValidationError, match="Cannot remove more than available quantity"):
            InventoryService.remove_product_from_box_slot(mock_storage, 10) 