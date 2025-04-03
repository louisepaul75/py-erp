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
        
    @action(detail=False, methods=["get"])
    def monthly_analysis(self, request):
        """
        Get sales data for the current month aggregated by day.
        Returns daily sales and cumulative sum for INVOICE records.
        """
        import datetime
        from django.db.models import Sum
        from django.db.models.functions import TruncDay
        from collections import OrderedDict
        
        # Get current month
        today = datetime.date.today()
        start_date = today.replace(day=1)
        if today.month == 12:
            end_date = datetime.date(today.year + 1, 1, 1) - datetime.timedelta(days=1)
        else:
            end_date = datetime.date(today.year, today.month + 1, 1) - datetime.timedelta(days=1)
        
        # Get invoice records for current month
        invoice_records = self.queryset.filter(
            record_type="INVOICE",
            record_date__gte=start_date,
            record_date__lte=end_date
        )
        
        # Aggregate by day
        daily_sales = invoice_records.annotate(
            day=TruncDay('record_date')
        ).values('day').annotate(
            total=Sum('total_amount')
        ).order_by('day')
        
        # Generate all days in the month
        all_days = OrderedDict()
        current_date = start_date
        while current_date <= end_date:
            all_days[current_date.isoformat()] = {'day': current_date.isoformat(), 'total': 0}
            current_date += datetime.timedelta(days=1)
        
        # Fill in actual data
        for entry in daily_sales:
            day_iso = entry['day'].isoformat()
            if day_iso in all_days:
                all_days[day_iso]['total'] = float(entry['total']) if entry['total'] else 0
        
        # Calculate cumulative sum
        data = []
        cumulative = 0
        for day, values in all_days.items():
            cumulative += values['total']
            data.append({
                'date': day,
                'daily': values['total'],
                'cumulative': cumulative
            })
        
        return Response({
            'current_month': {
                'start_date': start_date.isoformat(),
                'end_date': end_date.isoformat(),
                'name': today.strftime('%B %Y')
            },
            'data': data
        })


class SalesRecordItemViewSet(viewsets.ModelViewSet):
    """
    API viewset for managing sales record items.
    """

    queryset = SalesRecordItem.objects.all()
    serializer_class = SalesRecordItemSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["sales_record", "fulfillment_status"]
