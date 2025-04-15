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

# Import sync_manager URLs
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
    
    # --- API URLs consolidated into pyerp.api_urls ---
    path("api/", include("pyerp.api_urls")), 
    
    # --- Include standard app URLs ---
    path("sales/", include(("pyerp.business_modules.sales.urls", "sales"), namespace="sales")),
    # Add other standard app includes here, e.g., products
    
    # --- Other non-API, non-i18n patterns remain ---
    # Serve Next.js built files - adjusted for Docker environment
    re_path(r'^_next/static/(?P<path>.*)$', serve, {
        'document_root': '/app/frontend-react/.next/static'
    }),
    re_path(r'^_next/(?P<path>.*)$', serve, {
        'document_root': '/app/frontend-react/.next'
    }),
]

# Add drf-spectacular API documentation URLs if available
# MOVED to pyerp.api_urls

# Optional API modules (excluding products since we added it directly)
# MOVED to pyerp.api_urls

# Add i18n patterns AFTER the main urlpatterns list is defined
urlpatterns += urlpatterns_i18n

# Include core URLs at root level LAST (for health check and other core functionality)
urlpatterns += [
    path("", include(("pyerp.core.urls", "core"), namespace="core"))
]

# Debug toolbar
if settings.DEBUG:
    # Debug toolbar
    if "debug_toolbar" in settings.INSTALLED_APPS:
        import debug_toolbar
        urlpatterns += [
            path("__debug__/", include(debug_toolbar.urls)),
        ]
    # Serve static and media files in development
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# Temporarily comment out the catch-all to debug 404s in tests
# # Final catch-all for React app (place this after all other patterns)
# urlpatterns.append(re_path(r'^.*$', ReactAppView.as_view(), name='react_app_catchall'))
