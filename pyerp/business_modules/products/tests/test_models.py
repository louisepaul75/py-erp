"""
Tests for the products models.
"""
import pytest
from django.test import TestCase
from django.db import connection

from pyerp.business_modules.products.models import (
    ParentProduct,
    VariantProduct,
    ProductCategory,
)


@pytest.mark.backend
@pytest.mark.unit
class ProductModelsTestCase(TestCase):
    """Test cases for product models."""

    def setUp(self):
        """Set up test data."""
        # Create test category
        self.category = ProductCategory.objects.create(
            code="TEST-CAT",
            name="Test Category",
            description="Test category description"
        )
        
        # Create parent product
        self.parent_product = ParentProduct.objects.create(
            sku="PARENT001",
            name="Test Parent Product",
            legacy_base_sku="PARENT001",
            is_active=True,
            category_id=self.category.id
        )
        
        # Create variant products
        self.variant1 = VariantProduct.objects.create(
            sku="VAR001",
            name="Test Variant 1",
            parent=self.parent_product,
            legacy_base_sku="VAR001",
            variant_code="001"
        )
        
        self.variant2 = VariantProduct.objects.create(
            sku="VAR002",
            name="Test Variant 2",
            parent=self.parent_product,
            legacy_base_sku="VAR002",
            variant_code="002"
        )

    def test_parent_product_str(self):
        """Test the string representation of ParentProduct."""
        self.assertEqual(
            str(self.parent_product),
            f"Test Parent Product (PARENT001)"
        )

    def test_variant_product_str(self):
        """Test the string representation of VariantProduct."""
        self.assertEqual(
            str(self.variant1),
            f"Test Variant 1 (001)"
        )

    def test_parent_child_relationship(self):
        """Test the parent-child relationship between products."""
        # Test parent has variants
        self.assertEqual(self.parent_product.variants.count(), 2)
        
        # Test variants have correct parent
        self.assertEqual(self.variant1.parent, self.parent_product)
        self.assertEqual(self.variant2.parent, self.parent_product)
    
    def test_active_flag(self):
        """Test the active flag on products."""
        self.assertTrue(self.parent_product.is_active)
        
        # Set parent to inactive
        self.parent_product.is_active = False
        self.parent_product.save()
        
        # Refresh from database
        self.parent_product.refresh_from_db()
        
        # Test flag was saved
        self.assertFalse(self.parent_product.is_active)

    def test_str_representation(self):
        """Test string representation of parent product."""
        self.assertEqual(str(self.parent_product), "Test Parent Product (PARENT001)")

    def test_is_active_default(self):
        """Test default value of is_active field."""
        self.assertTrue(self.parent_product.is_active)

    def test_is_new_default(self):
        """Test default value of is_new field."""
        self.assertFalse(self.parent_product.is_new) 