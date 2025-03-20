"""
Tests for the product tags inheritance system.
"""

from django.test import TestCase
from django.contrib.contenttypes.models import ContentType

from pyerp.business_modules.products.models import ParentProduct, VariantProduct
from pyerp.business_modules.products.tag_models import Tag, M2MOverride


class TagInheritanceTestCase(TestCase):
    """Test the tag inheritance functionality."""
    
    def setUp(self):
        """Set up test data."""
        # Create tags
        self.tag1 = Tag.objects.create(name="Tag1", description="Test tag 1")
        self.tag2 = Tag.objects.create(name="Tag2", description="Test tag 2")
        self.tag3 = Tag.objects.create(name="Tag3", description="Test tag 3")
        
        # Create minimal parent product with tags
        self.parent = ParentProduct.objects.create(
            sku="PARENT001",
            name="Parent Product",
            legacy_base_sku="PARENT001",
        )
        self.parent.tags.add(self.tag1, self.tag2)
        
        # Create minimal variant product
        self.variant = VariantProduct.objects.create(
            sku="VAR001",
            name="Variant Product",
            parent=self.parent,
            legacy_base_sku="VAR001",
        )
        
        # Create another variant with its own tag
        self.variant2 = VariantProduct.objects.create(
            sku="VAR002",
            name="Variant Product 2",
            parent=self.parent,
            legacy_base_sku="VAR002",
        )
        self.variant2.tags.add(self.tag3)
    
    def test_default_inheritance(self):
        """Test that variants inherit tags by default."""
        # By default, variants should inherit tags from parent
        self.assertTrue(self.variant.inherits_tags())
        
        # The variant should see parent tags
        all_tags = list(self.variant.get_all_tags())
        self.assertEqual(len(all_tags), 2)
        self.assertIn(self.tag1, all_tags)
        self.assertIn(self.tag2, all_tags)
    
    def test_inheritance_with_own_tags(self):
        """Test that variants can have their own tags while inheriting."""
        # Variant2 has its own tag and inherits parent tags
        all_tags = list(self.variant2.get_all_tags())
        self.assertEqual(len(all_tags), 3)
        self.assertIn(self.tag1, all_tags)
        self.assertIn(self.tag2, all_tags)
        self.assertIn(self.tag3, all_tags)
    
    def test_disable_inheritance(self):
        """Test that tag inheritance can be disabled."""
        # Disable inheritance for variant2
        self.variant2.set_tags_inheritance(False)
        
        # Now variant2 should only see its own tags
        all_tags = list(self.variant2.get_all_tags())
        self.assertEqual(len(all_tags), 1)
        self.assertIn(self.tag3, all_tags)
        
        # Re-enable inheritance
        self.variant2.set_tags_inheritance(True)
        
        # Now variant2 should see all tags again
        all_tags = list(self.variant2.get_all_tags())
        self.assertEqual(len(all_tags), 3)
    
    def test_override_status(self):
        """Test that the override status is stored correctly."""
        # First ensure variant2 has inheritance enabled
        self.variant2.set_tags_inheritance(True)
        
        # Get content type for VariantProduct
        content_type = ContentType.objects.get_for_model(VariantProduct)
        
        # Check if M2MOverride exists
        override = M2MOverride.objects.get(
            content_type=content_type,
            object_id=self.variant2.id,
            relationship_name='tags'
        )
        
        # Initial state should be inheriting
        self.assertTrue(override.inherit)
        
        # Disable inheritance
        self.variant2.set_tags_inheritance(False)
        
        # Refresh from DB
        override.refresh_from_db()
        
        # Should now be disabled
        self.assertFalse(override.inherit) 