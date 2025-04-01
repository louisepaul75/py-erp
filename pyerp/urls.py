"""
URL Configuration for pyERP project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
"""

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path, re_path
from django.views.i18n import JavaScriptCatalog, set_language
from django.conf.urls.i18n import i18n_patterns
from django.utils.translation import gettext_lazy as _
from rest_framework import permissions, routers
from rest_framework.documentation import include_docs_urls
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)
from django.views.static import serve
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view, renderer_classes, permission_classes
from rest_framework.renderers import JSONRenderer
from rest_framework.permissions import AllowAny

from pyerp.core.views import ReactAppView, UserProfileView
from pyerp.external_api.search.views import GlobalSearchViewSet

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
    print("Spectacular documentation enabled")
except ImportError:
    has_spectacular = False
    print("WARNING: drf_spectacular not available, API documentation will be disabled")

# Create a router for API endpoints
router = routers.DefaultRouter()

# Register API viewsets here
router.register(r"search", GlobalSearchViewSet, basename="search")

# Create a router for versioned API endpoints (v1)
router_v1 = routers.DefaultRouter()

# Register the same viewsets in the versioned router
router_v1.register(r"search", GlobalSearchViewSet, basename="search")

# Define URL patterns with i18n (language prefix) support FIRST
urlpatterns_i18n = i18n_patterns(
    # Django admin URLs
    path("admin/", admin.site.urls),
    # Add monitoring UI URL
    path(
        "monitoring/",
        include("pyerp.monitoring.urls", namespace="monitoring"),
    ),
    # Root URL for React application
    path("", ReactAppView.as_view(), name="react_app"),
    # Use language prefix by default
    prefix_default_language=True
)

# Define URL patterns for non-internationalized URLs (API, static files, etc.)
urlpatterns = [
    path("i18n/", include("django.conf.urls.i18n")),  # For language switching
    path("set-language/", set_language, name="set_language"),
    # JavaScript translations
    path(
        "jsi18n/",
        JavaScriptCatalog.as_view(),
        name="javascript-catalog",
    ),
    # API URLs - maintain backward compatibility with non-versioned endpoints
    path("api/", include(router.urls)),
    
    # Versioned API endpoints (v1)
    path("api/v1/", include(router_v1.urls)),
    
    # Custom API endpoints (Non-versioned)
    path("api/", include("pyerp.api.urls", namespace="custom_api")),
    # Custom API endpoints (Versioned v1)
    path("api/v1/", include("pyerp.api.urls", namespace="custom_api_v1")),
    
    # Add auth/user endpoint (both versioned and non-versioned)
    path("api/auth/user/", UserProfileView.as_view(), name="auth-user-profile"),
    path("api/v1/auth/user/", UserProfileView.as_view(), name="auth-user-profile-v1"),
    
    # Authentication tokens (keep these non-versioned for simplicity)
    path(
        "api/token/",
        TokenObtainPairView.as_view(permission_classes=[]),
        name="token_obtain_pair",
    ),
    path(
        "api/token/refresh/",
        TokenRefreshView.as_view(permission_classes=[]),
        name="token_refresh",
    ),
    path(
        "api/token/verify/",
        TokenVerifyView.as_view(permission_classes=[]),
        name="token_verify",
    ),
    # Add monitoring API URL (both versioned and non-versioned)
    path(
        "api/monitoring/",
        include("pyerp.monitoring.urls", namespace="api_monitoring"),
    ),
    path(
        "api/v1/monitoring/",
        include("pyerp.monitoring.urls", namespace="api_monitoring_v1"),
    ),
    # Add external API connection management (both versioned and non-versioned)
    path(
        "api/external/",
        include("pyerp.external_api.urls", namespace="external_api"),
    ),
    path(
        "api/v1/external/",
        include("pyerp.external_api.urls", namespace="external_api_v1"),
    ),
    # Add email system URLs (both versioned and non-versioned)
    path(
        "api/email/",
        include("pyerp.utils.email_system.urls", namespace="email_system"),
    ),
    path(
        "api/v1/email/",
        include("pyerp.utils.email_system.urls", namespace="email_system_v1"),
    ),
    # Add products API URLs with namespace (both versioned and non-versioned)
    path("api/products/", include("pyerp.business_modules.products.api_urls", namespace="products_api")),
    path("api/v1/products/", include("pyerp.business_modules.products.api_urls", namespace="products_api_v1")),
    # Add products UI URLs with namespace
    path("products/", include("pyerp.business_modules.products.urls", namespace="products")),
    # Add sales API URLs (both versioned and non-versioned)
    path("api/sales/", include("pyerp.business_modules.sales.urls")),
    path("api/v1/sales/", include("pyerp.business_modules.sales.urls", namespace="sales_v1")),
    # Add production API URLs with namespace (both versioned and non-versioned)
    path("api/production/", include("pyerp.business_modules.production.urls", namespace="production_api")),
    path("api/v1/production/", include("pyerp.business_modules.production.urls", namespace="production_api_v1")),
    # Add inventory API URLs with namespace (both versioned and non-versioned)
    path("api/inventory/", include(("pyerp.business_modules.inventory.urls", "inventory"), namespace="inventory")),
    path("api/v1/inventory/", include(("pyerp.business_modules.inventory.urls", "inventory_v1"), namespace="inventory_v1")),
    # API documentation with drf-docs (basic)
    path("api/docs/", include_docs_urls(title="pyERP API Documentation")),
    # Users API (both versioned and non-versioned)
    path("api/users/", include("users.urls", namespace="users")),
    path("api/v1/users/", include("users.urls", namespace="users_v1")),
    # Admin tools API (both versioned and non-versioned)
    path("api/admin/", include("admin_tools.urls")),
    path("api/v1/admin/", include("admin_tools.urls", namespace="admin_tools_v1")),
    
    # Serve Next.js built files - adjusted for Docker environment
    # These paths need to match the structure in the Docker container
    re_path(r'^_next/static/(?P<path>.*)$', serve, {
        'document_root': '/app/frontend-react/.next/static'
    }),
    re_path(r'^_next/(?P<path>.*)$', serve, {
        'document_root': '/app/frontend-react/.next'
    }),
]

