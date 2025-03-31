from django.http import JsonResponse
from django.urls import path, include
from rest_framework.decorators import api_view
from rest_framework.routers import DefaultRouter

from pyerp.business_modules.production.views import MoldViewSet, MoldProductViewSet

app_name = "production"

# Create a router for production API endpoints
router = DefaultRouter()
router.register(r'molds', MoldViewSet)
router.register(r'mold-products', MoldProductViewSet)

# Simple view that returns a placeholder response
@api_view(["GET"])
def placeholder_view(request):
    """A placeholder view that returns a simple JSON response."""
    return JsonResponse(
        {
            "message": "Production module is available but not fully implemented",
            "status": "placeholder",
        },
    )


# URL patterns for the production app
urlpatterns = [
    path("status/", placeholder_view, name="status"),
    path("placeholder/", placeholder_view, name="placeholder"),
    # Include router URLs
    path("", include(router.urls)),
]
