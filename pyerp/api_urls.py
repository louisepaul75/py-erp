"""
Consolidated API URL Configuration for pyERP project.
"""

from django.urls import include, path
from rest_framework import routers
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)
from rest_framework.permissions import AllowAny

# Import routers defined in main urls.py
# This assumes they are defined before this module is imported,
# which might be fragile. Consider passing them explicitly if issues arise.
from pyerp.urls import router, router_v1 

# Import views/URL modules referenced by the patterns
from pyerp.core.views import UserProfileView
from sync_manager import urls as sync_manager_urls

# Flag to track API doc availability
has_spectacular = False

# Check if drf_spectacular is available
try:
    from drf_spectacular.views import (
        SpectacularAPIView,
        SpectacularSwaggerView,
        SpectacularRedocView,
    )
    has_spectacular = True
except ImportError:
    has_spectacular = False

# Define API urlpatterns
urlpatterns = [
    # Core API URLs (contains /api/csrf/, etc.) - Included first
    path("", include("pyerp.core.api_urls", namespace="core_api")),
    
    # Custom API endpoints 
    path("", include("pyerp.api.urls", namespace="custom_api")),
    path("v1/", include("pyerp.api.urls", namespace="custom_api_v1")),
    
    # Specific JWT Token URLs
    path(
        "token/",
        TokenObtainPairView.as_view(permission_classes=[]),
        name="token_obtain_pair",
    ),
    path(
        "token/refresh/",
        TokenRefreshView.as_view(permission_classes=[]),
        name="token_refresh",
    ),
    path(
        "token/verify/",
        TokenVerifyView.as_view(permission_classes=[]),
        name="token_verify",
    ),

    # Default Router API URLs - Using imported routers
    path("", include(router.urls)), 
    path("v1/", include(router_v1.urls)),

    # Auth User Profile
    path("auth/user/", UserProfileView.as_view(), name="auth-user-profile"),
    path("v1/auth/user/", UserProfileView.as_view(), name="auth-user-profile-v1"),

    # Other included apps
    path("monitoring/", include("pyerp.monitoring.urls", namespace="api_monitoring")),
    path("v1/monitoring/", include("pyerp.monitoring.urls", namespace="api_monitoring_v1")),
    path("external/", include("pyerp.external_api.urls", namespace="external_api")),
    path("v1/external/", include("pyerp.external_api.urls", namespace="external_api_v1")),
    path("email/", include("pyerp.utils.email_system.urls", namespace="email_system")),
    path("v1/email/", include("pyerp.utils.email_system.urls", namespace="email_system_v1")),
    path("products/", include("pyerp.business_modules.products.api_urls", namespace="products_api")),
    path("v1/products/", include("pyerp.business_modules.products.api_urls", namespace="products_api_v1")),
    path("sales/", include("pyerp.business_modules.sales.api_urls", namespace="sales_api")),
    path("v1/sales/", include("pyerp.business_modules.sales.api_urls", namespace="sales_api_v1")),
    path("production/", include("pyerp.business_modules.production.urls", namespace="production_api")),
    path("v1/production/", include("pyerp.business_modules.production.urls", namespace="production_api_v1")),
    path("inventory/", include(("pyerp.business_modules.inventory.urls", "inventory"), namespace="inventory")),
    path("v1/inventory/", include(("pyerp.business_modules.inventory.urls", "inventory_v1"), namespace="inventory_v1")),
    path("users/", include("users.urls", namespace="users")),
    path("v1/users/", include("users.urls", namespace="users_v1")),
    path("admin/", include("admin_tools.urls")),
    path("v1/admin/", include("admin_tools.urls", namespace="admin_tools_v1")),
    path("sync/", include(sync_manager_urls, namespace="sync_manager")),
    path("v1/sync/", include(sync_manager_urls, namespace="sync_manager_v1")),
]

# Add drf-spectacular API documentation URLs if available
if has_spectacular:
    urlpatterns += [
        path("schema/", SpectacularAPIView.as_view(permission_classes=[AllowAny], authentication_classes=[]), name="schema"),
        path("v1/schema/", SpectacularAPIView.as_view(permission_classes=[AllowAny], authentication_classes=[]), name="schema_v1"),
        path("swagger/", SpectacularSwaggerView.as_view(url_name="schema_v1"), name="swagger-ui"),
        path("v1/swagger/", SpectacularSwaggerView.as_view(url_name="schema_v1"), name="swagger-ui-v1"),
        path("redoc/", SpectacularRedocView.as_view(url_name="schema_v1"), name="redoc"),
        path("v1/redoc/", SpectacularRedocView.as_view(url_name="schema_v1"), name="redoc-v1"),
    ] 