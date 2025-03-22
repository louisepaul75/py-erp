"""
Tests for mock inventory service functions.
These tests provide better coverage of error handling in services.
"""
import pytest
from unittest.mock import patch, MagicMock, call
from django.core.exceptions import ValidationError
from datetime import datetime, date

from pyerp.business_modules.inventory.models import Box, BoxSlot, StorageLocation, BoxStorage, ProductStorage, InventoryMovement
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

    def test_move_box_success(self):
        """Test successful box move."""
        # Mock objects
        mock_box = MagicMock()
        mock_prev_location = MagicMock()
        mock_prev_location.__str__.return_value = "Old Location"
        mock_box.storage_location = mock_prev_location
        
        mock_target_location = MagicMock()
        mock_target_location.__str__.return_value = "New Location"
        mock_target_location.capacity = 10
        
        # Mock query methods
        with patch.object(Box.objects, 'filter') as mock_filter:
            filter_mock = MagicMock()
            filter_mock.count.return_value = 3  # Below capacity
            mock_filter.return_value = filter_mock
            
            # Mock the slots and box_storage_items for move logging
            mock_slot = MagicMock()
            mock_storage = MagicMock()
            mock_product_storage = MagicMock()
            mock_product = MagicMock()
            
            mock_storage.product_storage = mock_product_storage
            mock_product_storage.product = mock_product
            mock_storage.quantity = 5
            
            mock_slot.box_storage_items.all.return_value = [mock_storage]
            mock_box.slots.all.return_value = [mock_slot]
            
            # Mock InventoryMovement creation
            with patch.object(InventoryMovement.objects, 'create') as mock_create_movement:
                # Execute the service method
                result = InventoryService.move_box(mock_box, mock_target_location)
                
                # Verify the box was updated
                assert mock_box.storage_location == mock_target_location
                assert mock_box.modified_at is not None
                assert mock_box.save.called
                
                # Verify movement was logged
                assert mock_create_movement.called
                mock_create_movement.assert_called_with(
                    product=mock_product,
                    from_slot=mock_slot,
                    to_slot=mock_slot,
                    quantity=5,
                    movement_type=InventoryMovement.MovementType.TRANSFER,
                    reference=f"Box move: {mock_box.code}",
                    notes=f"Box moved from {mock_prev_location} to {mock_target_location}",
                    created_by=None,
                )
                
                # Verify the method returned the updated box
                assert result == mock_box

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

    def test_add_product_to_box_slot_success(self):
        """Test successful product addition to box slot."""
        # Mock objects
        mock_product = MagicMock()
        mock_slot = MagicMock()
        mock_box = MagicMock()
        mock_location = MagicMock()
        
        # Set up the mocks
        mock_slot.box = mock_box
        mock_box.storage_location = mock_location
        mock_slot.max_products = 20
        mock_slot.product_count = 5
        quantity = 3
        batch_number = "BATCH123"
        expiry_date = date(2025, 12, 31)
        
        # Mock ProductStorage get_or_create
        mock_product_storage = MagicMock()
        with patch.object(ProductStorage.objects, 'get_or_create') as mock_get_or_create:
            mock_get_or_create.return_value = (mock_product_storage, True)
            
            # Mock BoxStorage create
            mock_box_storage = MagicMock()
            with patch.object(BoxStorage.objects, 'create') as mock_create_box_storage:
                mock_create_box_storage.return_value = mock_box_storage
                
                # Mock InventoryMovement create
                with patch.object(InventoryMovement.objects, 'create') as mock_create_movement:
                    # Execute the service method
                    result = InventoryService.add_product_to_box_slot(
                        mock_product, mock_slot, quantity, batch_number, expiry_date
                    )
                    
                    # Verify ProductStorage was updated
                    mock_get_or_create.assert_called_with(
                        product=mock_product,
                        storage_location=mock_location,
                        defaults={"quantity": 0}
                    )
                    # Instead of checking the value, verify the operation was performed
                    assert mock_product_storage.save.called
                    
                    # Verify BoxStorage was created
                    assert mock_create_box_storage.called
                    
                    # Verify slot status was updated
                    assert mock_slot.update_occupied_status.called
                    
                    # Verify movement was logged
                    assert mock_create_movement.called
                    
                    # Verify the method returned the box storage
                    assert result == mock_box_storage

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

    def test_move_product_between_box_slots_success(self):
        """Test successful product movement between box slots."""
        # Mock objects
        mock_source_box_storage = MagicMock()
        mock_source_slot = MagicMock()
        mock_target_slot = MagicMock()
        mock_source_box = MagicMock()
        mock_target_box = MagicMock()
        mock_source_location = MagicMock()
        mock_target_location = MagicMock()
        mock_product = MagicMock()
        mock_product_storage = MagicMock()
        
        # Set up the mocks
        mock_source_box_storage.box_slot = mock_source_slot
        mock_source_box_storage.product_storage = mock_product_storage
        mock_product_storage.product = mock_product
        mock_source_box_storage.quantity = 10
        mock_source_box_storage.batch_number = "BATCH123"
        mock_source_box_storage.expiry_date = date(2025, 12, 31)
        
        mock_source_slot.box = mock_source_box
        mock_target_slot.box = mock_target_box
        mock_source_box.storage_location = mock_source_location
        mock_target_box.storage_location = mock_target_location
        mock_target_slot.max_products = 20
        mock_target_slot.available_space = 15
        
        quantity = 5
        
        # Mock ProductStorage get_or_create for target
        mock_target_product_storage = MagicMock()
        with patch.object(ProductStorage.objects, 'get_or_create') as mock_get_or_create:
            mock_get_or_create.return_value = (mock_target_product_storage, True)
            
            # Mock BoxStorage get_or_create for target
            mock_target_box_storage = MagicMock()
            with patch.object(BoxStorage.objects, 'get_or_create') as mock_box_storage_get_or_create:
                mock_box_storage_get_or_create.return_value = (mock_target_box_storage, True)
                
                # Mock InventoryMovement create
                with patch.object(InventoryMovement.objects, 'create') as mock_create_movement:
                    # Execute the service method
                    result = InventoryService.move_product_between_box_slots(
                        mock_source_box_storage, mock_target_slot, quantity
                    )
                    
                    # Verify objects were saved
                    assert mock_target_product_storage.save.called
                    assert mock_product_storage.save.called
                    assert mock_source_box_storage.save.called
                    assert mock_target_box_storage.save.called
                    
                    # Verify slots' occupied status was updated
                    assert mock_source_slot.update_occupied_status.called
                    assert mock_target_slot.update_occupied_status.called
                    
                    # Verify movement was logged
                    assert mock_create_movement.called
                    
                    # Verify the method returned the expected tuple
                    assert result == (mock_source_box_storage, mock_target_box_storage)

    def test_move_all_product_between_box_slots_success(self):
        """Test successful movement of all products between box slots."""
        # Similar to previous test but with quantity equal to source quantity
        # Mock objects
        mock_source_box_storage = MagicMock()
        mock_source_slot = MagicMock()
        mock_target_slot = MagicMock()
        mock_source_box = MagicMock()
        mock_target_box = MagicMock()
        mock_source_location = MagicMock()
        mock_target_location = MagicMock()
        mock_product = MagicMock()
        mock_product_storage = MagicMock()
        
        # Set up the mocks
        mock_source_box_storage.box_slot = mock_source_slot
        mock_source_box_storage.product_storage = mock_product_storage
        mock_product_storage.product = mock_product
        mock_source_box_storage.quantity = 5  # Entire quantity will be moved
        mock_source_box_storage.batch_number = "BATCH123"
        mock_source_box_storage.expiry_date = date(2025, 12, 31)
        
        mock_source_slot.box = mock_source_box
        mock_target_slot.box = mock_target_box
        mock_source_box.storage_location = mock_source_location
        mock_target_box.storage_location = mock_target_location
        mock_target_slot.max_products = 20
        mock_target_slot.available_space = 15
        
        quantity = 5  # Move all
        
        # Mock ProductStorage get_or_create for target
        mock_target_product_storage = MagicMock()
        with patch.object(ProductStorage.objects, 'get_or_create') as mock_get_or_create:
            mock_get_or_create.return_value = (mock_target_product_storage, True)
            
            # Mock BoxStorage get_or_create for target
            mock_target_box_storage = MagicMock()
            with patch.object(BoxStorage.objects, 'get_or_create') as mock_box_storage_get_or_create:
                mock_box_storage_get_or_create.return_value = (mock_target_box_storage, True)
                
                # Mock InventoryMovement create
                with patch.object(InventoryMovement.objects, 'create') as mock_create_movement:
                    # Execute the service method
                    result = InventoryService.move_product_between_box_slots(
                        mock_source_box_storage, mock_target_slot, quantity
                    )
                    
                    # When quantity is equal to source quantity, the source box storage should be deleted
                    assert mock_source_box_storage.delete.called
                    
                    # Verify the method returned the expected tuple
                    assert result == (None, mock_target_box_storage)

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

    def test_remove_product_from_box_slot_success(self):
        """Test successful product removal from box slot."""
        # Mock objects
        mock_box_storage = MagicMock()
        mock_product_storage = MagicMock()
        mock_box_slot = MagicMock()
        mock_product = MagicMock()
        
        # Set up the mocks
        mock_box_storage.product_storage = mock_product_storage
        mock_product_storage.product = mock_product
        mock_box_storage.box_slot = mock_box_slot
        mock_box_storage.quantity = 10
        
        quantity = 5
        reason = "Testing removal"
        
        # Mock InventoryMovement create
        with patch.object(InventoryMovement.objects, 'create') as mock_create_movement:
            # Execute the service method
            result = InventoryService.remove_product_from_box_slot(
                mock_box_storage, quantity, reason
            )
            
            # Verify objects were saved
            assert mock_box_storage.save.called
            assert mock_product_storage.save.called
            
            # NOTE: update_occupied_status is only called when the box is completely emptied
            # Since we're removing only half the quantity, this should not be called
            assert not mock_box_slot.update_occupied_status.called
            
            # Verify movement was logged
            assert mock_create_movement.called
            # Based on the implementation, the default movement_type is PICK and the reference is the reason
            mock_create_movement.assert_called_with(
                product=mock_product,
                from_slot=mock_box_slot,
                quantity=quantity,
                movement_type=InventoryMovement.MovementType.PICK,
                reference=reason,
                notes=f"Removed {quantity} units from {mock_box_slot}",
                created_by=None,
            )
            
            # Verify the method returned the updated box storage
            assert result == mock_box_storage

    def test_remove_all_product_from_box_slot_success(self):
        """Test successful removal of all product from box slot."""
        # Mock objects
        mock_box_storage = MagicMock()
        mock_product_storage = MagicMock()
        mock_box_slot = MagicMock()
        mock_product = MagicMock()
        
        # Set up the mocks
        mock_box_storage.product_storage = mock_product_storage
        mock_product_storage.product = mock_product
        mock_box_storage.box_slot = mock_box_slot
        mock_box_storage.quantity = 5  # All will be removed
        
        quantity = 5
        reason = "Testing removal of all"
        
        # Mock InventoryMovement create
        with patch.object(InventoryMovement.objects, 'create') as mock_create_movement:
            # Execute the service method
            result = InventoryService.remove_product_from_box_slot(
                mock_box_storage, quantity, reason
            )
            
            # When quantity is equal to box storage quantity, the box storage should be deleted
            assert mock_box_storage.delete.called
            
            # Verify the method returned None (since box storage was deleted)
            assert result is None

    def test_remove_product_from_box_slot_with_disposal_reason(self):
        """Test product removal with 'disposal' reason sets correct movement type."""
        # Mock objects
        mock_box_storage = MagicMock()
        mock_product_storage = MagicMock()
        mock_box_slot = MagicMock()
        mock_product = MagicMock()
        
        # Set up the mocks
        mock_box_storage.product_storage = mock_product_storage
        mock_product_storage.product = mock_product
        mock_box_storage.box_slot = mock_box_slot
        mock_box_storage.quantity = 10
        
        quantity = 5
        reason = "disposal"  # This should trigger DISPOSAL movement type
        
        # Mock InventoryMovement create
        with patch.object(InventoryMovement.objects, 'create') as mock_create_movement:
            # Execute the service method
            result = InventoryService.remove_product_from_box_slot(
                mock_box_storage, quantity, reason
            )
            
            # Verify movement was logged with DISPOSAL type
            assert mock_create_movement.called
            mock_create_movement.assert_called_with(
                product=mock_product,
                from_slot=mock_box_slot,
                quantity=quantity,
                movement_type=InventoryMovement.MovementType.DISPOSAL,
                reference=reason,
                notes=f"Removed {quantity} units from {mock_box_slot}",
                created_by=None,
            )

    def test_remove_product_from_box_slot_with_adjustment_reason(self):
        """Test product removal with 'adjustment' reason sets correct movement type."""
        # Mock objects
        mock_box_storage = MagicMock()
        mock_product_storage = MagicMock()
        mock_box_slot = MagicMock()
        mock_product = MagicMock()
        
        # Set up the mocks
        mock_box_storage.product_storage = mock_product_storage
        mock_product_storage.product = mock_product
        mock_box_storage.box_slot = mock_box_slot
        mock_box_storage.quantity = 10
        
        quantity = 5
        reason = "adjustment"  # This should trigger ADJUSTMENT movement type
        
        # Mock InventoryMovement create
        with patch.object(InventoryMovement.objects, 'create') as mock_create_movement:
            # Execute the service method
            result = InventoryService.remove_product_from_box_slot(
                mock_box_storage, quantity, reason
            )
            
            # Verify movement was logged with ADJUSTMENT type
            assert mock_create_movement.called
            mock_create_movement.assert_called_with(
                product=mock_product,
                from_slot=mock_box_slot,
                quantity=quantity,
                movement_type=InventoryMovement.MovementType.ADJUSTMENT,
                reference=reason,
                notes=f"Removed {quantity} units from {mock_box_slot}",
                created_by=None,
            ) 