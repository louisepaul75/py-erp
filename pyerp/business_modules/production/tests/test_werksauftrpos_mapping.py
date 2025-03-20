"""Tests for the WerksauftrPos to ProductionOrderItem synchronization."""

from django.test import TestCase
from unittest.mock import patch

from pyerp.business_modules.products.models import ParentProduct
from pyerp.business_modules.production.models import ProductionOrderItem
from pyerp.sync.transformers.production import ProductionOrderItemTransformer


class TestWerksauftrPosMapping(TestCase):
    """Test the mapping between WerksauftrPos and ProductionOrderItem."""

    def setUp(self):
        """Set up test data."""
        # Create a parent product with a specific legacy_base_sku
        self.parent_product = ParentProduct.objects.create(
            sku="TEST-PARENT-001",
            name="Test Parent Product",
            legacy_base_sku="TEST-ART-NR-001"
        )

    def test_art_nr_to_legacy_base_sku_mapping(self):
        """Test that WerksauftrPos['Art_Nr'] correctly maps to ParentProduct['legacy_base_sku']."""
        # Create a transformer instance
        transformer = ProductionOrderItemTransformer({})

        # Create a mock WerksauftrPos record with Art_Nr matching our parent product's legacy_base_sku
        mock_record = {
            "__KEY": "TEST-KEY-001",
            "UUID": "TEST-UUID-001",
            "W_Auftr_Nr": "TEST-ORDER-001",
            "WAP_Nr": 1,
            "Arbeitsgang": "E",
            "Art_Nr": self.parent_product.legacy_base_sku,  # Match the legacy_base_sku
            "St_Soll": 10,
            "St_Haben": 5,
            "St_Rest": 5,
            "Status": "E"
        }

        # Transform the mock record
        transformed_records = transformer.transform([mock_record])
        
        # Verify we got a transformed record
        self.assertTrue(transformed_records, "Transformation failed to produce any records")
        
        transformed = transformed_records[0]
        
        # Verify the parent_product field is set correctly in the transformed record
        self.assertIn("parent_product", transformed, 
                     "parent_product field not found in transformed record")
        
        # Verify the parent_product is the one we created
        self.assertEqual(transformed["parent_product"], self.parent_product,
                        "parent_product not correctly mapped from Art_Nr to legacy_base_sku")
        
        # Verify other fields are also correctly mapped
        self.assertEqual(transformed["product_sku"], self.parent_product.legacy_base_sku,
                        "product_sku not correctly mapped from Art_Nr")
        self.assertEqual(transformed["operation_type"], "E",
                        "operation_type not correctly mapped from Arbeitsgang")

    def test_art_nr_no_matching_parent_product(self):
        """Test behavior when no matching parent product is found."""
        # Create a transformer instance
        transformer = ProductionOrderItemTransformer({})

        # Create a mock record with Art_Nr that doesn't match any parent product
        mock_record = {
            "__KEY": "TEST-KEY-002",
            "UUID": "TEST-UUID-002",
            "W_Auftr_Nr": "TEST-ORDER-002",
            "WAP_Nr": 2,
            "Arbeitsgang": "G",
            "Art_Nr": "NONEXISTENT-SKU",  # No matching parent product
            "St_Soll": 15,
            "St_Haben": 0,
            "St_Rest": 15,
            "Status": "P"
        }

        # Transform the mock record
        transformed_records = transformer.transform([mock_record])
        
        # Verify we got a transformed record
        self.assertTrue(transformed_records, "Transformation failed to produce any records")
        
        transformed = transformed_records[0]
        
        # Verify the parent_product field is not set in the transformed record
        self.assertNotIn("parent_product", transformed, 
                        "parent_product field should not be set when no match is found")
        
        # Verify the product_sku is still set correctly
        self.assertEqual(transformed["product_sku"], "NONEXISTENT-SKU",
                        "product_sku not correctly mapped from Art_Nr") 