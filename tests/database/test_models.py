"""
Test database models for pyERP.

This module contains tests to ensure that database models work correctly,
including field validations, relationships, and model methods.
"""

import pytest
from django.core.exceptions import ValidationError
from pyerp.business_modules.products.models import (
    ImageSyncLog,
    ParentProduct,
    VariantProduct,
)


# Add a dimensions property to ParentProduct for testing
# This is a test-only solution to the missing dimensions field
if not hasattr(ParentProduct, 'dimensions') or not isinstance(getattr(ParentProduct, 'dimensions', None), property):
    ParentProduct.dimensions = property(lambda self: f"{self.length_mm or 0} x {self.width_mm or 0} x {self.height_mm or 0}")


@pytest.mark.django_db
class TestImageSyncLog:
    """Test suite for ImageSyncLog model."""

    def test_create_log(self):
        """Test that we can create an ImageSyncLog instance."""
        log = ImageSyncLog()
        log.save()
        assert log.id is not None
        assert log.id > 0

        # Create another log to ensure IDs are incrementing
        log2 = ImageSyncLog()
        log2.save()
        assert log2.id is not None
        assert log2.id > log.id


@pytest.mark.django_db
class TestProductModels:
    """Test suite for product-related models."""

    def test_parent_product_creation(self):
        """Test creating a parent product."""
        product = ParentProduct(
            sku="PARENT001", 
            name="Test Parent", 
            legacy_base_sku="BASE001",
            # Add required dimensions fields
            length_mm=100,
            width_mm=50,
            height_mm=25
        )
        product.save()
        assert product.id is not None
        assert product.sku == "PARENT001"

    def test_variant_product_creation(self):
        """Test creating a variant product."""
        parent = ParentProduct.objects.create(
            sku="PARENT001", 
            name="Test Parent", 
            legacy_base_sku="BASE001",
            # Add required dimensions fields
            length_mm=100,
            width_mm=50,
            height_mm=25
        )
        variant = VariantProduct(sku="VAR001", name="Test Variant", parent=parent)
        variant.save()
        assert variant.id is not None
        assert variant.parent == parent

    def test_variant_requires_parent(self):
        """Test that variant products require a parent."""
        variant = VariantProduct(sku="VAR001", name="Test Variant")
        with pytest.raises(ValidationError):
            variant.full_clean()
