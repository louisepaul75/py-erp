"""
Serializers for the products app.
"""

from rest_framework import serializers

from pyerp.business_modules.products.models import ParentProduct, ProductCategory
import logging

logger = logging.getLogger(__name__)

class ProductCategorySerializer(serializers.ModelSerializer):
    """
    Serializer for the ProductCategory model with drf-spectacular documentation.
    """
    
    class Meta:
        model = ProductCategory
        fields = ['id', 'code', 'name', 'description', 'parent']
        
    def to_representation(self, instance):
        """Customize the representation to handle parent as a simple ID."""
        ret = super().to_representation(instance)
        # Get the parent's ID if parent exists, otherwise return None
        if instance.parent:
            ret['parent'] = instance.parent.id
        return ret


class ParentProductSerializer(serializers.ModelSerializer):
    """Serializer for the ParentProduct model."""
    legacy_base_sku = serializers.CharField(required=False, allow_null=True, allow_blank=True)

    class Meta:
        model = ParentProduct
        fields = [
            "id",
            "sku",
            "name",
            "description",
            "is_active",
            "is_new",
            "weight",
            "length_mm",
            "width_mm",
            "height_mm",
            "is_one_sided",
            "is_hanging",
            "legacy_base_sku",
            "legacy_id",
        ]
    
    def to_representation(self, instance):
        """Override to debug legacy_base_sku field."""
        ret = super().to_representation(instance)
        # Debug output to understand the issue
        legacy_base_sku = getattr(instance, 'legacy_base_sku', None)
        logger.debug(f"ParentProduct {instance.sku} legacy_base_sku: '{legacy_base_sku}' (type: {type(legacy_base_sku).__name__})")
        
        # Force legacy_base_sku to be string if it exists
        if legacy_base_sku is not None:
            ret['legacy_base_sku'] = str(legacy_base_sku)
        
        return ret 