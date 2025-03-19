"""
Unit tests for the inventory services.
"""

from django.test import TestCase
from django.core.exceptions import ValidationError
from unittest.mock import patch
from datetime import date

from pyerp.business_modules.inventory.models import (
    Box,
    BoxType,
    BoxSlot,
    BoxStorage,
    ProductStorage,
    StorageLocation,
    InventoryMovement,
)
from pyerp.business_modules.inventory.services import InventoryService
from pyerp.business_modules.products.models import VariantProduct, Product


class InventoryServiceTestCase(TestCase):
    """Test case for the inventory service."""

    def setUp(self):
        """Set up test data."""
        # Create a product
        self.product = Product.objects.create(
            name="Test Product",
            description="Test Description",
            is_active=True,
        )
        
        self.variant_product = VariantProduct.objects.create(
            base_product=self.product,
            sku="TEST-SKU-001",
            name="Test Variant",
            is_active=True,
        )
        
        # Create storage locations
        self.source_location = StorageLocation.objects.create(
            name="Source Location",
            location_code="SRC-LOC",
            capacity=10,
            is_active=True,
        )
        
        self.target_location = StorageLocation.objects.create(
            name="Target Location",
            location_code="TGT-LOC",
            capacity=5,
            is_active=True,
        )
        
        # Create box type
        self.box_type = BoxType.objects.create(
            name="Test Box Type",
            description="Test Box Type Description",
            color=BoxType.BoxColor.BLUE,
            slot_count=4,
        )
        
        # Create boxes
        self.source_box = Box.objects.create(
            code="SRC-BOX-001",
            box_type=self.box_type,
            status=Box.BoxStatus.IN_USE,
            storage_location=self.source_location,
        )
        
        self.target_box = Box.objects.create(
            code="TGT-BOX-001",
            box_type=self.box_type,
            status=Box.BoxStatus.AVAILABLE,
            storage_location=self.target_location,
        )
        
        # Create box slots
        self.source_slot = BoxSlot.objects.create(
            box=self.source_box,
            slot_number=1,
            slot_code="SRC-SLOT-1",
            max_products=10,
        )
        
        self.target_slot = BoxSlot.objects.create(
            box=self.target_box,
            slot_number=1,
            slot_code="TGT-SLOT-1",
            max_products=10,
        )
        
        # Create product storage
        self.product_storage = ProductStorage.objects.create(
            product=self.variant_product,
            storage_location=self.source_location,
            quantity=5,
        )
        
        # Create box storage
        self.box_storage = BoxStorage.objects.create(
            product_storage=self.product_storage,
            box_slot=self.source_slot,
            quantity=5,
            batch_number="BATCH-001",
        )
        
        # Update occupied status
        self.source_slot.update_occupied_status()

    def test_move_box(self):
        """Test moving a box to a different storage location."""
        result = InventoryService.move_box(
            box=self.source_box,
            target_storage_location=self.target_location,
        )
        
        # Check that the box's location was updated
        self.assertEqual(result.storage_location, self.target_location)
        
        # Reload from database to verify persistence
        updated_box = Box.objects.get(id=self.source_box.id)
        self.assertEqual(updated_box.storage_location, self.target_location)
        
        # Check that a movement record was created
        movements = InventoryMovement.objects.filter(
            movement_type=InventoryMovement.MovementType.TRANSFER,
            reference__startswith="Box move:",
        )
        self.assertTrue(movements.exists())

    def test_add_product_to_box_slot(self):
        """Test adding a product to a box slot."""
        result = InventoryService.add_product_to_box_slot(
            product=self.variant_product,
            box_slot=self.target_slot,
            quantity=3,
            batch_number="BATCH-002",
        )
        
        # Verify the result
        self.assertEqual(result.quantity, 3)
        self.assertEqual(result.box_slot, self.target_slot)
        self.assertEqual(result.batch_number, "BATCH-002")
        
        # Check that the box slot is now occupied
        self.target_slot.refresh_from_db()
        self.assertTrue(self.target_slot.occupied)
        
        # Check that a product storage record was created for the target location
        product_storage = ProductStorage.objects.get(
            product=self.variant_product,
            storage_location=self.target_location,
        )
        self.assertEqual(product_storage.quantity, 3)
        
        # Check that a movement record was created
        movement = InventoryMovement.objects.get(
            product=self.variant_product,
            to_slot=self.target_slot,
            quantity=3,
            movement_type=InventoryMovement.MovementType.RECEIPT,
        )
        self.assertIsNotNone(movement)

    def test_move_product_between_box_slots(self):
        """Test moving a product between box slots."""
        result = InventoryService.move_product_between_box_slots(
            source_box_storage=self.box_storage,
            target_box_slot=self.target_slot,
            quantity=2,
        )
        
        # Unpack the result
        source_updated, target_updated = result
        
        # Check source update
        self.assertIsNotNone(source_updated)
        self.assertEqual(source_updated.quantity, 3)  # 5 - 2 = 3
        
        # Check target update
        self.assertEqual(target_updated.quantity, 2)
        self.assertEqual(target_updated.box_slot, self.target_slot)
        
        # Check that both slots are occupied
        self.source_slot.refresh_from_db()
        self.target_slot.refresh_from_db()
        self.assertTrue(self.source_slot.occupied)
        self.assertTrue(self.target_slot.occupied)
        
        # Check that product storage quantities were updated
        source_product_storage = ProductStorage.objects.get(
            product=self.variant_product,
            storage_location=self.source_location,
        )
        target_product_storage = ProductStorage.objects.get(
            product=self.variant_product,
            storage_location=self.target_location,
        )
        self.assertEqual(source_product_storage.quantity, 3)
        self.assertEqual(target_product_storage.quantity, 2)
        
        # Check that a movement record was created
        movement = InventoryMovement.objects.get(
            product=self.variant_product,
            from_slot=self.source_slot,
            to_slot=self.target_slot,
            quantity=2,
            movement_type=InventoryMovement.MovementType.TRANSFER,
        )
        self.assertIsNotNone(movement)

    def test_move_all_product_between_box_slots(self):
        """Test moving all of a product between box slots."""
        result = InventoryService.move_product_between_box_slots(
            source_box_storage=self.box_storage,
            target_box_slot=self.target_slot,
            quantity=5,  # Move all 5 units
        )
        
        # Unpack the result
        source_updated, target_updated = result
        
        # Source should be None as all product was moved
        self.assertIsNone(source_updated)
        
        # Target should have all 5 units
        self.assertEqual(target_updated.quantity, 5)
        
        # Source slot should no longer be occupied
        self.source_slot.refresh_from_db()
        self.assertFalse(self.source_slot.occupied)
        
        # Target slot should be occupied
        self.target_slot.refresh_from_db()
        self.assertTrue(self.target_slot.occupied)
        
        # Check that no BoxStorage record exists for the source slot
        self.assertFalse(
            BoxStorage.objects.filter(box_slot=self.source_slot).exists()
        )

    def test_remove_product_from_box_slot(self):
        """Test removing a product from a box slot."""
        result = InventoryService.remove_product_from_box_slot(
            box_storage=self.box_storage,
            quantity=2,
            reason="Testing removal",
        )
        
        # Check the result
        self.assertIsNotNone(result)
        self.assertEqual(result.quantity, 3)  # 5 - 2 = 3
        
        # Check that the box slot is still occupied
        self.source_slot.refresh_from_db()
        self.assertTrue(self.source_slot.occupied)
        
        # Check that the product storage quantity was updated
        self.product_storage.refresh_from_db()
        self.assertEqual(self.product_storage.quantity, 3)
        
        # Check that a movement record was created
        movement = InventoryMovement.objects.get(
            product=self.variant_product,
            from_slot=self.source_slot,
            quantity=2,
            movement_type=InventoryMovement.MovementType.PICK,
        )
        self.assertIsNotNone(movement)

    def test_remove_all_product_from_box_slot(self):
        """Test removing all of a product from a box slot."""
        result = InventoryService.remove_product_from_box_slot(
            box_storage=self.box_storage,
            quantity=5,  # Remove all 5 units
            reason="disposal",
        )
        
        # Result should be None as all product was removed
        self.assertIsNone(result)
        
        # Check that the box slot is no longer occupied
        self.source_slot.refresh_from_db()
        self.assertFalse(self.source_slot.occupied)
        
        # Check that the BoxStorage record was deleted
        self.assertFalse(
            BoxStorage.objects.filter(id=self.box_storage.id).exists()
        )
        
        # Check that a movement record was created with the disposal type
        movement = InventoryMovement.objects.get(
            product=self.variant_product,
            from_slot=self.source_slot,
            quantity=5,
            movement_type=InventoryMovement.MovementType.DISPOSAL,
        )
        self.assertIsNotNone(movement)

    def test_validation_errors(self):
        """Test that validation errors are raised appropriately."""
        # Test moving a box to a full location
        for i in range(5):  # Fill up the target location to capacity
            Box.objects.create(
                code=f"FILL-BOX-{i}",
                box_type=self.box_type,
                storage_location=self.target_location,
            )
        
        with self.assertRaises(ValidationError):
            InventoryService.move_box(
                box=self.source_box,
                target_storage_location=self.target_location,
            )
        
        # Test adding too many products to a slot
        self.target_slot.max_products = 2
        self.target_slot.save()
        
        with self.assertRaises(ValidationError):
            InventoryService.add_product_to_box_slot(
                product=self.variant_product,
                box_slot=self.target_slot,
                quantity=3,  # Too many for max_products=2
            )
        
        # Test moving more product than available
        with self.assertRaises(ValidationError):
            InventoryService.move_product_between_box_slots(
                source_box_storage=self.box_storage,
                target_box_slot=self.target_slot,
                quantity=10,  # More than the 5 available
            )
        
        # Test removing more product than available
        with self.assertRaises(ValidationError):
            InventoryService.remove_product_from_box_slot(
                box_storage=self.box_storage,
                quantity=10,  # More than the 5 available
            ) 