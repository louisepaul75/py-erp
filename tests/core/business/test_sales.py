import unittest
from unittest.mock import patch, MagicMock

from django.db.utils import OperationalError
from django.test import TestCase

from pyerp.business_modules.sales.models import SalesModel, get_sales_status


class TestSalesModel(TestCase):
    """Tests for the SalesModel abstract model"""

    def test_abstract_model(self):
        """Test that SalesModel is an abstract model"""
        self.assertTrue(SalesModel._meta.abstract)


class TestSalesStatusFunction(unittest.TestCase):
    """Tests for the get_sales_status function"""

    @patch("django.db.connection")
    def test_get_sales_status_success(self, mock_connection):
        """Test get_sales_status when DB connection works"""
        # Set up mock
        mock_cursor = MagicMock()
        mock_connection.cursor.return_value = mock_cursor

        # Call function
        result = get_sales_status()

        # Verify results
        self.assertEqual(result, "Sales module database connection is working")
        mock_connection.cursor.assert_called_once()
        mock_cursor.close.assert_called_once()

    @patch("django.db.connection")
    def test_get_sales_status_operational_error(self, mock_connection):
        """Test get_sales_status when DB connection fails with error"""
        # Set up mock to raise OperationalError
        mock_connection.cursor.side_effect = OperationalError("DB error")

        # Call function
        result = get_sales_status()

        # Verify results
        expected = "Sales module found but database is not available"
        self.assertEqual(result, expected)
        mock_connection.cursor.assert_called_once()

    @patch("django.db.connection")
    def test_get_sales_status_general_exception(self, mock_connection):
        """Test get_sales_status when DB connection fails with exception"""
        # Set up mock to raise a general exception
        mock_connection.cursor.side_effect = Exception("Some error")

        # Call function
        result = get_sales_status()

        # Verify results
        self.assertEqual(result, "Sales module error: Some error")
        mock_connection.cursor.assert_called_once() 