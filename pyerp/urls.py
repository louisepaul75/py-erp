"""
URL Configuration for pyERP project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
"""

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from django.views.generic import RedirectView
from django.views.i18n import JavaScriptCatalog, set_language
from rest_framework import permissions, routers
from rest_framework.documentation import include_docs_urls
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)

from pyerp.core.views import VueAppView
from pyerp.external_api.search.views import GlobalSearchViewSet

# Check if drf_yasg is available
try:
    from drf_yasg import openapi
    from drf_yasg.views import get_schema_view

    # Create the API schema view
    schema_view = get_schema_view(
        openapi.Info(
            title="pyERP API",
            default_version="v1",
            description="API for pyERP system",
        ),
        public=False,
        permission_classes=(permissions.IsAuthenticated,),
    )
    has_swagger = True
    print("Swagger documentation enabled")
except ImportError:
    has_swagger = False
    print("WARNING: drf_yasg not available, API documentation will be disabled")

# Create a router for API endpoints
router = routers.DefaultRouter()

# Register API viewsets here
router.register(r'search', GlobalSearchViewSet, basename='search')

# Define URL patterns
urlpatterns = [
    path("set-language/", set_language, name="set_language"),
    # JavaScript translations
    path(
        "jsi18n/",
        JavaScriptCatalog.as_view(),
        name="javascript-catalog",
    ),
    # Django admin URLs
    path("admin/", admin.site.urls),
    # API URLs
    path("api/", include(router.urls)),
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
    # Add monitoring API URL
    path(
        "monitoring/",
        include("pyerp.monitoring.urls", namespace="monitoring"),
    ),
    path(
        "api/monitoring/",
        include("pyerp.monitoring.urls", namespace="api_monitoring"),
    ),
    # Add external API connection management
    path(
        "api/external/",
        include("pyerp.external_api.urls", namespace="external_api"),
    ),
    # Add email system URLs
    path(
        "api/email/",
        include("pyerp.utils.email_system.urls", namespace="email_system"),
    ),
    # Add products API URLs directly
    path("api/products/", include("pyerp.business_modules.products.api_urls")),
    # Add sales API URLs
    path("api/sales/", include("pyerp.business_modules.sales.urls")),
    # Add inventory API URLs
    path("api/inventory/", include("pyerp.business_modules.inventory.urls")),
    # API documentation
    path('api/docs/', include_docs_urls(title='pyERP API Documentation')),
    # Redirect root to admin interface for now
    path('', RedirectView.as_view(url='/admin/', permanent=False)),
    # Users API
    path("api/users/", include("users.urls")),
    # Admin tools API
    path("api/admin/", include("admin_tools.urls")),
]

# Add API documentation URLs if available
if has_swagger:
    urlpatterns += [
        path(
            "api/docs/",
            schema_view.with_ui("swagger", cache_timeout=0),
            name="schema-swagger-ui",
        ),
        path(
            "api/redoc/",
            schema_view.with_ui("redoc", cache_timeout=0),
            name="schema-redoc",
        ),
    ]

# Optional API modules (excluding products since we added it directly)
OPTIONAL_API_MODULES = [
    ("inventory", "pyerp.business_modules.inventory.urls"),
    ("production", "pyerp.production.urls"),
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

# Include core URLs at root level (for health check and other core functionality)
urlpatterns += [
    path("", include("pyerp.core.urls")),
]

# Include core API URLs
urlpatterns += [
    path("api/", include("pyerp.core.api_urls")),
]

# Vue.js application route - now as the root URL
urlpatterns += [
    path("", VueAppView.as_view(), name="vue_app"),
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
