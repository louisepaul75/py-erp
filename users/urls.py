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
    UserProfileViewSet
)

app_name = 'users'

# Create a router for viewsets
router = DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'profiles', UserProfileViewSet)
router.register(r'groups', GroupViewSet)
router.register(r'roles', RoleViewSet)
router.register(r'permissions', PermissionViewSet)

urlpatterns = [
    # Include router URLs
    path('', include(router.urls)),
] 