from django.urls import path
from .views import GroupViewSet
from rest_framework.routers import DefaultRouter

app_name = 'users'

# Create a router and register our viewsets with it
router = DefaultRouter()
router.register(r'groups', GroupViewSet, basename='group')

# The API URLs are now determined automatically by the router
urlpatterns = router.urls 