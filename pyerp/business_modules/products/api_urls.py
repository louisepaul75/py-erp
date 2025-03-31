"""
URL patterns for the products API.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter

from pyerp.business_modules.products.api import (
    ProductCategoryViewSet,
    ProductDetailViewSet,
    ProductListAPIView,
    VariantDetailAPIView,
)

app_name = "products_api"

# Create a router for documented API endpoints
router = DefaultRouter()
router.register(r'categories', ProductCategoryViewSet, basename='category')
router.register(r'products', ProductDetailViewSet, basename='product')

urlpatterns = [
    # Include the router URLs
    path('', include(router.urls)),
    
    # Add custom API views that don't follow REST ViewSet patterns
    path("list/", ProductListAPIView.as_view(), name="product_list"),
    path("variant/<int:pk>/", VariantDetailAPIView.as_view(), name="variant_detail"),
]
