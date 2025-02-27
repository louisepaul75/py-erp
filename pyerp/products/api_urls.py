"""
URL patterns for the products API.
"""

from django.urls import path

from pyerp.products.views import (
    ProductListAPIView,
    ProductDetailAPIView,
    CategoryListAPIView
)

app_name = 'products_api'

urlpatterns = [
    path('', ProductListAPIView.as_view(), name='product_list'),
    path('categories/', CategoryListAPIView.as_view(), name='category_list'),
    path('<int:pk>/', ProductDetailAPIView.as_view(), name='product_detail'),
    path('by-slug/<slug:slug>/', ProductDetailAPIView.as_view(), name='product_detail_slug'),
] 