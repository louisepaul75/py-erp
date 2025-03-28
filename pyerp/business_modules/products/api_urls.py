"""
URL patterns for the products API.
"""

from django.urls import path

from pyerp.business_modules.products.views import (
    CategoryListAPIView,
    ProductDetailAPIView,
    ProductListAPIView,
    VariantDetailAPIView,
)

app_name = "products_api"

urlpatterns = [
    path("", ProductListAPIView.as_view(), name="api_product_list"),
    path("categories/", CategoryListAPIView.as_view(), name="api_category_list"),
    path("<int:pk>/", ProductDetailAPIView.as_view(), name="api_product_detail"),
    path("variant/<int:pk>/", VariantDetailAPIView.as_view(), name="api_variant_detail"),
]
