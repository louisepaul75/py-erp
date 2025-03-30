"""
Tests for the products forms.
"""
import pytest
from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile

from pyerp.business_modules.products.forms import (
    ProductSearchForm,
    TagInheritanceForm,
    ProductForm,
    ParentProductForm,
    VariantProductForm,
    ProductCategoryForm
)
from pyerp.business_modules.products.models import (
    ParentProduct,
    VariantProduct,
    ProductCategory,
    UnifiedProduct
)
from pyerp.core.models import Tag

@pytest.mark.backend
@pytest.mark.unit
class ProductFormsTestCase(TestCase):
    """Test cases for product forms."""

    def setUp(self):
        """Set up test data."""
        self.category = ProductCategory.objects.create(
            name='Test Category',
            code='TEST',
            description='Test category description'
        )
        
        self.parent_product = ParentProduct.objects.create(
            sku='PARENT001',
            name='Test Parent Product',
            legacy_base_sku='PARENT001',
            is_active=True
        )
        
        self.variant = VariantProduct.objects.create(
            sku='VAR001',
            name='Test Variant',
            parent=self.parent_product,
            legacy_base_sku='VAR001'
        )
        
        self.tag = Tag.objects.create(
            name='Test Tag',
            description='Test tag description'
        )

    def test_product_search_form_valid(self):
        """Test ProductSearchForm with valid data."""
        form_data = {
            'q': 'Test Product',
            'category': self.category.id,
            'min_price': '10.00',
            'max_price': '100.00',
            'is_active': True,
            'in_stock': True
        }
        form = ProductSearchForm(data=form_data)
        self.assertTrue(form.is_valid())
        
        # Test empty form is also valid
        form = ProductSearchForm(data={})
        self.assertTrue(form.is_valid())

    def test_product_search_form_invalid(self):
        """Test ProductSearchForm with invalid data."""
        # Test invalid price range
        form_data = {
            'min_price': '100.00',
            'max_price': '10.00'
        }
        form = ProductSearchForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('min_price', form.errors)

    def test_tag_inheritance_form_valid(self):
        """Test TagInheritanceForm with valid data."""
        form_data = {
            'inherit_tags': True,
            'tags': [self.tag.id]
        }
        form = TagInheritanceForm(instance=self.variant, data=form_data)
        self.assertTrue(form.is_valid())
        
        # Test form without tags
        form_data = {
            'inherit_tags': False
        }
        form = TagInheritanceForm(instance=self.variant, data=form_data)
        self.assertTrue(form.is_valid())

    def test_product_form_valid(self):
        """Test ProductForm with valid data."""
        form_data = {
            'name': 'New Product',
            'sku': 'NEW001',
            'description': 'New product description',
            'is_active': True,
            'is_parent': True,
            'is_variant': False,
            'price': '99.99'
        }
        
        form = ProductForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_product_form_invalid(self):
        """Test ProductForm with invalid data."""
        # Create a product first to test duplicate SKU
        UnifiedProduct.objects.create(
            name='Existing Product',
            sku='EXISTING001',
            price='99.99',
            description='Test description',
            is_active=True,
            is_parent=True,
            is_variant=False
        )
        
        # Test duplicate SKU
        form_data = {
            'name': 'New Product',
            'sku': 'EXISTING001',  # Already exists
            'is_parent': True,
            'is_variant': False,
            'price': '99.99',
            'description': 'Test description',
            'is_active': True
        }
        
        form = ProductForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('sku', form.errors)
        
        # Test invalid parent/variant combination
        form_data = {
            'name': 'New Product',
            'sku': 'NEW001',
            'is_parent': True,
            'is_variant': True,  # Can't be both
            'price': '99.99',
            'description': 'Test description',
            'is_active': True
        }
        
        form = ProductForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('is_parent', form.errors)
        self.assertIn('is_variant', form.errors)

    def test_parent_product_form_valid(self):
        """Test ParentProductForm with valid data."""
        form_data = {
            'name': 'New Parent',
            'sku': 'NEWPARENT001',
            'legacy_base_sku': 'NEWPARENT001',
            'is_active': True
        }
        
        form = ParentProductForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_parent_product_form_invalid(self):
        """Test ParentProductForm with invalid data."""
        # Test duplicate SKU
        form_data = {
            'name': 'New Parent',
            'sku': 'PARENT001',  # Already exists
            'legacy_base_sku': 'NEWPARENT001'
        }
        
        form = ParentProductForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('sku', form.errors)

    def test_variant_product_form_valid(self):
        """Test VariantProductForm with valid data."""
        form_data = {
            'name': 'New Variant',
            'sku': 'NEWVAR001',
            'variant_code': '001',
            'parent': self.parent_product.id,
            'is_active': True
        }
        
        form = VariantProductForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_variant_product_form_invalid(self):
        """Test VariantProductForm with invalid data."""
        # Test missing required fields
        form = VariantProductForm(data={})
        self.assertFalse(form.is_valid())
        self.assertIn('name', form.errors)
        self.assertIn('sku', form.errors)
        self.assertIn('parent', form.errors)
        
        # Test duplicate SKU
        form_data = {
            'name': 'New Variant',
            'sku': 'VAR001',  # Already exists
            'variant_code': '001',
            'parent': self.parent_product.id
        }
        
        form = VariantProductForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('sku', form.errors)

    def test_product_category_form_valid(self):
        """Test ProductCategoryForm with valid data."""
        form_data = {
            'name': 'New Category',
            'code': 'NEWCAT'
        }
        
        form = ProductCategoryForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_product_category_form_invalid(self):
        """Test ProductCategoryForm with invalid data."""
        # Test missing required fields
        form = ProductCategoryForm(data={})
        self.assertFalse(form.is_valid())
        self.assertIn('name', form.errors)
        self.assertIn('code', form.errors) 