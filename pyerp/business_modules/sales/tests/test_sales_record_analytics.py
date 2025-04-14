"""
Tests for the SalesRecordViewSet analytics functionality.
"""
import datetime
from decimal import Decimal
import pytest
from django.conf import settings
from django.urls import reverse, include, path
from django.utils import timezone
from rest_framework.test import APIClient
from rest_framework.routers import DefaultRouter
from pyerp.business_modules.sales.views import SalesRecordViewSet
from pyerp.business_modules.sales.models import Customer, SalesRecord


# Mark all tests in this module as Django DB tests
pytestmark = pytest.mark.django_db


# Set up test URLs
router = DefaultRouter()
router.register(r'records', SalesRecordViewSet, basename='salesrecord')


urlpatterns = [
    path('api/', include(router.urls)),
]


# Override test settings
settings.ROOT_URLCONF = __name__


@pytest.fixture
def api_client():
    """Fixture for API client."""
    return APIClient()


@pytest.fixture
def setup_sales_data():
    """Fixture to create sample sales records across different years."""
    customer = Customer.objects.create(
        name="Test Customer", customer_number="CUST-001"
    )
    today = timezone.localdate()
    current_year = today.year
    prev_year = current_year - 1
    five_years_ago = current_year - 5

    # --- Current Year Data ---
    # Record for today
    SalesRecord.objects.create(
        customer=customer,
        record_type="INVOICE",
        record_number=f"INV-{current_year}-01",
        record_date=today,
        total_amount=Decimal("100.00"),
        payment_status="PAID",
    )
    # Record for first day of current month
    first_day_current_month = today.replace(day=1)
    SalesRecord.objects.create(
        customer=customer,
        record_type="INVOICE",
        record_number=f"INV-{current_year}-02",
        record_date=first_day_current_month,
        total_amount=Decimal("50.00"),
        payment_status="PAID",
    )
    # Record for yesterday (if not the first day)
    if today.day > 1:
        yesterday = today - datetime.timedelta(days=1)
        SalesRecord.objects.create(
            customer=customer,
            record_type="INVOICE",
            record_number=f"INV-{current_year}-03",
            record_date=yesterday,
            total_amount=Decimal("75.00"),
            payment_status="PENDING",
        )

    # --- Previous Year Data (Same month as today) ---
    prev_year_date_1 = first_day_current_month.replace(year=prev_year)
    SalesRecord.objects.create(
        customer=customer,
        record_type="INVOICE",
        record_number=f"INV-{prev_year}-01",
        record_date=prev_year_date_1,
        total_amount=Decimal("200.00"),
        payment_status="PAID",
    )
    # Add another record in the same month, previous year
    # Ensure second date is later in month
    if prev_year_date_1.day < 15:
        prev_year_date_2 = prev_year_date_1.replace(day=15)
        SalesRecord.objects.create(
            customer=customer,
            record_type="INVOICE",
            record_number=f"INV-{prev_year}-02",
            record_date=prev_year_date_2,
            total_amount=Decimal("250.00"),
            payment_status="PAID",
        )

    # --- 5 Years Ago Data (Same month as today) ---
    try:
        five_years_ago_date = first_day_current_month.replace(
            year=five_years_ago
        )
        SalesRecord.objects.create(
            customer=customer,
            record_type="INVOICE",
            record_number=f"INV-{five_years_ago}-01",
            record_date=five_years_ago_date,
            total_amount=Decimal("500.00"),
            payment_status="PAID",
        )
    except ValueError:
        # Handle cases like Feb 29 in a non-leap year 5 years ago
        pass

    # --- Data for other months/types (to ensure filtering works) ---
    # Previous month, current year
    if today.month > 1:
        prev_month_date = first_day_current_month.replace(
            month=today.month - 1
        )
        SalesRecord.objects.create(
            customer=customer,
            record_type="INVOICE",
            record_number=f"INV-{current_year}-OTHER",
            record_date=prev_month_date,
            total_amount=Decimal("1000.00"),
            payment_status="PAID",
        )
    # Different record type
    SalesRecord.objects.create(
        customer=customer,
        record_type="QUOTE",
        record_number=f"QT-{current_year}-01",
        record_date=today,
        total_amount=Decimal("50.00"),
        payment_status="DRAFT",
    )

    return {"customer": customer, "today": today}


