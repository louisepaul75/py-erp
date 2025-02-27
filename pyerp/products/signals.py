"""
Signal handlers for the products app.
"""

import logging
from django.db.models.signals import pre_save
from django.dispatch import receiver

from pyerp.products.models import ParentProduct, VariantProduct

logger = logging.getLogger(__name__)


@receiver(pre_save, sender=VariantProduct)
def variant_product_pre_save(sender, instance, **kwargs):
    """
    Handle pre-save operations for VariantProduct model.
    
    - Ensure sku is properly formatted if not provided
    """
    if instance.parent and instance.variant_code and not instance.sku:
        # Generate SKU from parent SKU and variant code
        parent_sku = instance.parent.sku or str(instance.parent.legacy_id)
        instance.sku = f"{parent_sku}-{instance.variant_code}" 