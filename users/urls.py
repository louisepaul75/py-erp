"""
URL patterns for the users app.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    UserViewSet,
    GroupViewSet,
    RoleViewSet,
    PermissionViewSet,
    UserProfileViewSet,
)

app_name = "users"

# Create a router for viewsets
router = DefaultRouter()
router.register(r"users", UserViewSet, basename="users")
router.register(r"profiles", UserProfileViewSet, basename="profiles")
router.register(r"groups", GroupViewSet, basename="groups")
router.register(r"roles", RoleViewSet, basename="roles")
router.register(r"permissions", PermissionViewSet, basename="permissions")

# Custom URLs to support the test expectations
urlpatterns = [
    # Include the router URLs with the app_name namespace
    path("", include((router.urls, app_name))),
]
