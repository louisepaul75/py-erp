from django.shortcuts import render
from rest_framework import viewsets, permissions, filters, generics
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import get_user_model
from django_filters.rest_framework import DjangoFilterBackend

from .models import Employee, Supplier
from .serializers import (
    EmployeeSerializer, 
    SupplierSerializer, 
    UserSerializer, 
)

User = get_user_model()

# Create your views here.

class EmployeeViewSet(viewsets.ModelViewSet):
    """API endpoint that allows employees to be viewed or edited."""
    queryset = Employee.objects.all().order_by('last_name', 'first_name')
    serializer_class = EmployeeSerializer
    permission_classes = [permissions.IsAuthenticated] # Adjust permissions as needed
    
    # Add filtering and searching capabilities
    filter_backends = [
        DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter
    ]
    # Fields for exact match filtering
    filterset_fields = ['is_terminated', 'is_present']
    # Fields for text search
    search_fields = [
        'employee_number', 'first_name', 'last_name', 'email', 'ad_username'
    ]
    # Fields allowed for ordering
    ordering_fields = [
        'last_name', 'first_name', 'employee_number', 'hire_date', 'created_at'
    ]
    # Default ordering
    ordering = ['last_name', 'first_name']

class UserListView(generics.ListAPIView):
    """API endpoint to list users for selection."""
    queryset = User.objects.filter(is_active=True).order_by('username')
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated] # Any authenticated user can see the list
    filter_backends = [filters.SearchFilter]
    search_fields = ['username', 'first_name', 'last_name', 'email']

class SupplierViewSet(viewsets.ModelViewSet):
    """API endpoint that allows suppliers to be viewed or edited."""
    queryset = Supplier.objects.all().order_by("name")
    serializer_class = SupplierSerializer
    lookup_field = 'id' # Explicitly use the UUID field for lookups
    permission_classes = [permissions.IsAuthenticated] # Adjust permissions as needed
    # Add pagination, filtering, search if needed later
    # pagination_class = YourPaginationClass
    # filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    # filterset_fields = ['field1', 'field2']
    # search_fields = ['name', 'email']
