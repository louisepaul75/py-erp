"""
Tests for the ProductImage model.

This module tests the functionality of the ProductImage model,
ensuring that it correctly stores and relates to VariantProduct instances.
"""

import pytest
import json
from django.test import TestCase
from django.utils import timezone

from pyerp.business_modules.products.models import (
    ParentProduct,
    VariantProduct,
    ProductImage,
    ImageSyncLog,
)


@pytest.mark.backend
@pytest.mark.unit
class ProductImageTestCase(TestCase):
    """Test cases for the ProductImage model."""

    def setUp(self):
        """Set up test data."""
        # Create parent product
        self.parent = ParentProduct.objects.create(
            sku="PARENT001",
            name="Test Parent Product",
            legacy_base_sku="PARENT001",
            is_active=True
        )
        
        # Create variant product
        self.variant = VariantProduct.objects.create(
            sku="VAR001",
            name="Test Variant 1",
            parent=self.parent,
            legacy_base_sku="PARENT001",
            variant_code="001"
        )
        
        # Create product images
        self.primary_image = ProductImage.objects.create(
            product=self.variant,
            external_id="IMG001",
            image_url="https://example.com/images/full/img001.jpg",
            thumbnail_url="https://example.com/images/thumb/img001.jpg",
            image_type="Produktfoto",
            is_primary=True,
            is_front=True,
            priority=1,
            alt_text="Primary product image",
            metadata={"source": "test", "width": 1200, "height": 800}
        )
        
        self.secondary_image = ProductImage.objects.create(
            product=self.variant,
            external_id="IMG002",
            image_url="https://example.com/images/full/img002.jpg",
            thumbnail_url="https://example.com/images/thumb/img002.jpg",
            image_type="Detailfoto",
            is_primary=False,
            is_front=False,
            priority=2,
            alt_text="Secondary product image",
            metadata={"source": "test", "width": 1200, "height": 800}
        )
        
    def test_product_image_creation(self):
        """Test that ProductImage instances are created correctly."""
        # Verify primary image fields
        self.assertEqual(self.primary_image.product, self.variant)
        self.assertEqual(self.primary_image.external_id, "IMG001")
        self.assertEqual(self.primary_image.image_url, "https://example.com/images/full/img001.jpg")
        self.assertEqual(self.primary_image.thumbnail_url, "https://example.com/images/thumb/img001.jpg")
        self.assertEqual(self.primary_image.image_type, "Produktfoto")
        self.assertTrue(self.primary_image.is_primary)
        self.assertTrue(self.primary_image.is_front)
        self.assertEqual(self.primary_image.priority, 1)
        self.assertEqual(self.primary_image.alt_text, "Primary product image")
        self.assertEqual(self.primary_image.metadata, {"source": "test", "width": 1200, "height": 800})
        
        # Verify secondary image fields
        self.assertFalse(self.secondary_image.is_primary)
        self.assertFalse(self.secondary_image.is_front)
        self.assertEqual(self.secondary_image.priority, 2)
        
    def test_product_image_str_representation(self):
        """Test the string representation of ProductImage."""
        expected_str = f"Image {self.primary_image.external_id} for {self.variant.sku}"
        self.assertEqual(str(self.primary_image), expected_str)
        
    def test_product_variant_relationship(self):
        """Test the relationship between ProductImage and VariantProduct."""
        # Test that the variant has the correct images
        self.assertEqual(self.variant.images.count(), 2)
        self.assertIn(self.primary_image, self.variant.images.all())
        self.assertIn(self.secondary_image, self.variant.images.all())
        
    def test_product_image_ordering(self):
        """Test that ProductImage instances are ordered by priority."""
        images = list(self.variant.images.all())
        self.assertEqual(images[0], self.primary_image)  # Priority 1
        self.assertEqual(images[1], self.secondary_image)  # Priority 2
        
        # Change priorities and verify ordering changes
        self.primary_image.priority = 3
        self.primary_image.save()
        
        images = list(self.variant.images.all())
        self.assertEqual(images[0], self.secondary_image)  # Priority 2
        self.assertEqual(images[1], self.primary_image)  # Priority 3
        
    def test_product_image_metadata(self):
        """Test handling of JSON metadata."""
        # Test that metadata is stored and retrieved as a dictionary
        metadata = self.primary_image.metadata
        self.assertIsInstance(metadata, dict)
        self.assertEqual(metadata["source"], "test")
        self.assertEqual(metadata["width"], 1200)
        self.assertEqual(metadata["height"], 800)
        
        # Update metadata and verify changes
        new_metadata = {"source": "updated", "width": 1600, "height": 1200, "format": "jpg"}
        self.primary_image.metadata = new_metadata
        self.primary_image.save()
        
        # Refresh from database
        self.primary_image.refresh_from_db()
        
        # Verify updated metadata
        self.assertEqual(self.primary_image.metadata, new_metadata)
        
    def test_product_image_without_product(self):
        """Test creating a ProductImage without a linked product."""
        # Create image not linked to a product
        unlinked_image = ProductImage.objects.create(
            external_id="IMG003",
            image_url="https://example.com/images/full/img003.jpg",
            image_type="Produktfoto"
        )
        
        # Verify fields
        self.assertIsNone(unlinked_image.product)
        self.assertEqual(unlinked_image.external_id, "IMG003")
        
        # Test string representation
        expected_str = f"Image IMG003 (unlinked)"
        self.assertEqual(str(unlinked_image), expected_str)


