from django.urls import path
from django.http import JsonResponse
from rest_framework.decorators import api_view

app_name = 'inventory'

# Simple view that returns a placeholder response
@api_view(['GET'])
def placeholder_view(request):
    """A placeholder view that returns a simple JSON response."""
    return JsonResponse({
        'message': 'Inventory module is available but not fully implemented',
        'status': 'placeholder'
    })

# URL patterns for the inventory app
urlpatterns = [
    # Add simple placeholder API endpoints
    path('status/', placeholder_view, name='status'),
    path('placeholder/', placeholder_view, name='placeholder'),
] 