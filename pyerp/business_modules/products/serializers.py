"""
Serializers for the products app.
"""

from rest_framework import serializers
from django.utils.translation import gettext_lazy as _

from pyerp.business_modules.products.models import ParentProduct, ProductCategory, VariantProduct, ProductImage
from pyerp.business_modules.business.models import Supplier
import logging

logger = logging.getLogger(__name__)

# Simple serializer for Suppliers
class SupplierSerializer(serializers.ModelSerializer):
    class Meta:
        model = Supplier
        fields = ['id', 'name']

# New serializer for ParentProduct summary (used in search and supplier detail)
class ParentProductSummarySerializer(serializers.ModelSerializer):
    """Minimal serializer for ParentProduct used in listings or relationships."""
    class Meta:
        model = ParentProduct
        fields = ['id', 'sku', 'name']

# New serializer for combined product search results
class ProductSearchResultSerializer(serializers.Serializer):
    """Serializer for representing combined search results (Parent or Variant)."""
    id = serializers.IntegerField(help_text="Parent Product ID")
    sku = serializers.CharField(max_length=50, help_text="Parent Product SKU")
    name = serializers.CharField(max_length=255, help_text="Parent Product Name")
    matched_sku = serializers.CharField(
        max_length=50, 
        help_text="SKU of the matched item (Parent or Variant)"
    )
    matched_name = serializers.CharField(
        max_length=255, 
        help_text="Name of the matched item"
    )
    is_variant = serializers.BooleanField(
        help_text="True if the match was a Variant Product"
    )

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

# New Serializer for ProductImage - moved before ParentProductSerializer
class ProductImageSerializer(serializers.ModelSerializer):
    """Serializer for ProductImage model."""
    class Meta:
        model = ProductImage
        fields = [
            'id', 
            'image_url', 
            'thumbnail_url', 
            'image_type', 
            'is_primary', 
            'is_front', 
            'alt_text'
        ]

class ParentProductSerializer(serializers.ModelSerializer):
    """Serializer for the ParentProduct model."""
    legacy_base_sku = serializers.CharField(
        required=False, 
        allow_null=True, 
        allow_blank=True
    )
    # Use the simple SupplierSerializer for the related field
    supplier = SupplierSerializer(read_only=True)
    # Add primary_image field derived from variants
    primary_image = ProductImageSerializer(read_only=True)
    # Add a computed field for variants_count
    variants_count = serializers.SerializerMethodField()

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
            "supplier",
            "primary_image",
            "variants_count",
        ]
        # Add sku to read_only_fields
        read_only_fields = ["sku"]
    
    def get_variants_count(self, obj):
        """Calculate the number of variants for the parent product."""
        # Check if the related manager exists before counting
        if hasattr(obj, 'variants'):
            return obj.variants.count()
        return 0 # Return 0 if 'variants' related manager doesn't exist
    
    def to_representation(self, instance):
        """Override to include primary_image derived from variants."""
        ret = super().to_representation(instance)
        
        # Debug output for legacy_base_sku remains
        legacy_base_sku = getattr(instance, 'legacy_base_sku', None)
        logger.debug(
            f"ParentProduct {instance.sku} legacy_base_sku: '{legacy_base_sku}' "
            f"(type: {type(legacy_base_sku).__name__})"
        )
        if legacy_base_sku is not None:
            ret['legacy_base_sku'] = str(legacy_base_sku)

        # --- Start: Logic to find primary_image from variants ---
        primary_image_obj = None
        variants = instance.variants.prefetch_related('images').all()

        # 1. Prioritize 'BE' variant's primary/front/Produktfoto image
        be_variant = next((v for v in variants if v.variant_code == 'BE'), None)
        if be_variant and be_variant.images.exists():
            # Try finding primary, front, Produktfoto
            primary_image_obj = be_variant.images.filter(
                is_primary=True, 
                is_front=True, 
                image_type__iexact="Produktfoto"
            ).first()
            if not primary_image_obj:
                # Try finding primary, Produktfoto
                primary_image_obj = be_variant.images.filter(
                    is_primary=True, 
                    image_type__iexact="Produktfoto"
                ).first()
            if not primary_image_obj:
                # Try finding front, Produktfoto
                primary_image_obj = be_variant.images.filter(
                    is_front=True, 
                    image_type__iexact="Produktfoto"
                ).first()
            if not primary_image_obj:
                # Try finding any Produktfoto
                primary_image_obj = be_variant.images.filter(
                    image_type__iexact="Produktfoto"
                ).first()
            if not primary_image_obj:
                # Try finding primary
                primary_image_obj = be_variant.images.filter(
                    is_primary=True
                ).first()
            if not primary_image_obj:
                # Fallback to first image of BE variant
                primary_image_obj = be_variant.images.first()

        # 2. Fallback: Any variant's primary/front/Produktfoto image
        if not primary_image_obj:
            for variant in variants:
                if variant.images.exists():
                    img = variant.images.filter(
                        is_primary=True, 
                        is_front=True, 
                        image_type__iexact="Produktfoto"
                    ).first()
                    if not img:
                        img = variant.images.filter(
                            is_primary=True, 
                            image_type__iexact="Produktfoto"
                        ).first()
                    if not img:
                        img = variant.images.filter(
                            is_front=True, 
                            image_type__iexact="Produktfoto"
                        ).first()
                    if not img:
                        img = variant.images.filter(
                            image_type__iexact="Produktfoto"
                        ).first()
                    if not img:
                        img = variant.images.filter(is_primary=True).first()
                        
                    if img:
                        primary_image_obj = img
                        break  # Found one, stop searching

        # 3. Fallback: First image of the first variant that has images
        if not primary_image_obj:
            for variant in variants:
                if variant.images.exists():
                    primary_image_obj = variant.images.first()
                    if primary_image_obj:
                        break  # Found one, stop searching

        # Serialize the found image or set to None
        if primary_image_obj:
            ret['primary_image'] = ProductImageSerializer(primary_image_obj).data
        else:
            ret['primary_image'] = None
        # --- End: Logic to find primary_image from variants ---
        
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
    images = ProductImageSerializer(many=True, read_only=True)

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
            "images",
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