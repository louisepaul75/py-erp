from django.shortcuts import render
from rest_framework import viewsets, permissions, filters
from django_filters.rest_framework import DjangoFilterBackend

from .models import Employee
from .serializers import EmployeeSerializer

# Create your views here.

class EmployeeViewSet(viewsets.ModelViewSet):
    """API endpoint that allows employees to be viewed or edited."""
    queryset = Employee.objects.all().order_by('last_name', 'first_name')
    serializer_class = EmployeeSerializer
    permission_classes = [permissions.IsAuthenticated] # Adjust permissions as needed
    
    # Add filtering and searching capabilities
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['is_active', 'is_terminated', 'is_present'] # Fields for exact match filtering
    search_fields = ['employee_number', 'first_name', 'last_name', 'email', 'ad_username'] # Fields for text search
    ordering_fields = ['last_name', 'first_name', 'employee_number', 'hire_date', 'created_at'] # Fields allowed for ordering
    ordering = ['last_name', 'first_name'] # Default ordering
