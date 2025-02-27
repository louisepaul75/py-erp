"""
URL patterns for the products app.
"""

from django.urls import path

from pyerp.products.views import (
    ProductListView, 
    ProductDetailView, 
    CategoryListView,
    VariantDetailView,
    save_product_images
)

app_name = 'products'

# Regular web interface URLs
urlpatterns = [
    path('', ProductListView.as_view(), name='product_list'),
    path('categories/', CategoryListView.as_view(), name='category_list'),
    path('<int:pk>/', ProductDetailView.as_view(), name='product_detail'),
    path('<slug:slug>/', ProductDetailView.as_view(), name='product_detail_slug'),
    path('variant/<int:pk>/', VariantDetailView.as_view(), name='variant_detail'),
    path('<int:pk>/save-images/', save_product_images, name='save_product_images'),
] 