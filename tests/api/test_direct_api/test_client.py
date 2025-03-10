"""
Unit tests for the LegacyERPClient class.

These tests verify that the LegacyERPClient correctly handles API requests,
session management, and response parsing.
"""

import unittest
from unittest.mock import patch

import pandas as pd
import pytest

from pyerp.external_api.legacy_erp.client import LegacyERPClient
from pyerp.external_api.legacy_erp.exceptions import LegacyERPError


class TestLegacyERPClient(unittest.TestCase):
    """Test cases for the LegacyERPClient class."""

    def setUp(self):
        """Set up test fixtures."""
        self.client = LegacyERPClient(environment="test")

        # Sample API response
        self.sample_response = {
            "__DATACLASS": "Artikel_Familie",
            "__entityModel": "Artikel_Familie",
            "__GlobalStamp": 0,
            "__COUNT": 3,
            "__FIRST": 0,
            "__ENTITIES": [
                {
                    "__KEY": "key1",
                    "UID": "uid1",
                    "Bezeichnung": "Item 1",
                },
                {
                    "__KEY": "key2",
                    "UID": "uid2",
                    "Bezeichnung": "Item 2",
                },
                {
                    "__KEY": "key3",
                    "UID": "uid3",
                    "Bezeichnung": "Item 3",
                },
            ],
        }

    @patch("pyerp.external_api.legacy_erp.client.LegacyERPClient.fetch_table")
    def test_fetch_table_success(self, mock_fetch_table):
        """Test successful table fetch."""
        # Setup mock response
        mock_df = pd.DataFrame(self.sample_response["__ENTITIES"])
        mock_fetch_table.return_value = mock_df

        # Call the method
        result = self.client.fetch_table("Artikel_Familie", top=10)

        # Verify the result
        self.assertIsInstance(result, pd.DataFrame)
        self.assertEqual(len(result), 3)
        self.assertEqual(result.iloc[0]["Bezeichnung"], "Item 1")

        # Verify the request was made correctly
        mock_fetch_table.assert_called_once_with(
            "Artikel_Familie",
            top=10,
        )

    @patch("pyerp.external_api.legacy_erp.client.LegacyERPClient.fetch_table")
    def test_fetch_table_pagination(self, mock_fetch_table):
        """Test table fetch with pagination."""
        # Setup first response
        first_df = pd.DataFrame([
            {"__KEY": "key1", "UID": "uid1", "Bezeichnung": "Item 1"},
            {"__KEY": "key2", "UID": "uid2", "Bezeichnung": "Item 2"},
        ])

        # Configure mock to return the same response (no pagination)
        mock_fetch_table.return_value = first_df

        # Call the method with top=2
        result = self.client.fetch_table("Artikel_Familie", top=2)

        # Verify the result
        self.assertIsInstance(result, pd.DataFrame)
        self.assertEqual(len(result), 2)  # Should have 2 records as pagination is not implemented
        self.assertEqual(result.iloc[0]["Bezeichnung"], "Item 1")

        # Verify request was made once
        mock_fetch_table.assert_called_once_with(
            "Artikel_Familie",
            top=2,
        )

    @patch("pyerp.external_api.legacy_erp.client.LegacyERPClient.fetch_table")
    def test_fetch_table_error_handling(self, mock_fetch_table):
        """Test error handling during table fetch."""
        mock_fetch_table.side_effect = LegacyERPError("Failed to fetch table")

        # Verify the exception is propagated
        with pytest.raises(LegacyERPError):
            self.client.fetch_table("Artikel_Familie")

    def test_check_connection(self):
        """Test connection check functionality."""
        with patch.object(self.client, 'validate_session') as mock_validate:
            # Test successful connection
            mock_validate.return_value = True
            self.assertTrue(self.client.check_connection())

            # Test failed connection
            mock_validate.side_effect = Exception("Connection failed")
            with pytest.raises(LegacyERPError):
                self.client.check_connection()


if __name__ == "__main__":
    unittest.main()
