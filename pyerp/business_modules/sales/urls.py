from django.http import JsonResponse
from django.urls import path, include
from rest_framework.decorators import api_view
from rest_framework.routers import DefaultRouter
from .views import CustomerViewSet, AddressViewSet

app_name = "sales"

# Create a router and register our viewsets with it
router = DefaultRouter()
router.register(r'customers', CustomerViewSet)
router.register(r'addresses', AddressViewSet)

# Simple view that returns a placeholder response
@api_view(["GET"])
def placeholder_view(request):
    """A placeholder view that returns a simple JSON response."""
    return JsonResponse(
        {
            "message": "Sales module is available but not fully implemented",
            "status": "placeholder",
        },
    )

# URL patterns for the sales app
urlpatterns = [
    path('', include(router.urls)),
    path("status/", placeholder_view, name="status"),
    path("placeholder/", placeholder_view, name="placeholder"),
]
