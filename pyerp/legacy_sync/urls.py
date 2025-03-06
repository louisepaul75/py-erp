"""
URL Configuration for the Legacy Sync module.

This module defines API endpoints for synchronizing data with the legacy system.  # noqa: E501
"""

from django.urls import path  # noqa: F401
from rest_framework.routers import DefaultRouter

# Initialize the router
router = DefaultRouter()

# Add any viewsets to the router here
# Example: router.register('entities', EntityViewSet)

# URL patterns
urlpatterns = router.urls
  # noqa: F841

# Add any additional URL patterns here

  # noqa: F841
