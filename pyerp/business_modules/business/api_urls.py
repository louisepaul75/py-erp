from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import EmployeeViewSet, SupplierViewSet

router = DefaultRouter()
router.register(r'employees', EmployeeViewSet)
router.register(r'suppliers', SupplierViewSet)

app_name = 'business_api' # Optional: Define an app namespace

urlpatterns = [
    path('', include(router.urls)),
] 