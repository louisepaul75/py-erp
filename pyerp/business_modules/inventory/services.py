"""
Service classes for inventory and warehouse management business logic.

This module contains service classes that implement the business logic
for inventory operations such as moving boxes, placing products in boxes,
and managing inventory movements.
"""

import logging
from datetime import datetime
from django.db import transaction
from django.core.exceptions import ValidationError
from django.db import models

from pyerp.business_modules.inventory.models import Box, BoxSlot, BoxStorage, InventoryMovement, ProductStorage
from pyerp.business_modules.products.models import VariantProduct

logger = logging.getLogger(__name__)


class InventoryService:
    """Service for inventory management operations."""

    @staticmethod
    def move_box(box, target_storage_location, user=None):
        """
        Move a box to a new storage location.

        Args:
            box: The box to move
            target_storage_location: The target storage location
            user: The user performing the action (optional)

        Raises:
            PermissionError: If the user lacks permission to move the box
            ValidationError: If validation fails
        """
        if user and not user.has_perm('inventory.change_box'):
            raise PermissionError("User does not have permission to move boxes")

        if not box or not target_storage_location:
            raise ValidationError("Box and target location are required")

        if (target_storage_location.capacity_limit and
            Box.objects.filter(storage_location=target_storage_location).count() >= target_storage_location.capacity_limit):
            raise ValidationError("Target location has reached capacity limit")

        # Store the old location for logging
        old_location = box.storage_location

        # Update box's storage location
        box.storage_location = target_storage_location
        box.save()

        # Log the movement
        logger.info(f"Box {box.code} moved from {old_location} to {target_storage_location}")

        return box

    @staticmethod
    def add_product_to_box_slot(product, box_slot, quantity, user=None, batch_number=None, expiry_date=None):
        """
        Add a product to a box slot.

        Args:
            product: The product to add
            box_slot: The box slot to add the product to
            quantity: The quantity to add
            user: The user performing the action (optional)
            batch_number: The batch number for the product (optional)
            expiry_date: The expiry date for the product (optional)

        Raises:
            PermissionError: If the user lacks permission
            ValidationError: If validation fails
        """
        if user and not user.has_perm('inventory.change_boxstorage'):
            raise PermissionError("User does not have permission to modify box storage")

        if not product or not box_slot or quantity <= 0:
            raise ValidationError("Valid product, box slot, and positive quantity are required")

        current_quantity = BoxStorage.objects.filter(box_slot=box_slot).aggregate(
            total=models.Sum('quantity'))['total'] or 0

        if box_slot.capacity and current_quantity + quantity > box_slot.capacity:
            raise ValidationError("Adding this quantity would exceed the slot's capacity")

        # Create or update the product storage
        product_storage, _ = ProductStorage.objects.get_or_create(
            product=product,
            storage_location=box_slot.box.storage_location,
            defaults={'quantity': 0}
        )

        # Create or update the box storage
        box_storage, _ = BoxStorage.objects.get_or_create(
            product_storage=product_storage,
            box_slot=box_slot,
            batch_number=batch_number,
            expiry_date=expiry_date,
            created_by=user,
            defaults={'quantity': 0}
        )

        # Update quantities
        box_storage.quantity += quantity
        box_storage.save()

        product_storage.quantity += quantity
        product_storage.save()

        # Log the addition
        logger.info(f"Added {quantity} of product {product.name} to box slot {box_slot.slot_code}")

        return box_storage

    @classmethod
    @transaction.atomic
    def move_product_between_box_slots(
        cls, source_box_storage, target_box_slot, quantity, user=None
    ):
        """
        Move products from one box slot to another.
        
        Args:
            source_box_storage (BoxStorage): The source box storage record
            target_box_slot (BoxSlot): The target box slot
            quantity (int): The quantity to move
            user (User, optional): The user performing the action for audit purposes

        Returns:
            tuple: (updated_source_box_storage, new_target_box_storage)

        Raises:
            ValidationError: If the move cannot be completed
        """
        if not source_box_storage or not target_box_slot or quantity <= 0:
            raise ValidationError("Valid source, target, and positive quantity are required")
            
        if quantity > source_box_storage.quantity:
            raise ValidationError("Cannot move more than available quantity")
            
        # Check if target slot has capacity
        if target_box_slot.max_products is not None:
            if not target_box_slot.available_space >= quantity:
                raise ValidationError("Target slot does not have enough capacity")
        
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
                "date_stored": datetime.now(),
                "created_by": user if user else None,
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
            reference=f"Transfer between boxes",
            notes=f"Moved {quantity} units from {source_slot} to {target_box_slot}",
        )
        
        logger.info(
            f"Moved {quantity} of product {product} from {source_slot} to {target_box_slot}"
        )
        return (updated_source, target_box_storage)

    @classmethod
    @transaction.atomic
    def remove_product_from_box_slot(cls, box_storage, quantity, reason=None, user=None):
        """
        Remove a product from a box slot.
        
        Args:
            box_storage (BoxStorage): The box storage record
            quantity (int): The quantity to remove
            reason (str, optional): Reason for removal
            user (User, optional): The user performing the action for audit purposes

        Returns:
            BoxStorage: The updated box storage record (or None if fully removed)

        Raises:
            ValidationError: If the removal cannot be completed
        """
        if not box_storage or quantity <= 0:
            raise ValidationError("Valid box storage and positive quantity are required")
            
        if quantity > box_storage.quantity:
            raise ValidationError("Cannot remove more than available quantity")
            
        box_slot = box_storage.box_slot
        product = box_storage.product_storage.product
        
        # Update quantities
        box_storage.quantity -= quantity
        box_storage.product_storage.quantity -= quantity
        box_storage.product_storage.save()
        
        # Determine movement type based on reason
        movement_type = InventoryMovement.MovementType.PICK
        if reason == "disposal":
            movement_type = InventoryMovement.MovementType.DISPOSAL
        elif reason == "adjustment":
            movement_type = InventoryMovement.MovementType.ADJUSTMENT
            
        # Log the inventory movement
        InventoryMovement.objects.create(
            product=product,
            from_slot=box_slot,
            quantity=quantity,
            movement_type=movement_type,
            reference=reason or "Product removal",
            notes=f"Removed {quantity} units from {box_slot}",
        )
        
        # Handle complete removal
        if box_storage.quantity == 0:
            box_storage.delete()
            box_slot.update_occupied_status()
            logger.info(
                f"Completely removed product {product} from {box_slot}"
            )
            return None
        else:
            box_storage.save()
            logger.info(
                f"Removed {quantity} of product {product} from {box_slot}, {box_storage.quantity} remaining"
            )
            return box_storage 