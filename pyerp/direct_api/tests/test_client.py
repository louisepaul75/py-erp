"""
Unit tests for the DirectAPIClient class.

These tests verify that the DirectAPIClient correctly handles API requests,
session management, and response parsing.  # noqa: E501
"""

import unittest
from unittest.mock import patch, MagicMock
import pandas as pd
import json  # noqa: F401

from pyerp.direct_api.client import DirectAPIClient
from pyerp.direct_api.exceptions import ResponseError, ConnectionError, DataError  # noqa: E501, F401


class TestDirectAPIClient(unittest.TestCase):
    """Test cases for the DirectAPIClient class."""

    def setUp(self):
        """Set up test fixtures."""
        self.client = DirectAPIClient(environment='test')

        # Sample 4D API response
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
                    "Bezeichnung": "Item 1"
                },
                {
                    "__KEY": "key2",
                    "UID": "uid2",
                    "Bezeichnung": "Item 2"
                },
                {
                    "__KEY": "key3",
                    "UID": "uid3",
                    "Bezeichnung": "Item 3"
                }
            ]
        }

    @patch('pyerp.direct_api.client.DirectAPIClient._make_request')
    def test_fetch_table_success(self, mock_make_request):
        """Test successful table fetch."""
        # Setup mock response
        mock_response = MagicMock()
        mock_response.json.return_value = self.sample_response
        mock_make_request.return_value = mock_response

        # Call the method
        result = self.client.fetch_table('Artikel_Familie', top=10)

        # Verify the result
        self.assertIsInstance(result, pd.DataFrame)
        self.assertEqual(len(result), 3)
        self.assertEqual(result.iloc[0]['Bezeichnung'], 'Item 1')

        # Verify the request was made correctly
        mock_make_request.assert_called_once_with(
            'GET',
            'Artikel_Familie',
            params={'$top': 10, '$skip': 0, 'new_data_only': 'true'}
        )

    @patch('pyerp.direct_api.client.DirectAPIClient._make_request')
    def test_fetch_table_pagination(self, mock_make_request):
        """Test table fetch with pagination."""
        # Setup first response with pagination
        first_response = MagicMock()
        first_response.json.return_value = {
            "__DATACLASS": "Artikel_Familie",
            "__entityModel": "Artikel_Familie",
            "__COUNT": 5,  # Total count is 5
            "__FIRST": 0,
            "__ENTITIES": [
                {"__KEY": "key1", "UID": "uid1", "Bezeichnung": "Item 1"},
                {"__KEY": "key2", "UID": "uid2", "Bezeichnung": "Item 2"}
            ]
        }

        # Setup second response
        second_response = MagicMock()
        second_response.json.return_value = {
            "__DATACLASS": "Artikel_Familie",
            "__entityModel": "Artikel_Familie",
            "__COUNT": 5,
            "__FIRST": 2,
            "__ENTITIES": [
                {"__KEY": "key3", "UID": "uid3", "Bezeichnung": "Item 3"},
                {"__KEY": "key4", "UID": "uid4", "Bezeichnung": "Item 4"},
                {"__KEY": "key5", "UID": "uid5", "Bezeichnung": "Item 5"}
            ]
        }

        # Configure mock to return different responses
        mock_make_request.side_effect = [first_response, second_response]

        # Call the method with top=2 to trigger pagination
        result = self.client.fetch_table('Artikel_Familie', top=2)

        # Verify the result
        self.assertIsInstance(result, pd.DataFrame)
        self.assertEqual(len(result), 5)  # Should have all 5 records
        self.assertEqual(result.iloc[2]['Bezeichnung'], 'Item 3')

        # Verify both requests were made
        self.assertEqual(mock_make_request.call_count, 2)
        mock_make_request.assert_any_call(
            'GET',
            'Artikel_Familie',
            params={'$top': 2, '$skip': 0, 'new_data_only': 'true'}
        )
        mock_make_request.assert_any_call(
            'GET',
            'Artikel_Familie',
            params={'$top': 2, '$skip': 2, 'new_data_only': 'true'}
        )

    @patch('pyerp.direct_api.client.DirectAPIClient._make_request')
    def test_fetch_table_error_handling(self, mock_make_request):
        """Test error handling during table fetch."""
        # Setup mock to raise an exception
        mock_make_request.side_effect = ResponseError(
            404, "Not found", "Resource not found")

        # Verify the exception is propagated
        with self.assertRaises(ResponseError):
            self.client.fetch_table('Artikel_Familie')

    @patch('pyerp.direct_api.client.DirectAPIClient._make_request')
    def test_push_field_success(self, mock_make_request):
        """Test successful field update."""
        # Setup mock response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_make_request.return_value = mock_response

        # Call the method
        result = self.client.push_field(
            'Artikel_Familie', 'key1', 'Bezeichnung', 'New Name')

        # Verify the result
        self.assertTrue(result)

        # Verify the request was made correctly
        mock_make_request.assert_called_once_with(
            'PUT',
            'Artikel_Familie/key1/Bezeichnung',
            data={'value': 'New Name'}
        )

    @patch('pyerp.direct_api.client.DirectAPIClient._make_request')
    def test_push_field_error(self, mock_make_request):
        """Test error handling during field update."""
        # Setup mock to raise an exception
        mock_make_request.side_effect = ResponseError(
            404, "Not found", "Record not found")

        # Verify the exception is propagated
        with self.assertRaises(ResponseError):
            self.client.push_field(
                'Artikel_Familie',
                'invalid_key',
                'Bezeichnung',
                'New Name')


if __name__ == '__main__':
    unittest.main()
