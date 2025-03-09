from unittest.mock import patch, MagicMock
from datetime import datetime

from django.test import TestCase

from pyerp.business_modules.products.models import VariantProduct
from pyerp.business_modules.products.signals import variant_product_pre_save


class TestVariantProductSignals(TestCase):
    """Tests for variant product signal handlers"""

    def setUp(self):
        """Set up the test environment"""
        self.parent_product = MagicMock()
        self.parent_product.sku = "PARENT-SKU"
        self.parent_product.legacy_id = 12345

        self.variant = VariantProduct()
        self.variant.parent = self.parent_product
        self.variant.variant_code = "V1"
        self.variant.sku = ""
        self.variant.created_at = None
        self.variant.updated_at = None
        self.variant.pk = None  # Simulate new instance

    def test_variant_product_pre_save_sets_sku(self):
        """Test pre_save handler sets SKU with parent and variant code"""
        # Call the signal handler
        variant_product_pre_save(instance=self.variant)

        # Verify SKU was set correctly
        self.assertEqual(self.variant.sku, "PARENT-SKU-V1")

    def test_variant_product_pre_save_with_parent_sku_none(self):
        """Test when parent.sku is None, uses legacy_id for SKU generation"""
        # Set parent.sku to None
        self.parent_product.sku = None

        # Call the signal handler
        variant_product_pre_save(instance=self.variant)

        # Verify SKU was set using legacy_id
        self.assertEqual(self.variant.sku, "12345-V1")

    def test_variant_product_pre_save_with_existing_sku(self):
        """Test that pre_save handler doesn't overwrite an existing SKU"""
        # Set an existing SKU
        self.variant.sku = "EXISTING-SKU"

        # Call the signal handler
        variant_product_pre_save(instance=self.variant)

        # Verify SKU wasn't changed
        self.assertEqual(self.variant.sku, "EXISTING-SKU")

    @patch('pyerp.business_modules.products.signals.timezone')
    def test_variant_product_pre_save_sets_timestamps(self, mock_timezone):
        """Test that pre_save handler sets timestamps for new instances"""
        # Set up mock timezone
        now = datetime(2023, 1, 1, 12, 0, 0)
        mock_timezone.now.return_value = now

        # Call the signal handler
        variant_product_pre_save(instance=self.variant)

        # Verify timestamps were set
        self.assertEqual(self.variant.created_at, now)
        self.assertEqual(self.variant.updated_at, now)

    @patch('pyerp.business_modules.products.signals.timezone')
    def test_variant_product_pre_save_existing_instance(self, mock_timezone):
        """Test updating only updated_at for existing instances"""
        # Set up mock timezone
        now = datetime(2023, 1, 1, 12, 0, 0)
        mock_timezone.now.return_value = now

        # Set up an existing instance (has a pk)
        self.variant.pk = 123
        created_at = datetime(2022, 1, 1, 12, 0, 0)
        self.variant.created_at = created_at

        # Call the signal handler
        variant_product_pre_save(instance=self.variant)

        # Verify only updated_at was changed
        self.assertEqual(self.variant.created_at, created_at)  # Unchanged
        self.assertEqual(self.variant.updated_at, now)  # Updated 