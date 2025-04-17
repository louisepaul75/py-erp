from django.db import models
from django.db.models import F, Sum, Case, When, Value, BooleanField
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import SalesRecord, SalesRecordItem

# Constants for delivery status choices
PENDING_DELIVERY = "PENDING"
PARTIALLY_DELIVERED = "PARTIALLY_DELIVERED"
FULLY_DELIVERED = "FULLY_DELIVERED"
# We might not automatically set CANCELLED based on items alone
# CANCELLED = "CANCELLED"


@receiver([post_save, post_delete], sender=SalesRecordItem)
def update_delivery_status(sender, instance, **kwargs):
    """
    Updates the delivery_status of the related SalesRecord based on its items.
    """
    sales_record = instance.sales_record

    # Avoid processing if the parent record no longer exists
    # (e.g., cascade delete)
    try:
        # Refresh from DB to ensure we have the latest state if needed,
        # although accessing instance.sales_record should be sufficient here.
        sales_record.refresh_from_db()
    except SalesRecord.DoesNotExist:
        return # Parent record deleted, nothing to update

    # Aggregate status directly from the database for efficiency
    # Consider only items that are not 'cancelled' for delivery status calculation
    # NOTE: Adjust the filter if SalesRecordItem has its own status like 'CANCELLED'
    # that should exclude it from delivery calculations. Currently using `fulfillment_status`.
    # Assuming FULFILLMENT_STATUS_CHOICES = [('PENDING', ...), ('PARTIAL', ...), ('FULFILLED', ...), ('CANCELLED', ...)]

    aggregation = sales_record.line_items.exclude(
        fulfillment_status='CANCELLED' # Exclude cancelled items from calculation
    ).aggregate(
        total_quantity=Sum('quantity'),
        total_fulfilled=Sum('fulfilled_quantity'),
        # Check if *any* item is partially fulfilled (fulfilled > 0 and < quantity)
        any_partial=Sum(
            Case(
                When(fulfilled_quantity__gt=0, fulfilled_quantity__lt=F('quantity'), then=1),
                default=0,
                output_field=models.IntegerField()
            )
        ),
        # Check if *all* items are pending (fulfilled = 0)
        all_pending=Sum(
            Case(
                When(fulfilled_quantity=0, then=0), # If pending, it's not 'not pending'
                default=1, # If not pending (i.e. > 0), count it
                output_field=models.IntegerField()
            )
        ),
         # Check if *all* items are fully fulfilled (fulfilled >= quantity)
        all_fulfilled=Sum(
            Case(
                When(fulfilled_quantity__gte=F('quantity'), then=0), # If fulfilled, it's not 'not fulfilled'
                default=1, # If not fulfilled, count it
                output_field=models.IntegerField()
            )
        ),
        item_count=models.Count('id') # Count items considered
    )

    new_status = PENDING_DELIVERY # Default status

    if aggregation['item_count'] == 0:
        # No relevant items (all might be cancelled or none exist)
        # Default to PENDING, or potentially CANCELLED if record is cancelled?
        # For now, stick to PENDING if no items dictate otherwise.
        new_status = PENDING_DELIVERY
    elif aggregation['all_fulfilled'] == 0:
        # All items considered are fully fulfilled
        new_status = FULLY_DELIVERED
    elif aggregation['any_partial'] > 0 or aggregation['all_pending'] > 0:
         # If any item is partially delivered OR
         # if not all items are pending (meaning at least one has some fulfillment)
         # and not all items are fully fulfilled
        new_status = PARTIALLY_DELIVERED
    elif aggregation['all_pending'] == 0:
         # All items considered have zero fulfillment
         new_status = PENDING_DELIVERY
    # else: # Should cover all cases, defaults to PENDING_DELIVERY initially set

    # Update the SalesRecord only if the status has changed
    if sales_record.delivery_status != new_status:
        SalesRecord.objects.filter(pk=sales_record.pk).update(delivery_status=new_status)
        # Using .update() avoids triggering save() method and potentially
        # other signals attached to SalesRecord.

    return new_status 