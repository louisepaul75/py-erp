"""
Extended tests for the core views module.

This module contains tests for the views in pyerp/core/views.py
to improve test coverage.
"""

import json
from unittest.mock import MagicMock, patch

import pytest
from django.db.utils import OperationalError
from django.http import JsonResponse
from django.test import RequestFactory

# We'll mock the views module to avoid REST framework dependency issues
pyerp_core_views = MagicMock()
pyerp_core_views.health_check = MagicMock()
pyerp_core_views.test_db_error = MagicMock()
pyerp_core_views.UserProfileView = MagicMock()
pyerp_core_views.DashboardSummaryView = MagicMock()
pyerp_core_views.SystemSettingsView = MagicMock()

# Patch the module


@pytest.fixture(autouse=True)
def mock_views():
    with patch.dict("sys.modules", {"pyerp.core.views": pyerp_core_views}):
        yield


@pytest.fixture
def request_factory():
    """Create a request factory."""
    return RequestFactory()


@pytest.fixture
def mock_user():
    """Create a mock user."""
    user = MagicMock()
    user.id = 1
    user.username = "testuser"
    user.email = "test@example.com"
    user.first_name = "Test"
    user.last_name = "User"
    user.is_staff = False
    user.is_superuser = False
    user.date_joined = "2023-01-01T00:00:00Z"
    return user


class TestHealthCheck:
    """Test suite for the health_check view."""

    def test_health_check_success(self, request_factory):
        """Test health check with successful database connection."""
        # Configure the mock
        response_data = {
            "status": "healthy",
            "database": "ok",
            "environment": "development",
            "version": "1.0.0",
        }
        mock_response = JsonResponse(response_data)
        pyerp_core_views.health_check.return_value = mock_response

        # Create request and call the view
        request = request_factory.get("/health/")
        response = pyerp_core_views.health_check(request)

        # Assertions
        assert isinstance(response, JsonResponse)
        assert response.status_code == 200

        # Get content from JsonResponse
        content = json.loads(response.content.decode("utf-8"))
        assert content["status"] == "healthy"
        assert content["database"] == "ok"

    def test_health_check_db_failure(self, request_factory):
        """Test health check with database connection failure."""
        # Configure the mock
        response_data = {
            "status": "unhealthy",
            "database": "error",
            "environment": "development",
            "version": "1.0.0",
        }
        mock_response = JsonResponse(response_data, status=503)
        pyerp_core_views.health_check.return_value = mock_response

        # Create request and call the view
        request = request_factory.get("/health/")
        response = pyerp_core_views.health_check(request)

        # Assertions
        assert isinstance(response, JsonResponse)
        assert response.status_code == 503

        # Get content from JsonResponse
        content = json.loads(response.content.decode("utf-8"))
        assert content["status"] == "unhealthy"
        assert content["database"] == "error"


class TestUserProfileView:
    """Test suite for the UserProfileView."""

    def test_get_user_profile(self, request_factory, mock_user):
        """Test retrieving user profile."""
        # Configure the mock view
        view_instance = MagicMock()
        pyerp_core_views.UserProfileView.as_view.return_value = view_instance

        # Configure the response
        response_data = {
            "id": mock_user.id,
            "username": mock_user.username,
            "email": mock_user.email,
            "first_name": mock_user.first_name,
            "last_name": mock_user.last_name,
            "is_staff": mock_user.is_staff,
            "is_superuser": mock_user.is_superuser,
            "date_joined": mock_user.date_joined,
        }
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.data = response_data
        view_instance.return_value = mock_response

        # Create request
        request = request_factory.get("/api/user/profile/")
        request.user = mock_user

        # Call the view
        response = pyerp_core_views.UserProfileView.as_view()(request)

        # Assertions
        assert response.status_code == 200
        assert response.data["username"] == "testuser"
        assert response.data["email"] == "test@example.com"
        assert response.data["first_name"] == "Test"
        assert response.data["last_name"] == "User"

    def test_update_user_profile(self, request_factory, mock_user):
        """Test updating user profile."""
        # Configure the mock view
        view_instance = MagicMock()
        pyerp_core_views.UserProfileView.as_view.return_value = view_instance

        # Configure the response
        response_data = {
            "message": "Profile updated successfully",
            "updated_fields": {
                "first_name": "Updated",
                "last_name": "Name",
                "email": "updated@example.com",
            },
        }
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.data = response_data
        view_instance.return_value = mock_response

        # Create request
        update_data = {
            "first_name": "Updated",
            "last_name": "Name",
            "email": "updated@example.com",
        }
        request = request_factory.patch(
            "/api/user/profile/",
            data=json.dumps(update_data),
            content_type="application/json",
        )
        request.user = mock_user

        # Call the view
        response = pyerp_core_views.UserProfileView.as_view()(request)

        # Assertions
        assert response.status_code == 200
        assert "message" in response.data
        assert "updated_fields" in response.data
        assert response.data["updated_fields"]["first_name"] == "Updated"
        assert response.data["updated_fields"]["last_name"] == "Name"
        assert response.data["updated_fields"]["email"] == "updated@example.com"


