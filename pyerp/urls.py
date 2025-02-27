"""
URL Configuration for pyERP project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
"""

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions
from rest_framework_simplejwt.views import (TokenObtainPairView,
                                            TokenRefreshView, TokenVerifyView)

# Create the API schema view
schema_view = get_schema_view(
    openapi.Info(
        title="pyERP API",
        default_version='v1',
        description="API for pyERP system",
        terms_of_service="https://www.example.com/terms/",
        contact=openapi.Contact(email="contact@example.com"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=[permissions.IsAuthenticated],
)

# Main URL patterns
urlpatterns = [
    # Admin site
    path('admin/', admin.site.urls),
    
    # API authentication
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/token/verify/', TokenVerifyView.as_view(), name='token_verify'),
    
    # API documentation
    path('api/docs/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('api/redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    
    # API endpoints
    # Uncomment these as the app URLs are implemented
    # path('api/core/', include('pyerp.core.urls')),
    path('api/products/', include('pyerp.products.urls')),
    # path('api/sales/', include('pyerp.sales.urls')),
    # path('api/inventory/', include('pyerp.inventory.urls')),
    # path('api/production/', include('pyerp.production.urls')),
    # path('api/legacy-sync/', include('pyerp.legacy_sync.urls')),
    
    # Frontend URLs
    path('products/', include('pyerp.products.urls')),
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