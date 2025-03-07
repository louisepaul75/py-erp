"""
URL Configuration for pyERP project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
"""

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from django.views.i18n import JavaScriptCatalog, set_language
from rest_framework import permissions
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)

from pyerp.core.views import VueAppView

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
    path("api/", include("pyerp.core.api_urls")),
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
    # Add products API URLs directly
    path("api/products/", include("pyerp.products.api_urls")),
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
    ("sales", "pyerp.sales.urls"),
    ("inventory", "pyerp.inventory.urls"),
    ("production", "pyerp.production.urls"),
    ("legacy-sync", "pyerp.legacy_sync.urls"),
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