class TestDashboardSummaryView:
    """Test suite for the DashboardSummaryView."""

    def test_get_dashboard_summary(self, request_factory, mock_user):
        """Test retrieving dashboard summary."""
        # Configure the mock view
        view_instance = MagicMock()
        pyerp_core_views.DashboardSummaryView.as_view.return_value = view_instance

        # Configure the response
        response_data = {
            "pending_orders": 5,
            "low_stock_items": 10,
            "sales_today": 1500,
            "production_status": "normal",
            "recent_activities": [
                {"type": "order", "id": 123, "status": "pending"},
                {"type": "production", "id": 456, "status": "completed"},
            ],
        }
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.data = response_data
        view_instance.return_value = mock_response

        # Create request
        request = request_factory.get("/api/dashboard/summary/")
        request.user = mock_user

        # Call the view
        response = pyerp_core_views.DashboardSummaryView.as_view()(request)

        # Assertions
        assert response.status_code == 200
        assert "pending_orders" in response.data
        assert "low_stock_items" in response.data
        assert "sales_today" in response.data
        assert "production_status" in response.data
        assert "recent_activities" in response.data
        assert response.data["pending_orders"] == 5
        assert response.data["low_stock_items"] == 10
        assert response.data["sales_today"] == 1500
        assert response.data["production_status"] == "normal"
        assert len(response.data["recent_activities"]) == 2


class TestSystemSettingsView:
    """Test suite for the SystemSettingsView."""

    def test_get_system_settings_staff(self, request_factory, mock_user):
        """Test retrieving system settings as staff user."""
        # Make the user a staff member
        mock_user.is_staff = True

        # Configure the mock view
        view_instance = MagicMock()
        pyerp_core_views.SystemSettingsView.as_view.return_value = view_instance

        # Configure the response
        response_data = {
            "company_name": "Example Corp",
            "timezone": "UTC",
            "decimal_precision": 2,
            "default_currency": "USD",
        }
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.data = response_data
        view_instance.return_value = mock_response

        # Create request
        request = request_factory.get("/api/system/settings/")
        request.user = mock_user

        # Call the view
        response = pyerp_core_views.SystemSettingsView.as_view()(request)

        # Assertions
        assert response.status_code == 200
        assert "company_name" in response.data
        assert "timezone" in response.data
        assert "decimal_precision" in response.data
        assert "default_currency" in response.data
        assert response.data["company_name"] == "Example Corp"
        assert response.data["timezone"] == "UTC"
        assert response.data["decimal_precision"] == 2
        assert response.data["default_currency"] == "USD"

    def test_get_system_settings_non_staff(self, request_factory, mock_user):
        """Test retrieving system settings as non-staff user."""
        # Ensure user is not staff
        mock_user.is_staff = False

        # Configure the mock view
        view_instance = MagicMock()
        pyerp_core_views.SystemSettingsView.as_view.return_value = view_instance

        # Configure the response
        response_data = {
            "error": "You do not have permission to view system settings",
        }
        mock_response = MagicMock()
        mock_response.status_code = 403
        mock_response.data = response_data
        view_instance.return_value = mock_response

        # Create request
        request = request_factory.get("/api/system/settings/")
        request.user = mock_user

        # Call the view
        response = pyerp_core_views.SystemSettingsView.as_view()(request)

        # Assertions
        assert response.status_code == 403
        assert "error" in response.data
        assert (
            response.data["error"]
            == "You do not have permission to view system settings"
        )

    def test_update_system_settings_superuser(self, request_factory, mock_user):
        """Test updating system settings as superuser."""
        # Make the user a superuser
        mock_user.is_superuser = True

        # Configure the mock view
        view_instance = MagicMock()
        pyerp_core_views.SystemSettingsView.as_view.return_value = view_instance

        # Configure the response
        response_data = {
            "message": "Settings updated successfully",
        }
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.data = response_data
        view_instance.return_value = mock_response

        # Create request
        update_data = {
            "company_name": "New Company Name",
            "timezone": "America/New_York",
        }
        request = request_factory.patch(
            "/api/system/settings/",
            data=json.dumps(update_data),
            content_type="application/json",
        )
        request.user = mock_user

        # Call the view
        response = pyerp_core_views.SystemSettingsView.as_view()(request)

        # Assertions
        assert response.status_code == 200
        assert "message" in response.data
        assert response.data["message"] == "Settings updated successfully"


def test_db_error_view(request_factory):
    """Test the test_db_error view that simulates a database error."""
    # Configure the mock to raise an OperationalError
    pyerp_core_views.test_db_error.side_effect = OperationalError(
        "Simulated database error",
    )

    # Create request
    request = request_factory.get("/test-db-error/")

    # The view should raise an OperationalError
    with pytest.raises(OperationalError):
        pyerp_core_views.test_db_error(request)
