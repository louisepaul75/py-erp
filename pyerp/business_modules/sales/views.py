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
        Get sales data for a specific month aggregated by day.
        Returns daily sales and cumulative sum for INVOICE records.
        
        Query Parameters:
        - month: Integer (1-12) representing the month to get data for. Defaults to current month.
        - year: Integer representing the year. Defaults to current year.
        """
        import datetime
        from django.db.models import Sum
        from django.db.models.functions import TruncDay
        from collections import OrderedDict
        
        # Parse month and year from query parameters
        today = datetime.date.today()
        try:
            month = int(request.query_params.get('month', today.month))
            year = int(request.query_params.get('year', today.year))
            
            # Validate month value
            if month < 1 or month > 12:
                return Response(
                    {"error": "Month must be between 1 and 12"}, 
                    status=400
                )
            
            # Set start date to first day of requested month/year
            start_date = datetime.date(year, month, 1)
            
            # Calculate end date (last day of month)
            if month == 12:
                end_date = datetime.date(year + 1, 1, 1) - datetime.timedelta(days=1)
            else:
                end_date = datetime.date(year, month + 1, 1) - datetime.timedelta(days=1)
                
        except ValueError:
            return Response(
                {"error": "Invalid month or year parameter"}, 
                status=400
            )
        
        # Get invoice records for requested month
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
            current_day_date = datetime.date.fromisoformat(day)
            if current_day_date > today:
                # Set future values to None
                daily_value = None
                cumulative_value = None
            else:
                daily_value = values['total']
                cumulative += daily_value
                cumulative_value = cumulative
                
            data.append({
                'date': day,
                'daily': daily_value, 
                'cumulative': cumulative_value
            })
        
        # Get month name in German format
        month_name = datetime.date(year, month, 1).strftime('%B %Y')
        
        # Add information about previous and next months for navigation
        prev_month = month - 1
        prev_year = year
        if prev_month < 1:
            prev_month = 12
            prev_year = year - 1
            
        next_month = month + 1
        next_year = year
        if next_month > 12:
            next_month = 1
            next_year = year + 1
            
        return Response({
            'selected_month': {
                'start_date': start_date.isoformat(),
                'end_date': end_date.isoformat(),
                'name': month_name,
                'month': month,
                'year': year
            },
            'navigation': {
                'prev_month': prev_month,
                'prev_year': prev_year,
                'next_month': next_month,
                'next_year': next_year,
                'is_current': month == today.month and year == today.year
            },
            'data': data
        })

    @action(detail=False, methods=["get"])
    def annual_analysis(self, request):
        """
        Get sales data for a specific year aggregated by month.
        Returns monthly sales and cumulative sum for INVOICE records.
        
        Query Parameters:
        - year: Integer representing the year. Defaults to current year.
        """
        import datetime
        from django.db.models import Sum
        from django.db.models.functions import TruncMonth
        from collections import OrderedDict
        
        # Parse year from query parameters
        today = datetime.date.today()
        try:
            year = int(request.query_params.get('year', today.year))
            
            # Set start and end dates for the year
            start_date = datetime.date(year, 1, 1)
            end_date = datetime.date(year, 12, 31)
                
        except ValueError:
            return Response(
                {"error": "Invalid year parameter"}, 
                status=400
            )
        
        # Get invoice records for requested year
        invoice_records = self.queryset.filter(
            record_type="INVOICE",
            record_date__gte=start_date,
            record_date__lte=end_date
        )
        
        # Aggregate by month
        monthly_sales = invoice_records.annotate(
            month=TruncMonth('record_date')
        ).values('month').annotate(
            total=Sum('total_amount')
        ).order_by('month')
        
        # Generate all months in the year
        all_months = OrderedDict()
        for month_num in range(1, 13):
            month_start = datetime.date(year, month_num, 1)
            all_months[month_start.isoformat()] = {'month': month_start.isoformat(), 'total': 0}
        
        # Fill in actual data
        for entry in monthly_sales:
            month_iso = entry['month'].isoformat()
            if month_iso in all_months:
                all_months[month_iso]['total'] = float(entry['total']) if entry['total'] else 0
        
        # Calculate cumulative sum
        data = []
        cumulative = 0
        for month_date_str, values in all_months.items():
            current_month_start_date = datetime.date.fromisoformat(month_date_str)
            # Check if the entire month is in the future
            if current_month_start_date > today:
                daily_value = None
                cumulative_value = None
            else:
                daily_value = values['total']
                cumulative += daily_value
                cumulative_value = cumulative
            
            data.append({
                'date': month_date_str,  # Keep 'date' key for consistency with frontend
                'daily': daily_value, # Rename 'monthly' to 'daily' for consistency
                'cumulative': cumulative_value
            })
            
        # Navigation info
        prev_year = year - 1
        next_year = year + 1
            
        return Response({
            'selected_period': {
                'year': year
            },
            'navigation': {
                'prev_year': prev_year,
                'next_year': next_year,
                'is_current': year == today.year
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
