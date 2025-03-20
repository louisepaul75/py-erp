"""
URL Configuration for testing.

This module defines URL patterns specifically for testing, making the 
API endpoints available without namespaces.
"""

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from users.views import (
    UserViewSet,
    GroupViewSet,
    RoleViewSet,
    PermissionViewSet,
    UserProfileViewSet,
)

# Create a router for viewsets without namespace
router = DefaultRouter()
router.register(r"users", UserViewSet)
router.register(r"profiles", UserProfileViewSet)
router.register(r"groups", GroupViewSet)
router.register(r"roles", RoleViewSet)
router.register(r"permissions", PermissionViewSet)

urlpatterns = [
    # Include router URLs without namespace
    path("", include(router.urls)),
    # Include the original users app URLs with namespace
    path("namespaced/", include("users.urls", namespace="users")),
] 