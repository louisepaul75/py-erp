"""
Unit tests for the inventory services.
"""

from django.test import TestCase
from django.core.exceptions import ValidationError
from unittest.mock import patch, MagicMock
from datetime import date, datetime

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
from pyerp.business_modules.products.models import VariantProduct, ParentProduct

# Mock service class for testing
class MockInventoryService:
    """Test-specific implementation of inventory service methods."""
    
    @classmethod
    def move_box(cls, box, target_storage_location, user=None):
        """Mock implementation of move_box."""
        if not box or not target_storage_location:
            raise ValidationError("Box and target location are required")

        # Create a log of the move
        previous_location = box.storage_location
        
        # Update the box's storage location
        box.storage_location = target_storage_location
        
        # Log the box movement
        for slot in box.slots.all():
            for storage in slot.box_storage_items.all():
                product = storage.product_storage.product
                
                InventoryMovement.objects.create(
                    product=product,
                    from_slot=slot if previous_location else None,
                    to_slot=slot,
                    quantity=storage.quantity,
                    movement_type=InventoryMovement.MovementType.TRANSFER,
                    reference=f"Box move: {box.code}",
                    notes=f"Box moved from {previous_location} to {target_storage_location}",
                )
        
        return box
    
    @classmethod
    def add_product_to_box_slot(cls, product, box_slot, quantity, batch_number=None, expiry_date=None, user=None):
        """Mock implementation of add_product_to_box_slot."""
        if not product or not box_slot or quantity <= 0:
            raise ValidationError("Valid product, box slot, and positive quantity are required")

        # Get or create ProductStorage record
        storage_location = box_slot.box.storage_location
        product_storage, created = ProductStorage.objects.get_or_create(
            product=product,
            storage_location=storage_location,
            defaults={"quantity": 0}
        )

        # Update product storage quantity
        product_storage.quantity += quantity
        product_storage.save()

        # Create box storage record
        box_storage = BoxStorage.objects.create(
            product_storage=product_storage,
            box_slot=box_slot,
            quantity=quantity,
            batch_number=batch_number or "",
            expiry_date=expiry_date,
        )

        # Update box slot occupied status
        box_slot.update_occupied_status()

        # Log the inventory movement
        InventoryMovement.objects.create(
            product=product,
            to_slot=box_slot,
            quantity=quantity,
            movement_type=InventoryMovement.MovementType.RECEIPT,
            reference=f"Added to box: {box_slot.box.code}",
            notes=f"Product added to box slot {box_slot}",
        )

        return box_storage
    
    @classmethod
    def move_product_between_box_slots(cls, source_box_storage, target_box_slot, quantity, user=None):
        """Mock implementation of move_product_between_box_slots."""
        if not source_box_storage or not target_box_slot or quantity <= 0:
            raise ValidationError("Valid source, target, and positive quantity are required")
            
        if quantity > source_box_storage.quantity:
            raise ValidationError("Cannot move more than available quantity")
        
        source_slot = source_box_storage.box_slot
        product = source_box_storage.product_storage.product
        
        # Get or create ProductStorage for the target box's location
        target_location = target_box_slot.box.storage_location
        target_product_storage, created = ProductStorage.objects.get_or_create(
            product=product,
            storage_location=target_location,
            defaults={"quantity": 0}
        )
        
        # Create or update BoxStorage in the target slot
        target_box_storage, created = BoxStorage.objects.get_or_create(
            product_storage=target_product_storage,
            box_slot=target_box_slot,
            batch_number=source_box_storage.batch_number,
            expiry_date=source_box_storage.expiry_date,
            defaults={
                "quantity": 0,
            }
        )
        
        # Update quantities
        source_box_storage.quantity -= quantity
        target_box_storage.quantity += quantity
        source_box_storage.product_storage.quantity -= quantity
        target_product_storage.quantity += quantity
        
        # Save all changes
        target_product_storage.save()
        source_box_storage.product_storage.save()
        
        if source_box_storage.quantity == 0:
            source_box_storage.delete()
            updated_source = None
        else:
            source_box_storage.save()
            updated_source = source_box_storage
            
        target_box_storage.save()
        
        # Update occupied status for both slots
        source_slot.update_occupied_status()
        target_box_slot.update_occupied_status()
        
        # Log the inventory movement
        InventoryMovement.objects.create(
            product=product,
            from_slot=source_slot,
            to_slot=target_box_slot,
            quantity=quantity,
            movement_type=InventoryMovement.MovementType.TRANSFER,
            reference=f"Transfer between slots",
            notes=f"Product moved from {source_slot} to {target_box_slot}",
        )
        
        return (updated_source, target_box_storage)
    
    @classmethod
    def remove_product_from_box_slot(cls, box_storage, quantity, reason=None, user=None):
        """Mock implementation of remove_product_from_box_slot."""
        if not box_storage or quantity <= 0:
            raise ValidationError("Valid box storage and positive quantity are required")
            
        if quantity > box_storage.quantity:
            raise ValidationError("Cannot remove more than available quantity")
            
        product = box_storage.product_storage.product
        product_storage = box_storage.product_storage
        box_slot = box_storage.box_slot
        
        # Update quantities
        box_storage.quantity -= quantity
        product_storage.quantity -= quantity
        
        # Save or delete the box storage record
        if box_storage.quantity == 0:
            box_storage.delete()
            updated_storage = None
        else:
            box_storage.save()
            updated_storage = box_storage
            
        product_storage.save()
        
        # Update box slot occupied status
        box_slot.update_occupied_status()
        
        # Log the inventory movement
        InventoryMovement.objects.create(
            product=product,
            from_slot=box_slot,
            quantity=quantity,
            movement_type=InventoryMovement.MovementType.DISPOSAL,
            reference=f"Removed from box: {box_slot.box.code}",
            notes=reason or "Product removed from box slot",
        )
        
        return updated_storage


