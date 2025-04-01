from django.http import JsonResponse
from django.urls import path, include
from rest_framework.decorators import api_view
# from rest_framework.routers import DefaultRouter # Comment out
from .views import (
    CustomerViewSet,
    AddressViewSet,
    SalesRecordViewSet,
    SalesRecordItemViewSet,
    placeholder_view # Ensure placeholder_view is imported
)

app_name = "sales"

# Create a router and register our viewsets with it
# router = DefaultRouter() # Comment out
# router.register(r"customers", CustomerViewSet) # Comment out
# router.register(r"addresses", AddressViewSet) # Comment out
# router.register(r"records", SalesRecordViewSet) # Comment out
# router.register(r"record-items", SalesRecordItemViewSet) # Comment out


# Simple view that returns a placeholder response
# @api_view(["GET"]) # This decorator is already on the view in views.py
# def placeholder_view(request):
#     """A placeholder view that returns a simple JSON response."""
#     return JsonResponse(
#         {
#             "message": "Sales module is available but not fully implemented",
#             "status": "placeholder",
#         },
#     )


# URL patterns for the sales app
urlpatterns = [
    # path("", include(router.urls)), # Comment out
    path("status/", placeholder_view, name="status"),
    path("placeholder/", placeholder_view, name="placeholder"),
    # Add a direct path for testing:
    path("records/", placeholder_view, name="records_test"),
]
