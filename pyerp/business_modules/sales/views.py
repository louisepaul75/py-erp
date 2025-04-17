from rest_framework import viewsets, filters
from django_filters.rest_framework import DjangoFilterBackend
from .models import Customer, Address, SalesRecord, SalesRecordItem, SalesRecordRelationship
from .serializers import (
    CustomerSerializer,
    AddressSerializer,
    SalesRecordSerializer,
    SalesRecordItemSerializer
)
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models.functions import TruncDay, TruncMonth
from django.utils import timezone
from django.db.models import Prefetch, Count, Sum, Q, Value, DecimalField, Max
from django.db.models.functions import Coalesce
from django.shortcuts import render

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

    serializer_class = CustomerSerializer
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_fields = {
        "id": ["exact", "in"],
        "customer_group": ["exact"],
        "delivery_block": ["exact"],
    }
    search_fields = ["name", "customer_number", "email"]
    ordering_fields = ["name", "customer_number", "created_at"]

    def get_queryset(self):
        """
        Optimize queryset to prefetch primary address and annotate related data.
        """
        queryset = Customer.objects.all().prefetch_related(
            # Prefetch only the primary address into a predictable attribute
            Prefetch(
                'addresses',
                queryset=Address.objects.filter(is_primary=True),
                to_attr='primary_address_list'  # Use a list attribute
            )
        ).annotate(
            # Calculate order count (adjust if only certain record types count)
            order_count=Count('sales_records'),
            # Calculate total spent (sum of INVOICE totals,
            # default to 0.00 if none)
            # Ensure the output field type is DecimalField
            total_spent=Coalesce(
                Sum(
                    'sales_records__total_amount',
                    filter=Q(sales_records__record_type='INVOICE')
                ),
                Value(0.0),
                output_field=DecimalField()
            ),
            # Get the date of the last sales record
            last_order_date=Max('sales_records__record_date')
        ).order_by(
            '-created_at'
        )  # Default ordering, can be overridden by OrderingFilter

        # Adjust search_fields if email is only on Address - requires
        # more complex filtering
        # For now, assuming Customer.email might exist or search needs
        # adjustment
        # Example adjustment (if Customer doesn't have email directly):
        # self.search_fields = [
        #     "name", "customer_number", "addresses__email"
        # ]

        return queryset


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
        
    @action(detail=True, methods=['get'], url_path='flow-data')
    def flow_data(self, request, pk=None):
        """
        Retrieve data formatted for React Flow visualization, showing the
        target SalesRecord and its direct relationships (incoming/outgoing).
        """
        try:
            record = self.get_object()
        except SalesRecord.DoesNotExist:
            return Response({"error": "SalesRecord not found."}, status=404)

        nodes = []
        edges = []
        processed_record_ids = set()  # Keep track to avoid duplicate nodes

        # Function to add a node if not already added
        def add_node(sales_record):
            if sales_record.pk not in processed_record_ids:
                nodes.append({
                    'id': f'record_{sales_record.pk}',
                    'type': 'salesRecordNode', # Or your preferred node type
                    'position': {'x': 0, 'y': 0}, # Initial position
                    'data': {
                        'pk': sales_record.pk,
                        'record_number': sales_record.record_number,
                        'record_type': sales_record.get_record_type_display(),
                        'record_date': sales_record.record_date,
                        'total_amount': sales_record.total_amount,
                        'delivery_status': sales_record.get_delivery_status_display(),
                        # Add other relevant data for the node display
                    }
                })
                processed_record_ids.add(sales_record.pk)

        # Add the central node
        add_node(record)

        # Get outgoing relationships (relationships FROM this record)
        outgoing_rels = SalesRecordRelationship.objects.filter(
            from_record=record
        ).select_related(
            'to_record'
        )  # Optimize query

        for rel in outgoing_rels:
            related_record = rel.to_record
            add_node(related_record) # Add the related node

            edges.append({
                'id': f'rel_{rel.pk}',
                'source': f'record_{record.pk}', # Source is the main record
                'target': f'record_{related_record.pk}', # Target is the related record
                'type': 'relationshipEdge', # Or your preferred edge type
                'label': rel.get_relationship_type_display(), # Optional label
                'data': {
                    'pk': rel.pk,
                    'relationship_type': rel.relationship_type,
                }
            })

        # Get incoming relationships (relationships TO this record)
        incoming_rels = SalesRecordRelationship.objects.filter(
            to_record=record
        ).select_related(
            'from_record'
        )  # Optimize query

        for rel in incoming_rels:
            related_record = rel.from_record
            add_node(related_record) # Add the related node

            edges.append({
                'id': f'rel_{rel.pk}',
                'source': f'record_{related_record.pk}', # Source is the related record
                'target': f'record_{record.pk}', # Target is the main record
                'type': 'relationshipEdge', # Or your preferred edge type
                'label': rel.get_relationship_type_display(), # Optional label
                'data': {
                    'pk': rel.pk,
                    'relationship_type': rel.relationship_type,
                }
            })

        return Response({'nodes': nodes, 'edges': edges})

    @action(detail=False, methods=["get"])
    def monthly_analysis(self, request):
        """
        Get sales data for a specific month aggregated by day.
        Returns daily sales and cumulative sum for INVOICE records.
        Also includes cumulative data for the previous year and the 5-year
        average.

        Query Parameters:
        - month: Integer (1-12) representing the month to get data for.
                 Defaults to current month.
        - year: Integer representing the year. Defaults to current year.
        """
        import datetime
        from django.db.models import Sum

        # Parse month and year from query parameters
        today = timezone.localdate()  # Use timezone aware date
        try:
            month = int(request.query_params.get('month', today.month))
            year = int(request.query_params.get('year', today.year))

            if month < 1 or month > 12:
                return Response(
                    {"error": "Month must be between 1 and 12"}, status=400
                )

            start_date = datetime.date(year, month, 1)
            if month == 12:
                end_date = datetime.date(year + 1, 1, 1) - datetime.timedelta(
                    days=1
                )
            else:
                end_date = datetime.date(
                    year, month + 1, 1
                ) - datetime.timedelta(days=1)

        except ValueError:
            return Response(
                {"error": "Invalid month or year parameter"}, status=400
            )

        # Helper function to get cumulative daily data for a given period
        def get_cumulative_daily_data(target_year, target_month):
            try:
                period_start_date = datetime.date(target_year, target_month, 1)
                if target_month == 12:
                    period_end_date = datetime.date(
                        target_year + 1, 1, 1
                    ) - datetime.timedelta(days=1)
                else:
                    period_end_date = datetime.date(
                        target_year, target_month + 1, 1
                    ) - datetime.timedelta(days=1)
            except ValueError:  # Handle invalid dates like Feb 30
                return {}, 0

            records = self.queryset.filter(
                record_type="INVOICE",
                record_date__gte=period_start_date,
                record_date__lte=period_end_date
            )
            daily_sales = (
                records.annotate(day=TruncDay('record_date'))
                .values('day')
                .annotate(total=Sum('total_amount'))
                .order_by('day')
            )

            print("\nDebug: Daily sales query results:")
            for entry in daily_sales:
                print(
                    f"  - Day: {entry['day']}, "
                    f"Total: {entry['total']}"
                )

            daily_totals = {
                entry['day'].day: float(entry['total'] or 0)
                for entry in daily_sales
            }

            print("\nDebug: Daily totals dictionary:")
            for day, total in daily_totals.items():
                print(f"  - Day {day}: {total}")

            cumulative_data = {}
            cumulative_sum = 0
            num_days = (period_end_date - period_start_date).days + 1
            
            print(f"\nDebug: Calculating cumulative for {num_days} days")
            for day_num in range(1, num_days + 1):
                daily_total = daily_totals.get(day_num, 0)
                cumulative_sum += daily_total
                cumulative_data[day_num] = cumulative_sum
                print(
                    f"  - Day {day_num}: "
                    f"Daily={daily_total}, "
                    f"Cumulative={cumulative_sum}"
                )
                
            return cumulative_data, num_days

        # --- Current Period ---
        current_cumulative_data, num_days_current = get_cumulative_daily_data(
            year, month
        )
        # Get daily totals for the current period separately for the 'daily'
        # field
        current_records = self.queryset.filter(
            record_type="INVOICE",
            record_date__gte=start_date,
            record_date__lte=end_date
        )
        current_daily_sales_agg = (
            current_records.annotate(day=TruncDay('record_date'))
            .values('day')
            .annotate(total=Sum('total_amount'))
            .order_by('day')
        )
        current_daily_totals = {
            entry['day'].day: float(entry['total'] or 0)
            for entry in current_daily_sales_agg
        }

        # --- Previous Year ---
        prev_year_cumulative_data, _ = get_cumulative_daily_data(
            year - 1, month
        )

        # --- 5-Year Average ---
        past_5_years_cumulative = {}  # {day_num: [cumulative1, ...]}
        valid_years_count = {}  # {day_num: count}

        # Ensure we check date validity for each year (e.g., leap years)
        # Add try-except block for earliest record query
        try:
            min_record = self.queryset.filter(record_type="INVOICE").earliest(
                'record_date'
            )
            min_year_in_db = min_record.record_date.year
        except SalesRecord.DoesNotExist:
            # If no records exist, set min_year to current year to avoid issues
            min_year_in_db = year

        # Start from year-5 or earliest data, whichever is later
        earliest_possible_year = max(year - 5, min_year_in_db)

        for i in range(1, 6):
            target_year = year - i
            # Stop if we go before the earliest possible year
            if target_year < earliest_possible_year:
                break  # Changed from continue for clarity and efficiency

            past_cumulative, num_days_past = get_cumulative_daily_data(
                target_year, month
            )
            for day_num in range(1, num_days_past + 1):
                cumulative_val = past_cumulative.get(day_num, 0)
                if day_num not in past_5_years_cumulative:
                    past_5_years_cumulative[day_num] = []
                    valid_years_count[day_num] = 0
                past_5_years_cumulative[day_num].append(cumulative_val)
                valid_years_count[day_num] += 1

        avg_5_years_cumulative_data = {}
        for day_num, values in past_5_years_cumulative.items():
            count = valid_years_count.get(day_num, 0)
            if count > 0:
                avg_5_years_cumulative_data[day_num] = sum(values) / count
            else:
                avg_5_years_cumulative_data[day_num] = 0  # Default to 0

        # --- Combine Data ---
        data = []
        num_days_in_month = (end_date - start_date).days + 1

        for day_num in range(1, num_days_in_month + 1):
            current_day_date = start_date + datetime.timedelta(
                days=day_num - 1
            )
            day_iso = current_day_date.isoformat()

            # Explicitly initialize comparison values
            cumulative_prev_year_value = None
            cumulative_avg_5_years_value = None

            # Get pre-calculated cumulative values directly using day_num
            cumulative_value = current_cumulative_data.get(day_num, 0)
            cumulative_prev_year_value = prev_year_cumulative_data.get(day_num, 0)
            cumulative_avg_5_years_value = avg_5_years_cumulative_data.get(
                day_num, 0
            )

            # Only get daily value if the date is not in the future
            daily_value = None
            if current_day_date <= today:
                daily_value = current_daily_totals.get(day_num, 0)
            # Note: Cumulative values remain populated even for future dates,
            # relying on connectNulls=true in the frontend if a gap truly
            # exists in source data.

            data.append({
                'date': day_iso,
                'daily': daily_value,
                'cumulative': cumulative_value,
                'cumulative_prev_year': cumulative_prev_year_value,
                'cumulative_avg_5_years': cumulative_avg_5_years_value
            })

        # Get month name in German format
        month_name = start_date.strftime('%B %Y')

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
            'selected_period': {  # Changed from selected_month
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
        Also includes cumulative data for the previous year and the 5-year
        average.

        Query Parameters:
        - year: Integer representing the year. Defaults to current year.
        """
        import datetime
        from django.db.models import Sum

        today = timezone.localdate()
        try:
            year = int(request.query_params.get('year', today.year))
            start_date = datetime.date(year, 1, 1)
            end_date = datetime.date(year, 12, 31)
        except ValueError:
            return Response({"error": "Invalid year parameter"}, status=400)

        # Helper function to get cumulative monthly data for a given year
        def get_cumulative_monthly_data(target_year):
            period_start_date = datetime.date(target_year, 1, 1)
            period_end_date = datetime.date(target_year, 12, 31)

            records = self.queryset.filter(
                record_type="INVOICE",
                record_date__gte=period_start_date,
                record_date__lte=period_end_date
            )
            monthly_sales = (
                records.annotate(month=TruncMonth('record_date'))
                .values('month')
                .annotate(total=Sum('total_amount'))
                .order_by('month')
            )

            # Map month number (1-12) to total
            monthly_totals = {
                entry['month'].month: float(entry['total'] or 0)
                for entry in monthly_sales
            }

            cumulative_data = {}
            cumulative_sum = 0
            for month_num in range(1, 13):
                monthly_total = monthly_totals.get(month_num, 0)
                cumulative_sum += monthly_total
                cumulative_data[month_num] = cumulative_sum
            return cumulative_data

        # --- Current Period ---
        current_cumulative_data = get_cumulative_monthly_data(year)
        # Get monthly totals for the current period separately for the 'daily'
        # field (renamed to monthly_total for clarity)
        current_records = self.queryset.filter(
            record_type="INVOICE",
            record_date__gte=start_date,
            record_date__lte=end_date
        )
        current_monthly_sales_agg = (
            current_records.annotate(month=TruncMonth('record_date'))
            .values('month')
            .annotate(total=Sum('total_amount'))
            .order_by('month')
        )
        current_monthly_totals = {
            entry['month'].month: float(entry['total'] or 0)
            for entry in current_monthly_sales_agg
        }

        # --- Previous Year ---
        prev_year_cumulative_data = get_cumulative_monthly_data(year - 1)

        # --- 5-Year Average ---
        past_5_years_cumulative = {}  # {month_num: [cumulative1, ...]}
        valid_years_count = {}  # {month_num: count}

        # Add try-except block for earliest record query
        try:
            min_record = self.queryset.filter(record_type="INVOICE").earliest(
                'record_date'
            )
            min_year_in_db = min_record.record_date.year
        except SalesRecord.DoesNotExist:
            # If no records exist, set min_year to current year
            min_year_in_db = year

        # Start from year-5 or earliest data, whichever is later
        earliest_possible_year = max(year - 5, min_year_in_db)

        for i in range(1, 6):
            target_year = year - i
            # Stop if we go before the earliest possible year
            if target_year < earliest_possible_year:
                break  # Changed from continue for clarity
            
            past_cumulative = get_cumulative_monthly_data(target_year)
            for month_num in range(1, 13):
                cumulative_val = past_cumulative.get(month_num, 0)
                if month_num not in past_5_years_cumulative:
                    past_5_years_cumulative[month_num] = []
                    valid_years_count[month_num] = 0
                past_5_years_cumulative[month_num].append(cumulative_val)
                valid_years_count[month_num] += 1

        avg_5_years_cumulative_data = {}
        for month_num, values in past_5_years_cumulative.items():
            count = valid_years_count.get(month_num, 0)
            if count > 0:
                avg_5_years_cumulative_data[month_num] = sum(values) / count
            else:
                avg_5_years_cumulative_data[month_num] = 0

        # --- Combine Data ---
        data = []
        for month_num in range(1, 13):
            # Date represents the start of the month for consistency
            current_month_start_date = datetime.date(year, month_num, 1)
            month_iso = current_month_start_date.isoformat()

            # Explicitly initialize comparison values
            cumulative_prev_year_value = None
            cumulative_avg_5_years_value = None

            # Get pre-calculated cumulative values directly using month_num
            cumulative_value = current_cumulative_data.get(month_num, 0)
            cumulative_prev_year_value = prev_year_cumulative_data.get(
                month_num, 0  # Default to 0 if not found for prev year
            )
            cumulative_avg_5_years_value = avg_5_years_cumulative_data.get(
                month_num, 0  # Default to 0 if not found for 5yr avg
            )

            # In annual view, 'daily' represents the total for the month
            # Only get monthly total if the month is not in the future
            monthly_total_value = None
            # Use <= comparison to include the current month fully
            is_future_month = (
                current_month_start_date.replace(day=1)
                > today.replace(day=1)
            )
            if not is_future_month:
                monthly_total_value = current_monthly_totals.get(month_num, 0)
            # Set cumulative value to None for future months
            else:
                cumulative_value = None  # Set to None for future months

            data.append({
                'date': month_iso,  # Use start of month date for X-axis
                'daily': monthly_total_value,  # Represents the total for the month
                'cumulative': cumulative_value,
                'cumulative_prev_year': cumulative_prev_year_value,
                'cumulative_avg_5_years': cumulative_avg_5_years_value
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


# New view for Sales Flow placeholder
def sales_flow_view(request):
    """
    Placeholder view for the Sales Flow page.
    """
    context = {
        'page_title': 'Sales Flow',  # Example context
        'content': 'This is the placeholder for the Sales Flow page.'
    }
    # Assuming the template will be in sales/templates/sales/sales_flow.html
    return render(request, 'sales/sales_flow.html', context)
