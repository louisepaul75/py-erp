"""
URL Configuration for the Legacy Sync module.

This module defines API endpoints for synchronizing data with the legacy system.
"""

from django.urls import path
from rest_framework.routers import DefaultRouter

# Initialize the router
router = DefaultRouter()

# Add any viewsets to the router here
# Example: router.register('entities', EntityViewSet)

# URL patterns
urlpatterns = router.urls

# Add any additional URL patterns here
# Example: path('sync-status/', SyncStatusView.as_view(), name='sync-status'), 