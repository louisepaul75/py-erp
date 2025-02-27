"""
Signal handlers for the products app.
"""

import logging
from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver

from pyerp.products.models import Product, ProductImage

logger = logging.getLogger(__name__)


@receiver(pre_save, sender=Product)
def product_pre_save(sender, instance, **kwargs):
    """
    Handle pre-save operations for Product model.
    
    - Ensure base_sku and variant_code are set based on sku if not provided
    """
    if instance.sku and not instance.base_sku:
        # If SKU contains a hyphen, split it to get base_sku and variant_code
        if '-' in instance.sku:
            parts = instance.sku.split('-', 1)
            instance.base_sku = parts[0]
            if not instance.variant_code:
                instance.variant_code = parts[1]
        else:
            # If no hyphen, the entire SKU is the base_sku
            instance.base_sku = instance.sku


@receiver(post_save, sender=ProductImage)
def product_image_post_save(sender, instance, created, **kwargs):
    """
    Handle post-save operations for ProductImage model.
    
    - If this image is marked as primary, ensure no other images for the same product are primary
    """
    if instance.is_primary:
        # Get all other images for this product and set is_primary to False
        ProductImage.objects.filter(
            product=instance.product
        ).exclude(
            id=instance.id
        ).update(
            is_primary=False
        ) 