"""
Tests for the products views.
"""
import pytest
from django.test import TestCase, Client, override_settings
from django.urls import reverse, include, path
from django.contrib.auth import get_user_model
from django.contrib.messages import get_messages
from rest_framework.test import APIClient, APITestCase

from pyerp.business_modules.products.models import (
    ParentProduct,
    VariantProduct,
    ProductCategory,
    ProductImage
)
from pyerp.business_modules.products.tag_models import Tag

User = get_user_model()

# Set up test URLs
urlpatterns = [
    path('products/', include('pyerp.business_modules.products.urls', namespace='products')),
    path('api/products/', include('pyerp.business_modules.products.api_urls', namespace='products_api')),
]

@pytest.mark.backend
@pytest.mark.unit
@override_settings(ROOT_URLCONF=__name__)
class ProductViewsTestCase(TestCase):
    """Test cases for product views."""

    def setUp(self):
        """Set up test data."""
        # Create test user
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.client = Client()
        self.client.login(username='testuser', password='testpass123')
        
        # Create test data
        self.category = ProductCategory.objects.create(
            name='Test Category',
            description='Test category description'
        )
        
        # Create parent product
        self.parent_product = ParentProduct.objects.create(
            sku='PARENT001',
            name='Test Parent Product',
            legacy_base_sku='PARENT001',
            is_active=True
        )
        
        # Create variant products
        self.variant1 = VariantProduct.objects.create(
            sku='VAR001',
            name='Test Variant 1',
            parent=self.parent_product,
            legacy_base_sku='VAR001',
            variant_code='001'
        )
        
        self.variant2 = VariantProduct.objects.create(
            sku='VAR002',
            name='Test Variant 2',
            parent=self.parent_product,
            legacy_base_sku='VAR002',
            variant_code='002'
        )
        
        # Create test tags
        self.tag1 = Tag.objects.create(name='Tag1', description='Test tag 1')
        self.tag2 = Tag.objects.create(name='Tag2', description='Test tag 2')
        
        # Add tags to parent product
        self.parent_product.tags.add(self.tag1)
        
        # Create test images
        self.product_image = ProductImage.objects.create(
            product=self.variant1,
            image_type='Produktfoto',
            is_front=True,
            image_url='http://example.com/test_image.jpg'
        )

    def test_product_list_view(self):
        """Test the product list view."""
        url = reverse('products:product_list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'products/product_list.html')
        self.assertContains(response, self.parent_product.name)
        self.assertContains(response, self.variant1.name)
        self.assertContains(response, self.variant2.name)

    def test_product_detail_view(self):
        """Test the product detail view."""
        url = reverse('products:product_detail', kwargs={'pk': self.parent_product.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'products/product_detail.html')
        self.assertContains(response, self.parent_product.name)
        self.assertContains(response, self.variant1.name)
        self.assertContains(response, self.variant2.name)

    def test_variant_detail_view(self):
        """Test the variant detail view."""
        url = reverse('products:variant_detail', kwargs={'pk': self.variant1.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'products/variant_detail.html')
        self.assertContains(response, self.variant1.name)
        self.assertContains(response, self.parent_product.name)

    def test_tag_views(self):
        """Test the tag-related views."""
        # Test tag list view
        url = reverse('products:tag_list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'products/tag_list.html')
        self.assertContains(response, self.tag1.name)
        self.assertContains(response, self.tag2.name)

        # Test tag detail view
        url = reverse('products:tag_update', kwargs={'pk': self.tag1.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'products/tag_form.html')
        self.assertContains(response, self.tag1.name)

@pytest.mark.backend
@pytest.mark.unit
@override_settings(ROOT_URLCONF=__name__)
class ProductAPIViewsTestCase(APITestCase):
    """Test cases for product API views."""

    def setUp(self):
        """Set up test data."""
        # Create test user
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
        
        # Create test data
        self.category = ProductCategory.objects.create(
            name='Test Category',
            description='Test category description'
        )
        
        # Create parent product
        self.parent_product = ParentProduct.objects.create(
            sku='PARENT001',
            name='Test Parent Product',
            legacy_base_sku='PARENT001',
            is_active=True
        )
        
        # Create variant products
        self.variant1 = VariantProduct.objects.create(
            sku='VAR001',
            name='Test Variant 1',
            parent=self.parent_product,
            legacy_base_sku='VAR001',
            variant_code='001'
        )

    def test_category_list_api(self):
        """Test the category list API endpoint."""
        url = reverse('products_api:api_category_list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['name'], self.category.name)

    def test_product_list_api(self):
        """Test the product list API endpoint."""
        url = reverse('products_api:api_product_list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['sku'], self.parent_product.sku)

    def test_product_detail_api(self):
        """Test the product detail API endpoint."""
        url = reverse('products_api:api_product_detail', kwargs={'pk': self.parent_product.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['sku'], self.parent_product.sku)
        self.assertEqual(response.data['name'], self.parent_product.name)

    def test_variant_detail_api(self):
        """Test the variant detail API endpoint."""
        url = reverse('products_api:api_variant_detail', kwargs={'pk': self.variant1.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['sku'], self.variant1.sku)
        self.assertEqual(response.data['name'], self.variant1.name) 