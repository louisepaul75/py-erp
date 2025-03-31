"""
Tests for the VariantProduct tag inheritance methods.

This module tests the tag inheritance functionality of VariantProduct models,
ensuring that tag inheritance works correctly between parent and variant products.
"""

import pytest
from django.test import TestCase
from django.contrib.contenttypes.models import ContentType

from pyerp.core.models import Tag, TaggedItem
from pyerp.business_modules.products.models import ParentProduct, VariantProduct
from pyerp.business_modules.products.tag_models import M2MOverride, FieldOverride


@pytest.mark.backend
@pytest.mark.unit
class VariantProductTagMethodsTestCase(TestCase):
    """Test the tag inheritance methods of VariantProduct."""

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
        
        # Create tags
        self.tag1 = Tag.objects.create(name="Tag 1")
        self.tag2 = Tag.objects.create(name="Tag 2")
        self.tag3 = Tag.objects.create(name="Tag 3")
        
        # Add tags to parent
        content_type = ContentType.objects.get_for_model(self.parent)
        TaggedItem.objects.create(
            tag=self.tag1,
            content_type=content_type,
            object_id=self.parent.pk
        )
        TaggedItem.objects.create(
            tag=self.tag2,
            content_type=content_type,
            object_id=self.parent.pk
        )
        
    def test_get_tag_override_creates_new(self):
        """Test that get_tag_override creates a new override if it doesn't exist."""
        # Ensure no override exists yet
        content_type = ContentType.objects.get_for_model(self.variant)
        M2MOverride.objects.filter(
            content_type=content_type,
            object_id=self.variant.id,
            relationship_name='tags'
        ).delete()
        
        # Call the method
        override = self.variant.get_tag_override()
        
        # Verify the override was created
        self.assertIsNotNone(override)
        self.assertEqual(override.content_type, content_type)
        self.assertEqual(override.object_id, self.variant.id)
        self.assertEqual(override.relationship_name, 'tags')
        self.assertTrue(override.inherit)  # Default should be True
        
    def test_get_tag_override_returns_existing(self):
        """Test that get_tag_override returns existing override."""
        # Create an override with inherit=False
        content_type = ContentType.objects.get_for_model(self.variant)
        existing_override = M2MOverride.objects.create(
            content_type=content_type,
            object_id=self.variant.id,
            relationship_name='tags',
            inherit=False
        )
        
        # Call the method
        override = self.variant.get_tag_override()
        
        # Verify the same override was returned
        self.assertEqual(override.id, existing_override.id)
        self.assertFalse(override.inherit)  # Should retain False value
        
    def test_inherits_tags_with_no_parent(self):
        """Test inherits_tags when the variant has no parent."""
        # Set variant's parent to None
        variant_no_parent = VariantProduct.objects.create(
            sku="VAR002",
            name="Test Variant 2",
            parent=None,
            legacy_base_sku="VAR002",
            variant_code="002"
        )
        
        # Check that inherits_tags returns False
        self.assertFalse(variant_no_parent.inherits_tags())
        
    def test_inherits_tags_with_override_true(self):
        """Test inherits_tags when the override has inherit=True."""
        # Create override with inherit=True
        content_type = ContentType.objects.get_for_model(self.variant)
        M2MOverride.objects.create(
            content_type=content_type,
            object_id=self.variant.id,
            relationship_name='tags',
            inherit=True
        )
        
        # Check that inherits_tags returns True
        self.assertTrue(self.variant.inherits_tags())
        
    def test_inherits_tags_with_override_false(self):
        """Test inherits_tags when the override has inherit=False."""
        # Create override with inherit=False
        content_type = ContentType.objects.get_for_model(self.variant)
        M2MOverride.objects.create(
            content_type=content_type,
            object_id=self.variant.id,
            relationship_name='tags',
            inherit=False
        )
        
        # Check that inherits_tags returns False
        self.assertFalse(self.variant.inherits_tags())
        
    def test_set_tags_inheritance_true(self):
        """Test set_tags_inheritance with inherit=True."""
        # Set inheritance to True
        self.variant.set_tags_inheritance(True)
        
        # Check that the override has inherit=True
        override = self.variant.get_tag_override()
        self.assertTrue(override.inherit)
        
    def test_set_tags_inheritance_false(self):
        """Test set_tags_inheritance with inherit=False."""
        # Set inheritance to False
        self.variant.set_tags_inheritance(False)
        
        # Check that the override has inherit=False
        override = self.variant.get_tag_override()
        self.assertFalse(override.inherit)
        
    def test_get_all_tags_with_inheritance_enabled(self):
        """Test get_all_tags when inheritance is enabled."""
        # Ensure inheritance is enabled
        self.variant.set_tags_inheritance(True)
        
        # Add a tag to the variant
        content_type = ContentType.objects.get_for_model(self.variant)
        TaggedItem.objects.create(
            tag=self.tag3,
            content_type=content_type,
            object_id=self.variant.pk
        )
        
        # Get all tags
        all_tags = self.variant.get_all_tags()
        
        # Should contain all 3 tags (2 from parent, 1 from variant)
        self.assertEqual(len(all_tags), 3)
        tag_ids = [tag.id for tag in all_tags]
        self.assertIn(self.tag1.id, tag_ids)
        self.assertIn(self.tag2.id, tag_ids)
        self.assertIn(self.tag3.id, tag_ids)
        
    def test_get_all_tags_with_inheritance_disabled(self):
        """Test get_all_tags when inheritance is disabled."""
        # Disable inheritance
        self.variant.set_tags_inheritance(False)
        
        # Add a tag to the variant
        content_type = ContentType.objects.get_for_model(self.variant)
        TaggedItem.objects.create(
            tag=self.tag3,
            content_type=content_type,
            object_id=self.variant.pk
        )
        
        # Get all tags
        all_tags = self.variant.get_all_tags()
        
        # Should contain only 1 tag (from variant)
        self.assertEqual(len(all_tags), 1)
        self.assertEqual(all_tags[0].id, self.tag3.id)
        
    def test_get_all_tags_with_no_parent(self):
        """Test get_all_tags when the variant has no parent."""
        # Create variant with no parent
        variant_no_parent = VariantProduct.objects.create(
            sku="VAR003",
            name="Test Variant 3",
            parent=None,
            legacy_base_sku="VAR003",
            variant_code="003"
        )
        
        # Add a tag to the variant
        content_type = ContentType.objects.get_for_model(variant_no_parent)
        TaggedItem.objects.create(
            tag=self.tag3,
            content_type=content_type,
            object_id=variant_no_parent.pk
        )
        
        # Get all tags
        all_tags = variant_no_parent.get_all_tags()
        
        # Should contain only 1 tag (from variant)
        self.assertEqual(len(all_tags), 1)
        self.assertEqual(all_tags[0].id, self.tag3.id) 