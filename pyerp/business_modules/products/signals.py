"""
Signal handlers for the products app.
"""

from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.utils import timezone

from pyerp.business_modules.products.models import VariantProduct
from pyerp.utils.logging import get_logger

logger = get_logger(__name__)


@receiver(pre_save, sender=VariantProduct)
def variant_product_pre_save(_sender=None, instance=None, **_kwargs):
    """
    Handle pre-save operations for VariantProduct model.

    - Ensure sku is properly formatted if not provided
    - Set timestamps appropriately
    """
    if instance.parent and instance.variant_code and not instance.sku:
        # Only set SKU if parent has a valid identifier
        if instance.parent.sku or instance.parent.legacy_id:
            parent_sku = instance.parent.sku or str(instance.parent.legacy_id)
            instance.sku = f"{parent_sku}-{instance.variant_code}"
        else:
            # If parent has no identifier, leave SKU empty
            instance.sku = ""

    # Handle timestamp logic (equivalent to auto_now and auto_now_add)
    if not instance.pk:  # New instance
        if not instance.created_at:
            instance.created_at = timezone.now()

    # Always update the updated_at timestamp (equivalent to auto_now)
    instance.updated_at = timezone.now()