@pytest.mark.backend
@pytest.mark.unit
class ImageSyncLogTestCase(TestCase):
    """Test cases for the ImageSyncLog model."""

    def setUp(self):
        """Set up test data."""
        self.sync_log = ImageSyncLog.objects.create(
            status="in_progress",
            images_added=0,
            images_updated=0,
            images_deleted=0,
            products_affected=0
        )
        
    def test_image_sync_log_creation(self):
        """Test that ImageSyncLog instances are created correctly."""
        # Verify fields
        self.assertEqual(self.sync_log.status, "in_progress")
        self.assertEqual(self.sync_log.images_added, 0)
        self.assertEqual(self.sync_log.images_updated, 0)
        self.assertEqual(self.sync_log.images_deleted, 0)
        self.assertEqual(self.sync_log.products_affected, 0)
        self.assertIsNotNone(self.sync_log.started_at)
        self.assertIsNone(self.sync_log.completed_at)
        self.assertEqual(self.sync_log.error_message, "")
        
    def test_image_sync_log_str_representation(self):
        """Test the string representation of ImageSyncLog."""
        expected_str = f"Image Sync #{self.sync_log.id} - In Progress"
        self.assertEqual(str(self.sync_log), expected_str)
        
    def test_image_sync_log_completion(self):
        """Test updating an ImageSyncLog to completed status."""
        # Update sync log
        self.sync_log.status = "completed"
        self.sync_log.completed_at = timezone.now()
        self.sync_log.images_added = 10
        self.sync_log.images_updated = 5
        self.sync_log.images_deleted = 2
        self.sync_log.products_affected = 7
        self.sync_log.save()
        
        # Refresh from database
        self.sync_log.refresh_from_db()
        
        # Verify updated fields
        self.assertEqual(self.sync_log.status, "completed")
        self.assertIsNotNone(self.sync_log.completed_at)
        self.assertEqual(self.sync_log.images_added, 10)
        self.assertEqual(self.sync_log.images_updated, 5)
        self.assertEqual(self.sync_log.images_deleted, 2)
        self.assertEqual(self.sync_log.products_affected, 7)
        
        # Test string representation after completion
        expected_str = f"Image Sync #{self.sync_log.id} - Completed"
        self.assertEqual(str(self.sync_log), expected_str)
        
    def test_image_sync_log_failure(self):
        """Test updating an ImageSyncLog to failed status."""
        # Update sync log
        error_message = "Failed to connect to image server"
        self.sync_log.status = "failed"
        self.sync_log.completed_at = timezone.now()
        self.sync_log.error_message = error_message
        self.sync_log.save()
        
        # Refresh from database
        self.sync_log.refresh_from_db()
        
        # Verify updated fields
        self.assertEqual(self.sync_log.status, "failed")
        self.assertIsNotNone(self.sync_log.completed_at)
        self.assertEqual(self.sync_log.error_message, error_message)
        
        # Test string representation after failure
        expected_str = f"Image Sync #{self.sync_log.id} - Failed"
        self.assertEqual(str(self.sync_log), expected_str) 