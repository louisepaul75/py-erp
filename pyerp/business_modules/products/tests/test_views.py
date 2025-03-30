"""
Tests for the products views.
"""
import pytest
from django.test import override_settings
from django.urls import reverse, include, path
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient, APITestCase

from pyerp.business_modules.products.models import (
    ParentProduct,
    VariantProduct,
    ProductCategory,
    ProductImage
)
from pyerp.core.models import Tag

User = get_user_model()

# Set up test URLs
urlpatterns = [
    path('products/', include('pyerp.business_modules.products.urls', 
         namespace='products')),
    path('api/products/', include('pyerp.business_modules.products.api_urls', 
         namespace='products_api')),
]


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
        self.assertIn('results', response.data)
        self.assertTrue(len(response.data['results']) >= 1)
        self.assertTrue(any(category['name'] == self.category.name 
                            for category in response.data['results']))

    def test_product_list_api(self):
        """Test the product list API endpoint."""
        url = reverse('products_api:api_product_list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertIn('results', response.data)
        self.assertTrue(len(response.data['results']) >= 1)
        self.assertTrue(any(product['sku'] == self.parent_product.sku 
                            for product in response.data['results']))

    def test_product_detail_api(self):
        """Test the product detail API endpoint."""
        url = reverse('products_api:api_product_detail', 
                      kwargs={'pk': self.parent_product.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['sku'], self.parent_product.sku)
        self.assertEqual(response.data['name'], self.parent_product.name)

    def test_variant_detail_api(self):
        """Test the variant detail API endpoint."""
        url = reverse('products_api:api_variant_detail', 
                      kwargs={'pk': self.variant1.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['sku'], self.variant1.sku)
        self.assertEqual(response.data['name'], self.variant1.name) 