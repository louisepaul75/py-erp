"""
Test database models for pyERP.

This module contains tests to ensure that database models work correctly,
including field validations, relationships, and model methods.
"""

import pytest
from django.core.exceptions import ValidationError
from django.db import connection
from pyerp.products.models import ImageSyncLog, ParentProduct, VariantProduct


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
            base_sku="BASE001"
        )
        product.save()
        assert product.id is not None
        assert product.sku == "PARENT001"

    def test_variant_product_creation(self):
        """Test creating a variant product."""
        parent = ParentProduct.objects.create(
            sku="PARENT001",
            name="Test Parent",
            base_sku="BASE001"
        )
        variant = VariantProduct(
            sku="VAR001",
            name="Test Variant",
            parent=parent
        )
        variant.save()
        assert variant.id is not None
        assert variant.parent == parent

    def test_variant_requires_parent(self):
        """Test that variant products require a parent."""
        variant = VariantProduct(
            sku="VAR001",
            name="Test Variant"
        )
        with pytest.raises(ValidationError):
            variant.full_clean() 