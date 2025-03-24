"""
Tests for mock inventory service functions.
These tests provide better coverage of error handling in services.
"""
import pytest
from unittest.mock import patch, MagicMock, Mock
from django.core.exceptions import ValidationError
from django.test import TestCase

from pyerp.business_modules.inventory.models import Box, BoxSlot, StorageLocation, BoxStorage
from pyerp.business_modules.products.models import VariantProduct
from pyerp.business_modules.inventory.services import InventoryService


@pytest.mark.django_db
class TestInventoryServiceMock(TestCase):
    """Test cases for inventory service using mocks."""

    def setUp(self):
        """Set up test data."""
        self.mock_box = MagicMock(spec=Box)
        self.mock_box.code = "BOX001"
        self.mock_location = MagicMock()
        self.mock_location.name = "Test Location"
        self.mock_location.capacity_limit = 5
        self.mock_location.box_capacity = 10

    def test_move_box_validation_errors(self):
        """Test validation errors when moving a box."""
        # Test with invalid box
        with pytest.raises(ValidationError) as exc:
            InventoryService.move_box(None, MagicMock())
        self.assertEqual(exc.value.messages[0], "Box and target location are required")
            
        # Test with invalid location
        with pytest.raises(ValidationError) as exc:
            InventoryService.move_box(MagicMock(), None)
        self.assertEqual(exc.value.messages[0], "Box and target location are required")
            
        # Test capacity limit
        with patch.object(Box.objects, 'filter') as mock_filter:
            mock_box = MagicMock()
            mock_location = MagicMock()
            mock_location.capacity_limit = 5  # Set as integer
            mock_location.box_capacity = 5  # Set as integer
            
            # Set up the filter to return a mock that says there are already 5 boxes
            filter_mock = MagicMock()
            filter_mock.count.return_value = 5  # Set as integer
            mock_filter.return_value = filter_mock
            
            with pytest.raises(ValidationError) as exc:
                InventoryService.move_box(mock_box, mock_location)
            self.assertEqual(exc.value.messages[0], "Target location has reached capacity limit")

    def test_add_product_to_box_slot_validation_errors(self):
        """Test validation errors when adding a product to a box slot."""
        # Test with invalid product
        with pytest.raises(ValidationError) as exc:
            InventoryService.add_product_to_box_slot(None, MagicMock(), 1)
        self.assertEqual(exc.value.messages[0], "Valid product, box slot, and positive quantity are required")
        
        # Test with invalid box slot
        with pytest.raises(ValidationError) as exc:
            InventoryService.add_product_to_box_slot(MagicMock(), None, 1)
        self.assertEqual(exc.value.messages[0], "Valid product, box slot, and positive quantity are required")
        
        # Test with invalid quantity
        with pytest.raises(ValidationError) as exc:
            InventoryService.add_product_to_box_slot(MagicMock(), MagicMock(), 0)
        self.assertEqual(exc.value.messages[0], "Valid product, box slot, and positive quantity are required")
            
        # Test slot capacity limit
        mock_product = Mock(spec=VariantProduct)
        mock_slot = Mock(spec=BoxSlot)
        mock_slot.id = 1  # Add an ID to the mock slot
        mock_slot.capacity = 10
        mock_slot.box_capacity = 10
        
        # Set up the mock for BoxStorage.objects.filter().aggregate()
        mock_aggregate = Mock(return_value={'total': 6})
        mock_filter = Mock()
        mock_filter.aggregate = mock_aggregate
        BoxStorage.objects.filter = Mock(return_value=mock_filter)
        
        with self.assertRaises(ValidationError) as context:
            InventoryService.add_product_to_box_slot(mock_product, mock_slot, 5)
        
        self.assertEqual(
            context.exception.messages,
            ["Adding this quantity would exceed the slot's capacity"]
        )

    def test_move_product_between_box_slots_validation_errors(self):
        """Test validation errors when moving products between box slots."""
        # Test with invalid source
        with pytest.raises(ValidationError) as exc:
            InventoryService.move_product_between_box_slots(None, MagicMock(), 1)
        self.assertEqual(exc.value.messages[0], "Valid source, target, and positive quantity are required")
        
        # Test with invalid target
        with pytest.raises(ValidationError) as exc:
            InventoryService.move_product_between_box_slots(MagicMock(), None, 1)
        self.assertEqual(exc.value.messages[0], "Valid source, target, and positive quantity are required")
        
        # Test with invalid quantity
        with pytest.raises(ValidationError) as exc:
            InventoryService.move_product_between_box_slots(MagicMock(), MagicMock(), 0)
        self.assertEqual(exc.value.messages[0], "Valid source, target, and positive quantity are required")
            
        # Test moving more than available
        mock_source = MagicMock()
        mock_source.quantity = 5
        mock_target = MagicMock()
        
        with pytest.raises(ValidationError) as exc:
            InventoryService.move_product_between_box_slots(mock_source, mock_target, 10)
        self.assertEqual(exc.value.messages[0], "Cannot move more than available quantity")
            
        # Test target slot capacity
        mock_source.quantity = 10
        mock_target.max_products = 5
        mock_target.available_space = 3
        
        with pytest.raises(ValidationError) as exc:
            InventoryService.move_product_between_box_slots(mock_source, mock_target, 5)
        self.assertEqual(exc.value.messages[0], "Target slot does not have enough capacity")

    def test_remove_product_from_box_slot_validation_errors(self):
        """Test validation errors when removing a product from a box slot."""
        # Test with invalid box storage
        with pytest.raises(ValidationError) as exc:
            InventoryService.remove_product_from_box_slot(None, 1)
        self.assertEqual(exc.value.messages[0], "Valid box storage and positive quantity are required")
        
        # Test with invalid quantity
        with pytest.raises(ValidationError) as exc:
            InventoryService.remove_product_from_box_slot(MagicMock(), 0)
        self.assertEqual(exc.value.messages[0], "Valid box storage and positive quantity are required")
            
        # Test removing more than available
        mock_storage = MagicMock()
        mock_storage.quantity = 5
        
        with pytest.raises(ValidationError) as exc:
            InventoryService.remove_product_from_box_slot(mock_storage, 10)
        self.assertEqual(exc.value.messages[0], "Cannot remove more than available quantity") 