"""
Tests for the products template filters.
"""
import pytest
from django.test import TestCase
from django.template import Template, Context

from pyerp.business_modules.products.models import (
    ParentProduct,
    VariantProduct,
    ProductImage
)
from pyerp.business_modules.products.templatetags.product_filters import (
    get_primary_image,
    get_item
)

@pytest.mark.backend
@pytest.mark.unit
class ProductTemplateFiltersTestCase(TestCase):
    """Test cases for product template filters."""

    def setUp(self):
        """Set up test data."""
        # Create parent product
        self.parent_product = ParentProduct.objects.create(
            sku='PARENT001',
            name='Test Parent Product',
            legacy_base_sku='PARENT001',
            is_active=True
        )
        
        # Create variant
        self.variant = VariantProduct.objects.create(
            sku='VAR001',
            name='Test Variant',
            parent=self.parent_product,
            legacy_base_sku='VAR001'
        )
        
        # Create product images (attached to variant)
        self.front_image = ProductImage.objects.create(
            product=self.variant,
            image_type='Produktfoto',
            is_front=True,
            image_url='http://example.com/front_image.jpg',
            external_id='front001'
        )
        
        self.primary_image = ProductImage.objects.create(
            product=self.variant,
            image_type='Produktfoto',
            is_primary=True,
            image_url='http://example.com/primary_image.jpg',
            external_id='primary001'
        )
        
        self.regular_image = ProductImage.objects.create(
            product=self.variant,
            image_type='Produktfoto',
            image_url='http://example.com/regular_image.jpg',
            external_id='regular001'
        )

    def test_get_primary_image_filter(self):
        """Test get_primary_image template filter."""
        # Test with front image
        primary = get_primary_image(self.variant)
        self.assertEqual(primary, self.front_image)
        
        # Test with primary image (after deleting front image)
        self.front_image.delete()
        primary = get_primary_image(self.variant)
        self.assertEqual(primary, self.primary_image)
        
        # Test with regular image (after deleting primary image)
        self.primary_image.delete()
        primary = get_primary_image(self.variant)
        self.assertEqual(primary, self.regular_image)
        
        # Test with no images
        self.regular_image.delete()
        primary = get_primary_image(self.variant)
        self.assertIsNone(primary)
        
        # Test with None input
        primary = get_primary_image(None)
        self.assertIsNone(primary)

    def test_get_item_filter(self):
        """Test get_item template filter."""
        # Test with valid dictionary and key
        test_dict = {'key1': 'value1', 'key2': 'value2'}
        self.assertEqual(get_item(test_dict, 'key1'), 'value1')
        
        # Test with invalid key
        self.assertIsNone(get_item(test_dict, 'nonexistent_key'))
        
        # Test with None dictionary
        self.assertIsNone(get_item(None, 'key1'))

    def test_template_rendering(self):
        """Test filters in template context."""
        template = Template(
            '{% load product_filters %}'
            '{% with image=variant|get_primary_image %}'
            '{{ image.image_url }}'
            '{% endwith %}'
        )
        
        context = Context({
            'variant': self.variant
        })
        
        rendered = template.render(context)
        self.assertNotEqual(rendered.strip(), '') 