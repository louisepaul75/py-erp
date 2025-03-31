from rest_framework import viewsets, filters
from django_filters.rest_framework import DjangoFilterBackend
from .models import Customer, Address, SalesRecord, SalesRecordItem
from .serializers import (
    CustomerSerializer,
    AddressSerializer,
    SalesRecordSerializer,
    SalesRecordItemSerializer,
)
from rest_framework.decorators import action
from rest_framework.response import Response

# Create your views here


class SalesViewSet(viewsets.ModelViewSet):
    """
    API viewset for sales-related models.
    This is a placeholder viewset - you'll need to implement your actual views.
    """


class CustomerViewSet(viewsets.ModelViewSet):
    """
    API viewset for managing customers.
    """

    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_fields = ["customer_group", "delivery_block"]
    search_fields = ["name", "customer_number", "email"]
    ordering_fields = ["name", "customer_number", "created_at"]


class AddressViewSet(viewsets.ModelViewSet):
    """
    API viewset for managing addresses.
    """

    queryset = Address.objects.all()
    serializer_class = AddressSerializer


class SalesRecordViewSet(viewsets.ModelViewSet):
    """
    API viewset for managing sales records.
    """

    queryset = SalesRecord.objects.all().order_by("-record_date")
    serializer_class = SalesRecordSerializer
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_fields = ["record_type", "payment_status", "customer"]
    search_fields = ["record_number", "customer__name"]
    ordering_fields = ["record_date", "record_number", "total_amount"]

    @action(detail=True, methods=["get"])
    def items(self, request, pk=None):
        """Get items for a specific sales record."""
        record = self.get_object()
        items = record.line_items.all()
        serializer = SalesRecordItemSerializer(items, many=True)
        return Response(serializer.data)


class SalesRecordItemViewSet(viewsets.ModelViewSet):
    """
    API viewset for managing sales record items.
    """

    queryset = SalesRecordItem.objects.all()
    serializer_class = SalesRecordItemSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["sales_record", "fulfillment_status"]
