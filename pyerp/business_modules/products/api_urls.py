"""
URL patterns for the products API.
"""

from django.urls import path

from pyerp.business_modules.products.api import (
    ProductCategoryViewSet,
    ProductListAPIView,
    ProductDetailViewSet,
    VariantDetailAPIView,
)
from pyerp.business_modules.products.views import ProductSearchAPIView

app_name = "products_api"

urlpatterns = [
    # Category endpoints
    path("categories/", ProductCategoryViewSet.as_view({"get": "list", "post": "create"}), name="categories_list"),
    path("categories/<int:pk>/", ProductCategoryViewSet.as_view({
        "get": "retrieve",
        "put": "update",
        "patch": "partial_update",
        "delete": "destroy"
    }), name="category_detail"),
    path("categories/<int:pk>/children/", ProductCategoryViewSet.as_view({"get": "children"}), name="category_children"),
    path("categories/tree/", ProductCategoryViewSet.as_view({"get": "tree"}), name="category_tree"),
    
    # Product endpoints
    path("", ProductListAPIView.as_view(), name="product_list"),
    path("", ProductDetailViewSet.as_view({"post": "create"}), name="product_create"),
    path("direct-search/", ProductListAPIView.as_view(direct_search=True), name="product_direct_search"),
    path("search/", ProductSearchAPIView.as_view(), name="product_search"),
    path("<int:pk>/", ProductDetailViewSet.as_view({
        "get": "retrieve",
        "put": "update",
        "patch": "partial_update",
        "delete": "destroy"
    }), name="product_detail"),
    path("<int:pk>/variants/", ProductDetailViewSet.as_view({'get': 'variants'}), name="product_variants_list"),
    
    # Variant endpoints
    path("variant/<int:pk>/", VariantDetailAPIView.as_view(), name="variant_detail"),
]
