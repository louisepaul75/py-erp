"""
Tests for the legacy_sync API client module using the direct_api implementation.  # noqa: E501
"""

import pytest  # noqa: F401
import pandas as pd  # noqa: F401
from unittest.mock import patch, MagicMock
from django.test import TestCase

from pyerp.legacy_sync.api_client import LegacyAPIClient


class TestLegacyAPIClient(TestCase):
    """Tests for the LegacyAPIClient class."""

    @patch('pyerp.legacy_sync.api_client.DirectAPIClient')
    def test_init_with_direct_api(self, mock_direct_api_client):
        """Test initialization with DirectAPIClient."""
        mock_client = MagicMock()
        mock_direct_api_client.return_value = mock_client

 # Create the instance
        client = LegacyAPIClient(environment='test')

 # Verify the instance was created correctly
        self.assertEqual(client.environment, 'test')
        self.assertIsNotNone(client.direct_client)
        self.assertEqual(client.direct_client, mock_client)
        self.assertFalse(client.using_wsz_api)

 # Verify DirectAPIClient was initialized correctly
        mock_direct_api_client.assert_called_once_with(environment='test')

    @patch('pyerp.legacy_sync.api_client.DirectAPIClient')
    @patch('pyerp.legacy_sync.api_client.WSZ_api', None)
    def test_init_fallback_to_wsz_api(self, mock_direct_api_client):
        """Test initialization fallback to WSZ_api when DirectAPIClient fails."""  # noqa: E501
        mock_direct_api_client.side_effect = ImportError(
            "Cannot import DirectAPIClient")

 # Create an instance with mocked WSZ_api import
        with patch('pyerp.legacy_sync.api_client.importlib.import_module') as mock_import:  # noqa: E501
            mock_wsz_api = MagicMock()
            mock_import.return_value = mock_wsz_api

            client = LegacyAPIClient(environment='test')

 # Verify the instance was created with WSZ_api
            self.assertEqual(client.environment, 'test')
            self.assertIsNone(client.direct_client)
            self.assertTrue(client.using_wsz_api)
            self.assertEqual(client.wsz_api, mock_wsz_api)

    @patch('pyerp.legacy_sync.api_client.DirectAPIClient')
    def test_refresh_session_with_direct_api(self, mock_direct_api_client):
        """Test refresh_session method with DirectAPIClient."""
        mock_client = MagicMock()
        mock_direct_api_client.return_value = mock_client

 # Set up the session mock
        mock_session = MagicMock()
        mock_session.refresh.return_value = True
        mock_client._get_session.return_value = mock_session

 # Create the instance and call the method
        client = LegacyAPIClient(environment='test')
        result = client.refresh_session()

 # Verify the result
        self.assertTrue(result)
        mock_client._get_session.assert_called_once()
        mock_session.refresh.assert_called_once()

    @patch('pyerp.legacy_sync.api_client.get_session_cookie')
    def test_refresh_session_with_wsz_api(self, mock_get_session_cookie):
        """Test refresh_session method with WSZ_api."""
        mock_get_session_cookie.return_value = 'test_cookie'

 # Create an instance with mocked WSZ_api
        with patch('pyerp.legacy_sync.api_client.importlib.import_module') as mock_import:  # noqa: E501
            mock_wsz_api = MagicMock()
            mock_import.return_value = mock_wsz_api

 # Force using WSZ_api
            client = LegacyAPIClient(environment='test')
            client.direct_client = None
            client.using_wsz_api = True
            client.wsz_api = mock_wsz_api

 # Call the method
            result = client.refresh_session()

 # Verify the result
            self.assertTrue(result)
            mock_get_session_cookie.assert_called_once_with(environment='test')

    @patch('pyerp.legacy_sync.api_client.DirectAPIClient')
    def test_fetch_table_with_direct_api(self, mock_direct_api_client):
        """Test fetch_table method with DirectAPIClient."""
        mock_client = MagicMock()
        mock_direct_api_client.return_value = mock_client

 # Create a sample DataFrame to return
        df = pd.DataFrame({'id': [1, 2], 'name': ['Item 1', 'Item 2']})
        mock_client.fetch_table.return_value = df

 # Create the instance and call the method
        client = LegacyAPIClient(environment='test')
        result = client.fetch_table(
            table='products',  # noqa: E128
            top=10,  # noqa: F841
            skip=0,  # noqa: F841
            filter_query="name eq 'Item 1'"  # noqa: F841
        )

 # Verify the result
        self.assertTrue(result.equals(df))
        mock_client.fetch_table.assert_called_once_with(
            'products',  # noqa: E128
            top=10,  # noqa: F841
            skip=0,  # noqa: F841
            filter_query="name eq 'Item 1'",  # noqa: F841
            new_data_only=True  # noqa: F841
        )

    def test_fetch_table_with_wsz_api(self):
        """Test fetch_table method with WSZ_api."""
        df = pd.DataFrame({'id': [1, 2], 'name': ['Item 1', 'Item 2']})

 # Create an instance with mocked WSZ_api
        with patch('pyerp.legacy_sync.api_client.importlib.import_module') as mock_import:  # noqa: E501
            mock_wsz_api = MagicMock()
            mock_wsz_api.fetch_data_from_api.return_value = df
            mock_import.return_value = mock_wsz_api

 # Force using WSZ_api
            client = LegacyAPIClient(environment='test')
            client.direct_client = None
            client.using_wsz_api = True
            client.wsz_api = mock_wsz_api

 # Call the method
            result = client.fetch_table(
                table='products',  # noqa: E128
                top=100,  # noqa: F841
                skip=0,  # noqa: F841
                filter_query="name eq 'Item 1'"  # noqa: F841
            )

 # Verify the result
            self.assertTrue(result.equals(df))
            mock_wsz_api.fetch_data_from_api.assert_called_once_with(
                table='products',  # noqa: E128
                environment='test',  # noqa: F841
                new_data_only=True,  # noqa: F841
                limit=100,  # noqa: F841
                skip=0,  # noqa: F841
                filter_query="name eq 'Item 1'"  # noqa: F841
            )

    @patch('pyerp.legacy_sync.api_client.DirectAPIClient')
    def test_push_field_with_direct_api(self, mock_direct_api_client):
        """Test push_field method with DirectAPIClient."""
        mock_client = MagicMock()
        mock_direct_api_client.return_value = mock_client
        mock_client.push_field.return_value = True

 # Create the instance and call the method
        client = LegacyAPIClient(environment='test')
        result = client.push_field(
            table='products',  # noqa: E128
            id=123,  # noqa: F841
            field='name',  # noqa: F841
            value='New Product Name'  # noqa: F841
        )

 # Verify the result
        self.assertTrue(result)
        mock_client.push_field.assert_called_once_with(
            'products',  # noqa: E128
            123,
            'name',
            'New Product Name'
        )

    def test_push_field_with_wsz_api(self):
        """Test push_field method with WSZ_api."""
        with patch('pyerp.legacy_sync.api_client.importlib.import_module') as mock_import:  # noqa: E501
            mock_wsz_api = MagicMock()
            mock_wsz_api.push_data.return_value = True
            mock_import.return_value = mock_wsz_api

 # Force using WSZ_api
            client = LegacyAPIClient(environment='test')
            client.direct_client = None
            client.using_wsz_api = True
            client.wsz_api = mock_wsz_api

 # Call the method
            result = client.push_field(
                table='products',  # noqa: E128
                id=123,  # noqa: F841
                field='name',  # noqa: F841
                value='New Product Name'  # noqa: F841
            )

 # Verify the result
            self.assertTrue(result)
            mock_wsz_api.push_data.assert_called_once_with(
                table='products',  # noqa: E128
                id=123,  # noqa: F841
                field='name',  # noqa: F841
                value='New Product Name',  # noqa: F841
                environment='test'  # noqa: F841
            )

    @patch('pyerp.legacy_sync.api_client.DirectAPIClient')
    def test_fetch_record_with_direct_api(self, mock_direct_api_client):
        """Test fetch_record method with DirectAPIClient."""
        mock_client = MagicMock()
        mock_direct_api_client.return_value = mock_client

 # Create a sample record to return
        record = {'id': 123, 'name': 'Test Product', 'price': 19.99}
        mock_client.fetch_record.return_value = record

 # Create the instance and call the method
        client = LegacyAPIClient(environment='test')
        result = client.fetch_record(
            table='products',  # noqa: E128
            id=123  # noqa: F841
        )

 # Verify the result
        self.assertEqual(result, record)
        mock_client.fetch_record.assert_called_once_with(
            'products',  # noqa: E128
            123
        )

    def test_fetch_record_with_wsz_api(self):
        """Test fetch_record method with WSZ_api."""
        df = pd.DataFrame(
            {'id': [123], 'name': ['Test Product'], 'price': [19.99]})  # noqa: E128

 # Create an instance with mocked WSZ_api
                with patch('pyerp.legacy_sync.api_client.importlib.import_module') as mock_import:  # noqa: E501
            mock_wsz_api = MagicMock()
            mock_wsz_api.fetch_data_from_api.return_value = df
            mock_import.return_value = mock_wsz_api

 # Force using WSZ_api
            client = LegacyAPIClient(environment='test')
            client.direct_client = None
            client.using_wsz_api = True
            client.wsz_api = mock_wsz_api

 # Call the method
            result = client.fetch_record(
                table='products',  # noqa: E128
                id=123  # noqa: F841
            )

 # Verify the result - should be a dict representation of the first
 # row
            self.assertEqual(result['id'], 123)
            self.assertEqual(result['name'], 'Test Product')
            self.assertEqual(result['price'], 19.99)

 # Verify the WSZ_api call - should use the id to filter
            mock_wsz_api.fetch_data_from_api.assert_called_once()
            args, kwargs = mock_wsz_api.fetch_data_from_api.call_args
            self.assertEqual(kwargs['table'], 'products')
            self.assertEqual(kwargs['environment'], 'test')
            self.assertEqual(kwargs['filter_query'], "id eq 123")
