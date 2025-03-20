"""
Unit tests for core system health checks.
"""

from unittest.mock import MagicMock, patch

import pytest
from django.core.checks import Warning
from django.db.utils import DatabaseError, InterfaceError, OperationalError

from pyerp.core.checks import check_database_connection


def test_check_database_connection_success():
    """Test database connection check when connection is successful."""
    with patch("pyerp.core.checks.connections") as mock_connections:
        # Set up mock
        mock_cursor = MagicMock()
        mock_connection = MagicMock()
        mock_connection.cursor.return_value = mock_cursor
        mock_connections.__getitem__ = MagicMock(return_value=mock_connection)

        # Run check
        errors = check_database_connection(None)

        # Verify
        assert len(errors) == 0
        mock_connection.cursor.assert_called_once()


@pytest.mark.parametrize(
    "exception_class", [OperationalError, InterfaceError, DatabaseError]
)
def test_check_database_connection_failure(exception_class):
    """Test database connection check when connection fails."""
    with patch("pyerp.core.checks.connections") as mock_connections:
        # Set up mock to raise exception
        mock_connection = MagicMock()
        mock_connection.cursor.side_effect = exception_class("Test error")
        mock_connections.__getitem__ = MagicMock(return_value=mock_connection)

        # Run check
        errors = check_database_connection(None)

        # Verify
        assert len(errors) == 1
        assert isinstance(errors[0], Warning)
        assert errors[0].id == "pyerp.core.W001"
        assert "Database connection failed" in str(errors[0].msg)
        assert "Test error" in str(errors[0].msg)
        assert "database-dependent features will be unavailable" in errors[0].hint
