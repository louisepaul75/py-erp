"""
URL patterns for the products app.
"""

from django.urls import path

from pyerp.products.views import (
    ProductListView, 
    ProductDetailView, 
    CategoryListView,
    save_product_images
)

app_name = 'products'

urlpatterns = [
    path('', ProductListView.as_view(), name='product_list'),
    path('categories/', CategoryListView.as_view(), name='category_list'),
    path('<int:pk>/', ProductDetailView.as_view(), name='product_detail'),
    path('<slug:slug>/', ProductDetailView.as_view(), name='product_detail_slug'),
    path('<int:pk>/save-images/', save_product_images, name='save_product_images'),
] 