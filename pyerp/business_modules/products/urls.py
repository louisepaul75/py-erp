"""
URL patterns for the products app.
"""

from django.urls import path

from pyerp.business_modules.products.views import (
    CategoryListView,
    ProductDetailView,
    ProductListView,
    VariantDetailView,
    save_product_images,
    TagListView,
    TagCreateView,
    TagUpdateView,
    TagDeleteView,
    VariantProductTagUpdateView,
    ProductListWithTagFilterView,
)

app_name = "products"

# Regular web interface URLs
urlpatterns = [
    path("", ProductListView.as_view(), name="product_list"),
    path("categories/", CategoryListView.as_view(), name="category_list"),
    path("<int:pk>/", ProductDetailView.as_view(), name="product_detail"),
    path("<slug:slug>/", ProductDetailView.as_view(), name="product_detail_slug"),
    path("variant/<int:pk>/", VariantDetailView.as_view(), name="variant_detail"),
    path("<int:pk>/save-images/", save_product_images, name="save_product_images"),
    
    # Tag management URLs
    path("tags/", TagListView.as_view(), name="tag_list"),
    path("tags/create/", TagCreateView.as_view(), name="tag_create"),
    path("tags/<int:pk>/update/", TagUpdateView.as_view(), name="tag_update"),
    path("tags/<int:pk>/delete/", TagDeleteView.as_view(), name="tag_delete"),
    
    # Tag filter URLs
    path("by-tag/<slug:tag_slug>/", ProductListWithTagFilterView.as_view(), name="product_by_tag"),
    
    # Tag inheritance management
    path("variant/<int:pk>/tags/", VariantProductTagUpdateView.as_view(), name="variant_tag_update"),
]
