"""
Tests for the compatibility layer with WSZ_api.
"""

import pytest  # noqa: F401
import json  # noqa: F401
import pandas as pd
from unittest.mock import patch, MagicMock  # noqa: F401
from django.test import TestCase
import warnings

from pyerp.direct_api.compatibility import (
    fetch_data_from_api,
    push_data,
    get_session_cookie,
)


class TestCompatibilityLayer(TestCase):
    """Tests for the compatibility layer with WSZ_api."""

    def setUp(self):
        """Set up test environment."""
        # Clear the warnings registry for testing
        warnings.resetwarnings()
        # Ensure we capture all deprecation warnings
        warnings.simplefilter('always', DeprecationWarning)

    @patch('pyerp.direct_api.auth.get_session_cookie')
    def test_get_session_cookie(self, mock_auth_get_cookie):
        """Test get_session_cookie function."""
        # Set up the mock to return a test cookie
        mock_auth_get_cookie.return_value = 'test_cookie'

        # Call the function with the warning capture
        with warnings.catch_warnings(record=True) as w:
            cookie = get_session_cookie(mode='test')

            # Check for deprecation warning
            self.assertEqual(len(w), 1)
            self.assertTrue(issubclass(w[0].category, DeprecationWarning))
            self.assertIn('deprecated WSZ_api', str(w[0].message))

        # Verify the results
        self.assertEqual(cookie, 'test_cookie')
        mock_auth_get_cookie.assert_called_once_with(environment='test')

    @patch('pyerp.direct_api.compatibility._client')
    def test_fetch_data_from_api(self, mock_client):
        """Test fetch_data_from_api function."""
        # Create a sample DataFrame for the result
        sample_df = pd.DataFrame([
            {"id": 1, "name": "Product 1"},
            {"id": 2, "name": "Product 2"}
        ])
        mock_client.fetch_table.return_value = sample_df

        # Call the function with the warning capture
        with warnings.catch_warnings(record=True) as w:
            result_df = fetch_data_from_api(
                table_name='products',
                top=100,
                skip=0,
                new_data_only=True,
                date_created_start='2023-01-01'
            )

            # Check for deprecation warning
            self.assertEqual(len(w), 1)
            self.assertTrue(issubclass(w[0].category, DeprecationWarning))
            self.assertIn('deprecated WSZ_api', str(w[0].message))

        # Verify the results
        self.assertIs(result_df, sample_df)  # Should be the same object
        mock_client.fetch_table.assert_called_once_with(
            table_name='products',
            top=100,
            skip=0,
            new_data_only=True,
            date_created_start='2023-01-01'
        )

    @patch('pyerp.direct_api.compatibility._client')
    def test_push_data_success(self, mock_client):
        """Test push_data function with successful response."""
        mock_client.push_field.return_value = True

        # Call the function with the warning capture
        with warnings.catch_warnings(record=True) as w:
            result = push_data(
                table='products',
                column='name',
                key=123,
                value='New Name'
            )

            # Check for deprecation warning
            self.assertEqual(len(w), 1)
            self.assertTrue(issubclass(w[0].category, DeprecationWarning))
            self.assertIn('deprecated WSZ_api', str(w[0].message))

        # Verify the results
        self.assertTrue(result)
        mock_client.push_field.assert_called_once_with(
            table_name='products',
            record_id=123,
            field_name='name',
            field_value='New Name'
        )

    @patch('pyerp.direct_api.compatibility._client')
    def test_push_data_failure(self, mock_client):
        """Test push_data function with failure response."""
        mock_client.push_field.return_value = False

        # Call the function
        with warnings.catch_warnings():
            # Ignore the deprecation warning for this test
            warnings.simplefilter('ignore')
            result = push_data(
                table='products',
                column='name',
                key=123,
                value='New Name'
            )

        # Verify the results
        self.assertFalse(result)
