"""
URL Configuration for versioned API endpoints (v1).
This file contains only v1 endpoints for use with the API documentation.
"""

from django.urls import include, path
from rest_framework import routers
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)

from pyerp.core.views import UserProfileView
from pyerp.external_api.search.views import GlobalSearchViewSet

# Create a router for versioned API endpoints (v1)
router_v1 = routers.DefaultRouter()

# Register API viewsets in the v1 router
router_v1.register(r"search", GlobalSearchViewSet, basename="search")

# Define URL patterns for v1 endpoints only
urlpatterns = [
    # API URLs - only versioned endpoints (v1)
    path("api/v1/", include(router_v1.urls)),
    
    # Auth/user endpoint
    path("api/v1/auth/user/", UserProfileView.as_view(), name="auth-user-profile-v1"),
    
    # Monitoring API URL
    path(
        "api/v1/monitoring/",
        include("pyerp.monitoring.urls", namespace="api_monitoring_v1"),
    ),
    
    # External API connection management
    path(
        "api/v1/external/",
        include("pyerp.external_api.urls", namespace="external_api_v1"),
    ),
    
    # Email system URLs
    path(
        "api/v1/email/",
        include("pyerp.utils.email_system.urls", namespace="email_system_v1"),
    ),
    
    # Products API URLs
    path("api/v1/products/", include("pyerp.business_modules.products.api_urls", namespace="products_api_v1")),
    
    # Sales API URLs
    path("api/v1/sales/", include("pyerp.business_modules.sales.urls", namespace="sales_v1")),
    
    # Inventory API URLs
    path("api/v1/inventory/", include(("pyerp.business_modules.inventory.urls", "inventory_v1"), namespace="inventory_v1")),
    
    # Users API
    path("api/v1/users/", include("users.urls", namespace="users_v1")),
    
    # Admin tools API
    path("api/v1/admin/", include("admin_tools.urls", namespace="admin_tools_v1")),
    
    # Include core API URLs for v1
    path("api/v1/", include("pyerp.core.api_urls")),
] 