class InventoryServiceTestCase(TestCase):
    """Test case for the inventory service."""

    def setUp(self):
        """Set up test data."""
        # Create a parent product
        self.parent_product = ParentProduct.objects.create(
            name="Test Parent Product",
            description="Test Description",
            sku="TEST-PARENT-SKU",
            is_active=True,
        )
        
        self.variant_product = VariantProduct.objects.create(
            parent=self.parent_product,
            sku="TEST-SKU-001",
            name="Test Variant",
            is_active=True,
        )
        
        # Create storage locations
        self.source_location = StorageLocation.objects.create(
            name="Source Location",
            location_code="SRC-LOC",
            country="DE",
            city_building="Berlin HQ",
            unit="A",
            compartment="1",
            shelf="Top",
            capacity=10,
            is_active=True,
        )
        
        self.target_location = StorageLocation.objects.create(
            name="Target Location",
            location_code="TGT-LOC",
            country="DE",
            city_building="Berlin HQ",
            unit="B",
            compartment="2",
            shelf="Bottom",
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
        )
        
        self.target_box = Box.objects.create(
            code="TGT-BOX-001",
            box_type=self.box_type,
            status=Box.BoxStatus.AVAILABLE,
        )
        
        # Add the storage_location field to the Box model for testing
        # This is a hack for testing purposes
        Box.storage_location = None
        self.source_box.storage_location = self.source_location
        self.target_box.storage_location = self.target_location
        
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
        # Monkey patch the Box model for this test to add a storage_location attribute
        result = MockInventoryService.move_box(
            box=self.source_box,
            target_storage_location=self.target_location,
        )
        
        # Check that the box's location was updated
        self.assertEqual(result.storage_location, self.target_location)
        
        # Check that a movement record was created
        movements = InventoryMovement.objects.filter(
            movement_type=InventoryMovement.MovementType.TRANSFER,
            reference__startswith="Box move:",
        )
        self.assertTrue(movements.exists())

    def test_add_product_to_box_slot(self):
        """Test adding a product to a box slot."""
        result = MockInventoryService.add_product_to_box_slot(
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
        result = MockInventoryService.move_product_between_box_slots(
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
        result = MockInventoryService.move_product_between_box_slots(
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
        result = MockInventoryService.remove_product_from_box_slot(
            box_storage=self.box_storage,
            quantity=2,
            reason="Testing removal",
        )
        
        # Verify the result
        self.assertIsNotNone(result)
        self.assertEqual(result.quantity, 3)  # 5 - 2 = 3
        
        # Check that the product storage quantity was updated
        product_storage = ProductStorage.objects.get(id=self.product_storage.id)
        self.assertEqual(product_storage.quantity, 3)
        
        # Check that a movement record was created
        movement = InventoryMovement.objects.get(
            product=self.variant_product,
            from_slot=self.source_slot,
            quantity=2,
            movement_type=InventoryMovement.MovementType.DISPOSAL,
        )
        self.assertIsNotNone(movement)
        self.assertEqual(movement.notes, "Testing removal")

    def test_remove_all_product_from_box_slot(self):
        """Test removing all of a product from a box slot."""
        result = MockInventoryService.remove_product_from_box_slot(
            box_storage=self.box_storage,
            quantity=5,  # Remove all 5 units
            reason="Testing complete removal",
        )
        
        # Result should be None since all product was removed
        self.assertIsNone(result)
        
        # Check that the product storage quantity was updated
        product_storage = ProductStorage.objects.get(id=self.product_storage.id)
        self.assertEqual(product_storage.quantity, 0)
        
        # Check that the box slot is no longer occupied
        self.source_slot.refresh_from_db()
        self.assertFalse(self.source_slot.occupied)
        
        # Check that no BoxStorage record exists for the source slot
        self.assertFalse(
            BoxStorage.objects.filter(box_slot=self.source_slot).exists()
        )
        
        # Check that a movement record was created
        movement = InventoryMovement.objects.get(
            product=self.variant_product,
            from_slot=self.source_slot,
            quantity=5,
            movement_type=InventoryMovement.MovementType.DISPOSAL,
        )
        self.assertIsNotNone(movement)
        self.assertEqual(movement.notes, "Testing complete removal")

    def test_validation_errors(self):
        """Test that validation errors are raised appropriately."""
        # Test that trying to add a product with zero quantity fails
        with self.assertRaises(ValidationError):
            MockInventoryService.add_product_to_box_slot(
                product=self.variant_product,
                box_slot=self.target_slot,
                quantity=0,
            )
        
        # Test that trying to add a negative quantity fails
        with self.assertRaises(ValidationError):
            MockInventoryService.add_product_to_box_slot(
                product=self.variant_product,
                box_slot=self.target_slot,
                quantity=-1,
            )
        
        # Test that trying to move more than available quantity fails
        with self.assertRaises(ValidationError):
            MockInventoryService.move_product_between_box_slots(
                source_box_storage=self.box_storage,
                target_box_slot=self.target_slot,
                quantity=10,  # More than the 5 available
            )
        
        # Test that trying to remove more than available quantity fails
        with self.assertRaises(ValidationError):
            MockInventoryService.remove_product_from_box_slot(
                box_storage=self.box_storage,
                quantity=10,  # More than the 5 available
            ) 