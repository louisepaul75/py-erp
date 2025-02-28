"""
Tests for the DirectAPIClient class.
"""

import pytest
import json
import pandas as pd
from unittest.mock import patch, MagicMock
from django.test import TestCase
import requests

from pyerp.direct_api.client import DirectAPIClient
from pyerp.direct_api.exceptions import (
    ConfigurationError,
    ConnectionError,
    ResponseError,
    DataError,
    DirectAPIError,
    AuthenticationError
)


class TestDirectAPIClient(TestCase):
    """Tests for the DirectAPIClient class."""
    
    def setUp(self):
        """Set up test environment."""
        self.client = DirectAPIClient(environment='test')
    
    def test_init(self):
        """Test initialization with default parameters."""
        client = DirectAPIClient()
        self.assertEqual(client.environment, 'live')
        self.assertEqual(client.timeout, 30)  # Default from API_REQUEST_TIMEOUT
        
        # Test with custom parameters
        client = DirectAPIClient(environment='test', timeout=60)
        self.assertEqual(client.environment, 'test')
        self.assertEqual(client.timeout, 60)
    
    def test_init_invalid_environment(self):
        """Test initialization with invalid environment."""
        with self.assertRaises(ValueError):
            DirectAPIClient(environment='invalid')
    
    def test_get_base_url(self):
        """Test _get_base_url method."""
        # This should return the test environment URL
        self.assertEqual(self.client._get_base_url(), 'http://localhost:8080')
    
    @patch('pyerp.direct_api.client.get_session')
    def test_get_session(self, mock_get_session):
        """Test _get_session method."""
        # Set up the mock
        mock_session = MagicMock()
        mock_get_session.return_value = mock_session
        
        # Call the method
        session = self.client._get_session()
        
        # Verify the results
        self.assertEqual(session, mock_session)
        mock_get_session.assert_called_once_with('test')
    
    def test_build_url(self):
        """Test _build_url method."""
        # Test with simple endpoint
        url = self.client._build_url('products')
        self.assertEqual(url, 'http://localhost:8080/rest/products')
        
        # Test with endpoint that already has a leading slash
        url = self.client._build_url('/products')
        self.assertEqual(url, 'http://localhost:8080/products')
        
        # Test with endpoint that has query parameters
        url = self.client._build_url('products?$filter=name eq "Test"')
        self.assertEqual(url, 'http://localhost:8080/rest/products?$filter=name eq "Test"')
    
    @patch('pyerp.direct_api.client.DirectAPIClient._get_session')
    @patch('pyerp.direct_api.client.requests.request')
    def test_make_request_success(self, mock_request, mock_get_session):
        """Test _make_request method with successful response."""
        # Set up the mocks
        mock_session = MagicMock()
        mock_session.get_cookie.return_value = 'test_cookie'
        mock_get_session.return_value = mock_session
        
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_request.return_value = mock_response
        
        # Call the method
        response = self.client._make_request('GET', 'products')
        
        # Verify the results
        self.assertEqual(response, mock_response)
        mock_request.assert_called_once_with(
            method='GET',
            url='http://localhost:8080/rest/products',
            params=None,
            json=None,
            headers={'Cookie': 'test_cookie', 'Accept': 'application/json'},
            timeout=30
        )
    
    @patch('pyerp.direct_api.client.DirectAPIClient._get_session')
    @patch('pyerp.direct_api.client.requests.request')
    def test_make_request_auth_error_retry(self, mock_request, mock_get_session):
        """Test _make_request method with authentication error and retry."""
        # Set up the mocks
        mock_session = MagicMock()
        mock_session.get_cookie.return_value = 'test_cookie'
        mock_session.refresh = MagicMock()
        mock_get_session.return_value = mock_session
        
        # First response is 401, second is 200
        mock_response_error = MagicMock()
        mock_response_error.status_code = 401
        
        mock_response_success = MagicMock()
        mock_response_success.status_code = 200
        
        mock_request.side_effect = [mock_response_error, mock_response_success]
        
        # Call the method
        response = self.client._make_request('GET', 'products')
        
        # Verify the results
        self.assertEqual(response, mock_response_success)
        self.assertEqual(mock_request.call_count, 2)
        mock_session.refresh.assert_called_once()
    
    @patch('pyerp.direct_api.client.DirectAPIClient._get_session')
    @patch('pyerp.direct_api.client.requests.request')
    def test_make_request_error_response(self, mock_request, mock_get_session):
        """Test _make_request method with error response."""
        # Set up the mocks
        mock_session = MagicMock()
        mock_session.get_cookie.return_value = 'test_cookie'
        mock_get_session.return_value = mock_session
        
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_response.text = 'Internal Server Error'
        mock_request.return_value = mock_response
        
        # Call the method and check for exception
        with self.assertRaises(ResponseError):
            self.client._make_request('GET', 'products')
    
    @patch('pyerp.direct_api.client.DirectAPIClient._get_session')
    @patch('pyerp.direct_api.client.requests.request')
    def test_make_request_connection_error(self, mock_request, mock_get_session):
        """Test _make_request method with connection error."""
        # Set up the mocks
        mock_session = MagicMock()
        mock_session.get_cookie.return_value = 'test_cookie'
        mock_get_session.return_value = mock_session
        
        # Simulate a connection error
        mock_request.side_effect = requests.RequestException("Connection error")
        
        # Call the method and check for exception
        with self.assertRaises(ConnectionError):
            self.client._make_request('GET', 'products')
    
    @patch('pyerp.direct_api.client.DirectAPIClient._make_request')
    def test_fetch_table_success(self, mock_make_request):
        """Test fetch_table method with successful response."""
        # Set up the mock
        mock_response = MagicMock()
        mock_response.json.return_value = [
            {"id": 1, "name": "Product 1"},
            {"id": 2, "name": "Product 2"}
        ]
        mock_make_request.return_value = mock_response
        
        # Call the method
        df = self.client.fetch_table('products')
        
        # Verify the results
        self.assertIsInstance(df, pd.DataFrame)
        self.assertEqual(len(df), 2)
        self.assertEqual(df.iloc[0]['name'], 'Product 1')
        self.assertEqual(df.iloc[1]['name'], 'Product 2')
        
        # Verify the request was made correctly
        mock_make_request.assert_called_once_with(
            'GET',
            'products',
            params={'$top': 100, '$skip': 0, 'new_data_only': 'true'}
        )
    
    @patch('pyerp.direct_api.client.DirectAPIClient._make_request')
    def test_fetch_table_with_filters(self, mock_make_request):
        """Test fetch_table with filters."""
        # Set up the mock
        mock_response = MagicMock()
        mock_response.json.return_value = [
            {"id": 1, "name": "Product 1"}
        ]
        mock_make_request.return_value = mock_response
        
        # Call the method with filters
        df = self.client.fetch_table(
            'products',
            top=10,
            skip=5,
            new_data_only=False,
            date_created_start='2023-01-01',
            filter_query='name eq "Product 1"'
        )
        
        # Verify the results
        self.assertIsInstance(df, pd.DataFrame)
        self.assertEqual(len(df), 1)
        
        # Verify the request was made with the correct parameters
        mock_make_request.assert_called_once_with(
            'GET',
            'products',
            params={
                '$top': 10,
                '$skip': 5,
                'date_created_start': '2023-01-01',
                '$filter': 'name eq "Product 1"'
            }
        )
    
    @patch('pyerp.direct_api.client.DirectAPIClient._make_request')
    @patch('pyerp.direct_api.client.API_PAGINATION_ENABLED', True)
    def test_fetch_table_pagination(self, mock_make_request):
        """Test fetch_table with pagination."""
        # Set up the mock - first page has full results, second page has partial, indicating end
        
        mock_response1 = MagicMock()
        mock_response1.json.return_value = [
            {"id": 1, "name": "Product 1"},
            {"id": 2, "name": "Product 2"}
        ]
        
        mock_response2 = MagicMock()
        mock_response2.json.return_value = [
            {"id": 3, "name": "Product 3"}
        ]
        
        # Important: The first call should be with skip=0, the second with skip=2
        mock_make_request.side_effect = [mock_response1, mock_response2]
        
        # Call the method with a small page size to trigger pagination
        df = self.client.fetch_table('products', top=2, skip=0)
        
        # Verify the results - should have combined both pages
        self.assertIsInstance(df, pd.DataFrame)
        self.assertEqual(len(df), 3)
        
        # Verify the multiple requests were made
        self.assertEqual(mock_make_request.call_count, 2)
        
        # Check the calls were made with the correct parameters
        calls = mock_make_request.call_args_list
        self.assertEqual(calls[0][0], ('GET', 'products'))
        self.assertEqual(calls[0][1]['params'], {'$top': 2, '$skip': 2, 'new_data_only': 'true'})
        
        self.assertEqual(calls[1][0], ('GET', 'products'))
        self.assertEqual(calls[1][1]['params'], {'$top': 2, '$skip': 2, 'new_data_only': 'true'})
    
    @patch('pyerp.direct_api.client.DirectAPIClient._make_request')
    def test_fetch_table_json_error(self, mock_make_request):
        """Test fetch_table with JSON parsing error."""
        # Set up the mock - invalid JSON
        mock_response = MagicMock()
        mock_response.json.side_effect = json.JSONDecodeError("Invalid JSON", "", 0)
        mock_make_request.return_value = mock_response
        
        # Call the method and check for exception
        with self.assertRaises(DirectAPIError):
            self.client.fetch_table('products')
    
    @patch('pyerp.direct_api.client.DirectAPIClient._make_request')
    def test_fetch_table_unexpected_format(self, mock_make_request):
        """Test fetch_table with unexpected data format."""
        # Set up the mock - not a list but a dictionary
        mock_response = MagicMock()
        mock_response.json.return_value = {"error": "Not a list"}
        mock_make_request.return_value = mock_response
        
        # Call the method and check for exception
        with self.assertRaises(DirectAPIError):
            self.client.fetch_table('products')
    
    @patch('pyerp.direct_api.client.DirectAPIClient._make_request')
    def test_push_field_success(self, mock_make_request):
        """Test push_field with successful response."""
        # Set up the mock
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_make_request.return_value = mock_response
        
        # Call the method
        result = self.client.push_field('products', 1, 'name', 'New Name')
        
        # Verify the results
        self.assertTrue(result)
        mock_make_request.assert_called_once_with(
            'PUT',
            'products/1/name',
            data={'value': 'New Name'}
        )
    
    @patch('pyerp.direct_api.client.DirectAPIClient._make_request')
    def test_push_field_error(self, mock_make_request):
        """Test push_field with error response."""
        # Set up the mock to raise an exception
        mock_make_request.side_effect = ResponseError(400, "Bad Request")
        
        # Call the method and check for exception
        with self.assertRaises(ResponseError):
            self.client.push_field('products', 1, 'name', 'New Name')
    
    @patch('pyerp.direct_api.client.DirectAPIClient._make_request')
    def test_fetch_record_success(self, mock_make_request):
        """Test fetch_record with successful response."""
        # Set up the mock
        mock_response = MagicMock()
        mock_response.json.return_value = {"id": 1, "name": "Product 1"}
        mock_make_request.return_value = mock_response
        
        # Call the method
        record = self.client.fetch_record('products', 1)
        
        # Verify the results
        self.assertEqual(record['id'], 1)
        self.assertEqual(record['name'], 'Product 1')
        mock_make_request.assert_called_once_with('GET', 'products/1')
    
    @patch('pyerp.direct_api.client.DirectAPIClient._make_request')
    def test_fetch_record_json_error(self, mock_make_request):
        """Test fetch_record with JSON parsing error."""
        # Set up the mock - invalid JSON
        mock_response = MagicMock()
        mock_response.json.side_effect = json.JSONDecodeError("Invalid JSON", "", 0)
        mock_make_request.return_value = mock_response
        
        # Call the method and check for exception
        with self.assertRaises(DataError):
            self.client.fetch_record('products', 1)
    
    @patch('pyerp.direct_api.client.DirectAPIClient._make_request')
    def test_fetch_record_error(self, mock_make_request):
        """Test fetch_record with error response."""
        # Set up the mock to raise an exception
        mock_make_request.side_effect = ResponseError(404, "Not Found")
        
        # Call the method and check for exception
        with self.assertRaises(ResponseError):
            self.client.fetch_record('products', 1) 