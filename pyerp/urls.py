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
from django.views.i18n import JavaScriptCatalog
from rest_framework import permissions
from rest_framework_simplejwt.views import (
    TokenObtainPairView, TokenRefreshView, TokenVerifyView
)
from django.conf.urls.i18n import i18n_patterns
from django.views.i18n import set_language
from pyerp.core.views import VueAppView

# Check if drf_yasg is available
try:
    from drf_yasg import openapi
    from drf_yasg.views import get_schema_view
    
    # Create the API schema view
    schema_view = get_schema_view(
        openapi.Info(
            title="pyERP API",
            default_version='v1',
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

# Non-internationalized URLs - will not have language prefix
non_i18n_urlpatterns = [
    # Language selection URL - using Django's built-in view
    path('set-language/', set_language, name='set_language'),
    
    # JavaScript translations
    path('jsi18n/', JavaScriptCatalog.as_view(), name='javascript-catalog'),
    
    # Django admin URLs
    path('admin/', admin.site.urls),
    
    # API URLs
    path('api/v1/', include('pyerp.core.api_urls')),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/token/verify/', TokenVerifyView.as_view(), name='token_verify'),
    
    # Add monitoring API URL
    path('monitoring/', include('pyerp.monitoring.urls', namespace='monitoring')),
]

# Add API documentation URLs if available
if has_swagger:
    non_i18n_urlpatterns += [
        path('api/docs/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
        path('api/redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    ]

# Default/required app URLs to include in internationalized patterns
i18n_apps = [
    path('', include('pyerp.core.urls')),
    path('products/', include('pyerp.products.urls')),
]

# Optional modules to conditionally include in internationalized patterns
OPTIONAL_FRONTEND_MODULES = [
    ('sales/', 'pyerp.sales.urls'),
    ('inventory/', 'pyerp.inventory.urls'),
    ('production/', 'pyerp.production.urls'),
]

# Add optional frontend modules if available
for url_prefix, module_path in OPTIONAL_FRONTEND_MODULES:
    try:
        # Check if the module can be imported
        __import__(module_path.split('.', 1)[0])
        module_urls = __import__(module_path, fromlist=['urlpatterns'])
        if hasattr(module_urls, 'urlpatterns'):
            i18n_apps.append(path(url_prefix, include(module_path)))
            print(f"Added frontend URL patterns for {module_path}")
    except ImportError as e:
        print(f"WARNING: Could not import {module_path}: {e}")
        print(f"Frontend URL patterns for {url_prefix} will not be available")

# Optional API modules
OPTIONAL_API_MODULES = [
    ('products', 'pyerp.products.api_urls'),
    ('sales', 'pyerp.sales.urls'),
    ('inventory', 'pyerp.inventory.urls'),
    ('production', 'pyerp.production.urls'),
    ('legacy-sync', 'pyerp.legacy_sync.urls'),
]

# Add optional API modules if available
for url_prefix, module_path in OPTIONAL_API_MODULES:
    try:
        __import__(module_path.split('.', 1)[0])
        module_urls = __import__(module_path, fromlist=['urlpatterns'])
        if hasattr(module_urls, 'urlpatterns'):
            # Add to API (non-internationalized) paths
            non_i18n_urlpatterns.append(path(f'api/{url_prefix}/', include(module_path)))
            print(f"Added API URL patterns for {module_path}")
    except ImportError as e:
        print(f"WARNING: Could not import {module_path}: {e}")
        print(f"URL patterns for api/{url_prefix}/ will not be available")

# Build the internationalized URL patterns
i18n_urlpatterns = i18n_patterns(
    # Root URL - redirect to products list
    path('', RedirectView.as_view(pattern_name='products:product_list'), name='home'),
    
    # Django authentication URLs
    path('accounts/', include('django.contrib.auth.urls')),
    
    # Add all app URLs
    *i18n_apps,
    
    # Make language prefix optional
    prefix_default_language=False,
)

# Combine all URL patterns
urlpatterns = non_i18n_urlpatterns + i18n_urlpatterns

# Vue.js application route
urlpatterns += [
    path('vue/', VueAppView.as_view(), name='vue_app'),
]

# Serve static and media files in development
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    
    # Debug toolbar
    if 'debug_toolbar' in settings.INSTALLED_APPS:
        import debug_toolbar
        urlpatterns += [
            path('__debug__/', include(debug_toolbar.urls)),
        ] 