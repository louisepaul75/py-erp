"""
API URLs for the sales module.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    CustomerViewSet,
    AddressViewSet,
    SalesRecordViewSet,
    SalesRecordItemViewSet,
)
from .api import SalesRecordRelationshipViewSet

app_name = "sales_api"

# Create a router and register our viewsets with it
router = DefaultRouter()
router.register(r"customers", CustomerViewSet, basename='customers')
router.register(r"addresses", AddressViewSet)
router.register(r"records", SalesRecordViewSet, basename='salesrecord')
router.register(r"record-items", SalesRecordItemViewSet)
router.register(r"relationships", SalesRecordRelationshipViewSet)

# URL patterns for the sales API
urlpatterns = [
    path("", include(router.urls)),
] 