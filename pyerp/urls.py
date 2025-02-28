"""
URL Configuration for pyERP project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
"""

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import include, path
from django.views.generic import RedirectView
from rest_framework import permissions
from rest_framework_simplejwt.views import (TokenObtainPairView,
                                            TokenRefreshView, TokenVerifyView)

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
            terms_of_service="https://www.example.com/terms/",
            contact=openapi.Contact(email="contact@example.com"),
            license=openapi.License(name="BSD License"),
        ),
        public=True,
        permission_classes=[permissions.IsAuthenticated],
    )
    
    HAS_SWAGGER = True
    print("Swagger documentation enabled")
except ImportError:
    HAS_SWAGGER = False
    print("WARNING: drf_yasg not available, API documentation will be disabled")

# Main URL patterns
urlpatterns = [
    # Root URL - redirect to products list
    path('', RedirectView.as_view(pattern_name='products:product_list'), name='home'),
    
    # Admin site
    path('admin/', admin.site.urls),
    
    # Authentication URLs
    path('accounts/login/', auth_views.LoginView.as_view(), name='login'),
    path('accounts/logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('accounts/password_change/', auth_views.PasswordChangeView.as_view(), name='password_change'),
    path('accounts/password_change/done/', auth_views.PasswordChangeDoneView.as_view(), name='password_change_done'),
    path('accounts/password_reset/', auth_views.PasswordResetView.as_view(), name='password_reset'),
    path('accounts/password_reset/done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('accounts/reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('accounts/reset/done/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),
    
    # API authentication
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/token/verify/', TokenVerifyView.as_view(), name='token_verify'),
    
    # API endpoints
    # Uncomment these as the app URLs are implemented
    # path('api/core/', include('pyerp.core.urls')),
    path('api/products/', include('pyerp.products.api_urls')),
    
    # Frontend URLs
    path('products/', include('pyerp.products.urls')),
]

# Add Swagger documentation if available
if HAS_SWAGGER:
    urlpatterns.extend([
        path('api/docs/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
        path('api/redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    ])

# Conditionally include sales URLs
try:
    import pyerp.sales.urls
    urlpatterns.append(path('api/sales/', include('pyerp.sales.urls')))
    print("Sales URLs included")
except ImportError:
    print("WARNING: Sales module could not be imported, skipping URLs")

# Commented out URLs for future use
# path('api/inventory/', include('pyerp.inventory.urls')),
# path('api/production/', include('pyerp.production.urls')),
# path('api/legacy-sync/', include('pyerp.legacy_sync.urls')),

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