# Add drf-spectacular API documentation URLs if available
if has_spectacular:
    urlpatterns += [
        # API Schema generation
        path("api/schema/", 
            SpectacularAPIView.as_view(
                permission_classes=[AllowAny],
                authentication_classes=[],
            ), 
            name="schema"
        ),
        # Swagger UI - simplified configuration
        path(
            "api/swagger/",
            SpectacularSwaggerView.as_view(url_name="schema_v1"),  # Point to v1 schema
            name="swagger-ui",
        ),
        # ReDoc UI
        path(
            "api/redoc/",
            SpectacularRedocView.as_view(url_name="schema_v1"),  # Point to v1 schema
            name="redoc",
        ),
        # Versioned endpoints for documentation
        path("api/v1/schema/", 
            SpectacularAPIView.as_view(
                permission_classes=[AllowAny],
                authentication_classes=[],
            ), 
            name="schema_v1"
        ),
        path(
            "api/v1/swagger/",
            SpectacularSwaggerView.as_view(url_name="schema_v1"),
            name="swagger-ui-v1",
        ),
        path(
            "api/v1/redoc/",
            SpectacularRedocView.as_view(url_name="schema_v1"),
            name="redoc-v1",
        ),
    ]

# Optional API modules (excluding products since we added it directly)
OPTIONAL_API_MODULES = [
    ("sales", "pyerp.sales.urls"),
    # Removed production as it's now added directly
    ("legacy-sync", "pyerp.external_api.legacy_erp.urls"),
]

# Add optional API modules if available
for url_prefix, module_path in OPTIONAL_API_MODULES:
    try:
        __import__(module_path.split(".", 1)[0])
        module_urls = __import__(module_path, fromlist=["urlpatterns"])
        if hasattr(module_urls, "urlpatterns"):
            urlpatterns.append(path(f"api/{url_prefix}/", include(module_path)))
            print(f"Added API URL patterns for {module_path}")
    except ImportError as e:
        print(f"WARNING: Could not import {module_path}: {e}")
        print(f"URL patterns for api/{url_prefix}/ will not be available")

# Include core API URLs
urlpatterns += [
    path("api/", include(("pyerp.core.api_urls", "core_api"), namespace="core_api")),
]

# Add i18n patterns BEFORE the root core include
urlpatterns += urlpatterns_i18n

# Include core URLs at root level LAST (for health check and other core functionality)
urlpatterns += [
    path("", include(("pyerp.core.urls", "core"), namespace="core")),
]

# Serve static and media files in development
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

    # Debug toolbar
    if "debug_toolbar" in settings.INSTALLED_APPS:
        import debug_toolbar

        urlpatterns += [
            path("__debug__/", include(debug_toolbar.urls)),
        ]
