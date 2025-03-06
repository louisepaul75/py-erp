"""
URL patterns for the products app.
"""

from django.urls import path

from pyerp.products.views import (
    ProductListView,  # noqa: E128
    ProductDetailView,
    CategoryListView,
    VariantDetailView,
    save_product_images
)

app_name = 'products'

 # Regular web interface URLs
urlpatterns = [
               path('', ProductListView.as_view(), name='product_list'),
               path('categories/', CategoryListView.as_view(), name='category_list'),  # noqa: E501
               path('<int:pk>/', ProductDetailView.as_view(), name='product_detail'),  # noqa: E501
               path('<slug:slug>/', ProductDetailView.as_view(), name='product_detail_slug'),  # noqa: E501
               path('variant/<int:pk>/', VariantDetailView.as_view(), name='variant_detail'),  # noqa: E501
               path('<int:pk>/save-images/', save_product_images, name='save_product_images'),  # noqa: E501
               # noqa: E501, F841
]
