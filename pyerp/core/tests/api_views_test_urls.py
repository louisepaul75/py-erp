"""
Test URL configuration for API view tests.

This module provides isolated URL patterns for API tests.
"""
from django.urls import path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)
from rest_framework.permissions import AllowAny

from pyerp.core.views import csrf_token

app_name = 'test_api'

urlpatterns = [
    # CSRF token view
    path("api/csrf/", csrf_token, name="api-csrf-token"),
    
    # JWT token routes
    path(
        "api/token/",
        TokenObtainPairView.as_view(permission_classes=[AllowAny]),
        name="token_obtain_pair",
    ),
    path(
        "api/token/refresh/",
        TokenRefreshView.as_view(permission_classes=[AllowAny]),
        name="token_refresh",
    ),
    path(
        "api/token/verify/",
        TokenVerifyView.as_view(permission_classes=[AllowAny]),
        name="token_verify",
    ),
] 