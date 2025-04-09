"""
Serializers for the products app.
"""

from rest_framework import serializers
from django.utils.translation import gettext_lazy as _

from pyerp.business_modules.products.models import ParentProduct, ProductCategory, VariantProduct
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
        # Add sku to read_only_fields
        read_only_fields = ["sku"]
    
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

class VariantProductSerializer(serializers.ModelSerializer):
    """Serializer for the VariantProduct model."""
    parent_id = serializers.PrimaryKeyRelatedField(
        queryset=ParentProduct.objects.all(),
        source='parent',
        write_only=True,
        help_text=_("ID of the parent product.")
    )
    parent = ParentProductSerializer(read_only=True)

    class Meta:
        model = VariantProduct
        fields = [
            "id",
            "sku",
            "name",
            "variant_code",
            "description",
            "is_active",
            "parent_id",
            "parent",
            "retail_price",
            "wholesale_price",
            "retail_unit",
            "wholesale_unit",
            "color",
            "width_mm",
            "is_featured",
            "is_new",
            "is_bestseller",
            "legacy_sku",
            "legacy_base_sku",
        ]
        read_only_fields = ["sku"]

    def to_representation(self, instance):
        """Customize representation to include nested parent details."""
        representation = super().to_representation(instance)
        # Ensure parent details are included in the representation
        if instance.parent:
            representation['parent'] = ParentProductSerializer(instance.parent).data
        else:
            representation['parent'] = None
        return representation 