@pytest.mark.backend
class TestSalesRecordViewSetAnalytics:
    """Tests for the analytics actions in SalesRecordViewSet."""

    def test_monthly_analysis_current_month(
        self,
        api_client,
        setup_sales_data
    ):
        """Test monthly_analysis for the current month and year."""
        today = setup_sales_data["today"]
        print(f"\nDebug: Today's date is {today}")
        
        # Check what records exist in the database
        from pyerp.business_modules.sales.models import SalesRecord
        prev_year = today.year - 1
        prev_year_records = SalesRecord.objects.filter(
            record_type="INVOICE",
            record_date__year=prev_year,
            record_date__month=today.month
        ).order_by('record_date')
        print("\nDebug: Previous year records:")
        for record in prev_year_records:
            print(
                f"  - Date: {record.record_date}, "
                f"Amount: {record.total_amount}"
            )
            
        url = reverse("salesrecord-monthly-analysis")

        # No params needed for current month/year
        response = api_client.get(url)

        assert response.status_code == 200
        data = response.json()

        # Check top-level structure
        assert "selected_period" in data
        assert "navigation" in data
        assert "data" in data

        # Check selected period
        assert data["selected_period"]["year"] == today.year
        assert data["selected_period"]["month"] == today.month
        assert "name" in data["selected_period"]  # e.g., "April 2024"

        # Check navigation
        assert "prev_year" in data["navigation"]
        assert "prev_month" in data["navigation"]
        assert "next_year" in data["navigation"]
        assert "next_month" in data["navigation"]
        assert data["navigation"]["is_current"] is True  # Should be current

        # Check data array structure (basic check)
        assert isinstance(data["data"], list)
        assert len(data["data"]) > 0  # Should have entries for days
        first_day_data = data["data"][0]
        assert "date" in first_day_data
        assert "daily" in first_day_data
        assert "cumulative" in first_day_data
        assert "cumulative_prev_year" in first_day_data
        assert "cumulative_avg_5_years" in first_day_data

        # --- Verification of calculated values (more detailed checks) ---

        # Find data for the first day of the month
        first_day_entry = next(
            (
                d
                for d in data["data"]
                if d["date"] == today.replace(day=1).isoformat()
            ),
            None,
        )
        assert first_day_entry is not None
        # Check daily total for first day
        assert first_day_entry["daily"] == pytest.approx(50.00)
        # Check cumulative for the first day
        assert first_day_entry["cumulative"] == pytest.approx(50.00)

        # Find data for today
        today_entry = next(
            (d for d in data["data"] if d["date"] == today.isoformat()),
            None
        )
        assert today_entry is not None
        # Check today's daily total
        assert today_entry["daily"] == pytest.approx(100.00)

        # Check cumulative value for today
        # Sum of all records in the current month up to today
        expected_cumulative = Decimal("0.00")
        if today.day == 1:
            # Day 1 + Today
            expected_cumulative = Decimal("50.00") + Decimal("100.00")
        elif today.day > 1:
            # Day 1 + Yesterday + Today
            expected_cumulative = (
                Decimal("50.00") + Decimal("75.00") + Decimal("100.00")
            )

        assert today_entry["cumulative"] == pytest.approx(
            float(expected_cumulative)
        )

        # Check cumulative previous year value for today's date's position
        # Sum of all records in the same month, previous year
        first_day_current_month = today.replace(day=1)
        # First day record always exists
        expected_prev_year_cumulative = Decimal("200.00")
        if first_day_current_month.day < 15:
            # Second record exists only if first day < 15
            expected_prev_year_cumulative += Decimal("250.00")
        assert today_entry["cumulative_prev_year"] == pytest.approx(
            float(expected_prev_year_cumulative)
        )

        # Check 5-year average cumulative for today's date's position
        # Only one record 5 years ago in this setup
        # Average over 1 year found
        expected_5_year_avg_cumulative = Decimal("500.00") / 1
        assert today_entry["cumulative_avg_5_years"] == pytest.approx(
            float(expected_5_year_avg_cumulative)
        )

        # Check that future days have daily=None but cumulative values
        # populated
        if today.day < 28:  # Avoid issues at month end for simplicity
            tomorrow_iso = (today + datetime.timedelta(days=1)).isoformat()
            tomorrow_entry = next(
                (d for d in data["data"] if d["date"] == tomorrow_iso),
                None
            )
            if tomorrow_entry:  # Might not exist if today is last day of month
                assert tomorrow_entry["daily"] is None
                # Cumulative should be same as today's if no record tomorrow
                assert (
                    tomorrow_entry["cumulative"] == today_entry["cumulative"]
                )

    def test_monthly_analysis_specific_month_year(
        self, api_client, setup_sales_data
    ):
        """Test monthly_analysis for specific month and year parameters."""
        today = setup_sales_data["today"]
        prev_year = today.year - 1
        # Use the same month as current for test data setup
        target_month = today.month

        url = reverse("salesrecord-monthly-analysis")
        response = api_client.get(
            url,
            {'year': prev_year, 'month': target_month}
        )

        assert response.status_code == 200
        data = response.json()

        # Check selected period
        assert data["selected_period"]["year"] == prev_year
        assert data["selected_period"]["month"] == target_month

        # Check navigation
        assert data["navigation"]["is_current"] is False  # Not current month

        # Check data array structure
        assert isinstance(data["data"], list)
        assert len(data["data"]) > 0

        # Find data for the first day of the month
        first_day_entry = next(
            (
                d
                for d in data["data"]
                if d["date"] == today.replace(
                    day=1, year=prev_year
                ).isoformat()
            ),
            None,
        )
        assert first_day_entry is not None
        # Check daily total for the first day
        assert first_day_entry["daily"] == pytest.approx(200.00)

    def test_monthly_analysis_invalid_params(self, api_client):
        """Test monthly_analysis with invalid parameters."""
        url = reverse("salesrecord-monthly-analysis")

        # Invalid month
        response = api_client.get(url, {'month': 13})
        assert response.status_code == 400
        assert "error" in response.json()
        assert "Month must be between 1 and 12" in response.json()["error"]

        # Invalid year format
        response = api_client.get(url, {'year': 'abc'})
        assert response.status_code == 400
        assert "error" in response.json()
        assert "Invalid month or year parameter" in response.json()["error"]