"""
Serializers for the products app.
"""

from rest_framework import serializers

from pyerp.business_modules.products.models import ParentProduct


class ParentProductSerializer(serializers.ModelSerializer):
    """Serializer for the ParentProduct model."""

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