"""
Services for inventory and warehouse management business logic.

This module contains service classes that implement the business logic
for inventory operations such as moving boxes, placing products in boxes,
and managing inventory movements.
"""

import logging
from datetime import datetime
from django.db import transaction
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError

from .models import (
    Box, 
    BoxSlot, 
    BoxStorage, 
    ProductStorage, 
    InventoryMovement,
    StorageLocation
)

logger = logging.getLogger(__name__)


class InventoryService:
    """Service for inventory management operations."""

    @classmethod
    @transaction.atomic
    def move_box(cls, box, target_storage_location, user=None):
        """
        Move a box to a new storage location.
        
        Args:
            box (Box): The box to move
            target_storage_location (StorageLocation): The destination storage location
            user (User, optional): The user performing the action for audit purposes

        Returns:
            Box: The updated box

        Raises:
            ValidationError: If the move cannot be completed
        """
        if not box or not target_storage_location:
            raise ValidationError(_("Box and target location are required"))

        # Check if the target location has available capacity
        if target_storage_location.capacity is not None:
            boxes_in_location = Box.objects.filter(
                storage_location=target_storage_location
            ).count()
            
            if boxes_in_location >= target_storage_location.capacity:
                raise ValidationError(
                    _("Target location has reached capacity limit")
                )

        # Create a log of the move
        previous_location = box.storage_location
        
        # Update the box's storage location
        box.storage_location = target_storage_location
        box.modified_at = datetime.now()
        box.save()

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
                    created_by=user.username if user else None,
                )

        logger.info(
            f"Box {box.code} moved from {previous_location} to {target_storage_location}"
        )
        return box

    @classmethod
    @transaction.atomic
    def add_product_to_box_slot(
        cls, product, box_slot, quantity, batch_number=None, expiry_date=None, user=None
    ):
        """
        Add a product to a box slot.
        
        Args:
            product (VariantProduct): The product to add
            box_slot (BoxSlot): The box slot to add the product to
            quantity (int): The quantity to add
            batch_number (str, optional): Batch/lot number for the product
            expiry_date (date, optional): Expiry date for the product
            user (User, optional): The user performing the action for audit purposes

        Returns:
            BoxStorage: The created box storage record

        Raises:
            ValidationError: If the operation cannot be completed
        """
        if not product or not box_slot or quantity <= 0:
            raise ValidationError(_("Valid product, box slot, and positive quantity are required"))

        # Check if the slot has available space
        if box_slot.max_products is not None:
            current_count = box_slot.product_count
            if current_count + quantity > box_slot.max_products:
                raise ValidationError(
                    _("Adding {quantity} items would exceed the slot capacity of {max_products}")
                    .format(quantity=quantity, max_products=box_slot.max_products)
                )

        # Get or create ProductStorage record for this product and location
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
            date_stored=datetime.now(),
            created_by=user.username if user else None,
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
            created_by=user.username if user else None,
        )

        logger.info(
            f"Added {quantity} of product {product} to box slot {box_slot}"
        )
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
            raise ValidationError(_("Valid source, target, and positive quantity are required"))
            
        if quantity > source_box_storage.quantity:
            raise ValidationError(_("Cannot move more than available quantity"))
            
        # Check if target slot has capacity
        if target_box_slot.max_products is not None:
            if not target_box_slot.available_space >= quantity:
                raise ValidationError(_("Target slot does not have enough capacity"))
        
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
                "created_by": user.username if user else None,
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
            created_by=user.username if user else None,
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
            raise ValidationError(_("Valid box storage and positive quantity are required"))
            
        if quantity > box_storage.quantity:
            raise ValidationError(_("Cannot remove more than available quantity"))
            
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
            created_by=user.username if user else None,
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