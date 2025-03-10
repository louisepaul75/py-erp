from rest_framework import viewsets, filters
from django_filters.rest_framework import DjangoFilterBackend
from .models import Customer, Address
from .serializers import CustomerSerializer, AddressSerializer

# Create your views here


class SalesViewSet(viewsets.ModelViewSet):
    """
    API viewset for sales-related models.
    This is a placeholder viewset - you'll need to implement your actual views.
    """


class CustomerViewSet(viewsets.ModelViewSet):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter
    ]
    filterset_fields = ['customer_group', 'delivery_block']
    search_fields = [
        'customer_number',
        'addresses__company_name',
        'addresses__first_name',
        'addresses__last_name',
        'addresses__email',
        'addresses__city'
    ]
    ordering_fields = ['customer_number', 'created_at', 'modified_at']
    ordering = ['-created_at']


class AddressViewSet(viewsets.ModelViewSet):
    queryset = Address.objects.all()
    serializer_class = AddressSerializer
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter
    ]
    filterset_fields = ['customer', 'is_primary', 'country']
    search_fields = [
        'company_name',
        'first_name',
        'last_name',
        'email',
        'city',
        'postal_code'
    ]
    ordering_fields = ['created_at', 'modified_at']
    ordering = ['-created_at']
