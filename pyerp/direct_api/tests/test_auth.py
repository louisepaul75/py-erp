"""
Tests for the auth.py module.

This module tests the Session and SessionPool classes, ensuring that
authentication and session management work correctly.
"""

import pytest  # noqa: F401
import datetime
import json  # noqa: F401
from unittest.mock import patch, MagicMock, call
from django.test import TestCase
import requests
import time  # noqa: F401

from pyerp.direct_api.auth import (
    Session, SessionPool, get_session, get_session_cookie
)
from pyerp.direct_api.exceptions import (  # noqa: F401
    AuthenticationError, ConnectionError, ResponseError, SessionError
)
from pyerp.direct_api.settings import API_SESSION_EXPIRY, API_SESSION_REFRESH_MARGIN  # noqa: E501


class TestSession(TestCase):
    """Tests for the Session class."""

    def setUp(self):
        """Set up test environment."""
        self.session = Session(environment='test')

    def test_init(self):
        """Test initialization with default and custom parameters."""
        # Test with default parameters
        session = Session()
        self.assertEqual(session.environment, 'live')
        self.assertIsNone(session.cookie)
        self.assertIsNone(session.created_at)
        self.assertIsNone(session.expires_at)

        # Test with custom parameters
        session = Session(environment='test')
        self.assertEqual(session.environment, 'test')
        self.assertIsNone(session.cookie)
        self.assertIsNone(session.created_at)
        self.assertIsNone(session.expires_at)

    def test_init_invalid_environment(self):
        """Test initialization with invalid environment."""
        with self.assertRaises(ValueError):
            Session(environment='invalid')

    def test_is_valid_no_cookie(self):
        """Test is_valid with no cookie."""
        self.assertFalse(self.session.is_valid())

    def test_is_valid_no_expiry(self):
        """Test is_valid with cookie but no expiry."""
        self.session.cookie = 'test-cookie'
        self.assertFalse(self.session.is_valid())

    def test_is_valid_expired(self):
        """Test is_valid with expired cookie."""
        self.session.cookie = 'test-cookie'
        self.session.created_at = datetime.datetime.now(
        ) - datetime.timedelta(seconds=API_SESSION_EXPIRY + 1)
        self.session.expires_at = self.session.created_at + \
            datetime.timedelta(seconds=API_SESSION_EXPIRY)
        self.assertFalse(self.session.is_valid())

    def test_is_valid_near_expiry(self):
        """Test is_valid with cookie near expiry (within refresh margin)."""
        self.session.cookie = 'test-cookie'
        self.session.created_at = datetime.datetime.now() - datetime.timedelta(
            seconds=API_SESSION_EXPIRY - API_SESSION_REFRESH_MARGIN / 2
        )
        self.session.expires_at = self.session.created_at + \
            datetime.timedelta(seconds=API_SESSION_EXPIRY)
        self.assertFalse(self.session.is_valid())

    def test_is_valid_good(self):
        """Test is_valid with valid cookie."""
        self.session.cookie = 'test-cookie'
        self.session.created_at = datetime.datetime.now()
        self.session.expires_at = self.session.created_at + \
            datetime.timedelta(seconds=API_SESSION_EXPIRY)
        self.assertTrue(self.session.is_valid())

    @patch('pyerp.direct_api.auth.requests.get')
    def test_refresh_success(self, mock_get):
        """Test refresh with successful response."""
        # Mock the response with a cookie
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.headers = {'Set-Cookie': 'session=test-cookie'}
        mock_get.return_value = mock_response

        # Call refresh
        self.session.refresh()

        # Verify the result
        self.assertEqual(self.session.cookie, 'session=test-cookie')
        self.assertIsNotNone(self.session.created_at)
        self.assertIsNotNone(self.session.expires_at)
        self.assertEqual(
            self.session.expires_at - self.session.created_at,
            datetime.timedelta(seconds=API_SESSION_EXPIRY)
        )

        # Verify the call
        mock_get.assert_called_once_with(
            'http://localhost:8080/$info',
            timeout=30
        )

    @patch('pyerp.direct_api.auth.requests.get')
    def test_refresh_no_cookie(self, mock_get):
        """Test refresh with successful response but no cookie."""
        # Mock the response with no cookie
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.headers = {}
        mock_get.return_value = mock_response

        # Call refresh and expect an exception
        with self.assertRaises(AuthenticationError):
            self.session.refresh()

    @patch('pyerp.direct_api.auth.requests.get')
    def test_refresh_error_response(self, mock_get):
        """Test refresh with error response."""
        # Mock the response with an error
        mock_response = MagicMock()
        mock_response.status_code = 401
        mock_response.text = 'Unauthorized'
        mock_get.return_value = mock_response

        # Call refresh and expect an exception
        with self.assertRaises(ResponseError):
            self.session.refresh()

        # Verify the call
        mock_get.assert_called_once_with(
            'http://localhost:8080/$info',
            timeout=30
        )

    @patch('pyerp.direct_api.auth.requests.get')
    @patch('pyerp.direct_api.auth.time.sleep')
    def test_refresh_connection_error_retry(self, mock_sleep, mock_get):
        """Test refresh with connection error that succeeds on retry."""
        # Mock the first request to fail, second to succeed
        mock_get.side_effect = [
            requests.RequestException("Connection error"),
            MagicMock(
                status_code=200,
                headers={'Set-Cookie': 'session=test-cookie'}
            )
        ]

        # Call refresh
        self.session.refresh()

        # Verify the result
        self.assertEqual(self.session.cookie, 'session=test-cookie')
        self.assertIsNotNone(self.session.created_at)
        self.assertIsNotNone(self.session.expires_at)

        # Verify the calls
        self.assertEqual(mock_get.call_count, 2)
        mock_sleep.assert_called_once()

    @patch('pyerp.direct_api.auth.requests.get')
    @patch('pyerp.direct_api.auth.time.sleep')
    def test_refresh_connection_error_max_retries(self, mock_sleep, mock_get):
        """Test refresh with connection error that fails even after retries."""
        # Mock all requests to fail
        mock_get.side_effect = requests.RequestException("Connection error")

        # Call refresh and expect an exception
        with self.assertRaises(ConnectionError):
            self.session.refresh()

        # Verify multiple calls were made (1 initial + retries)
        self.assertTrue(mock_get.call_count > 1)
        self.assertEqual(mock_sleep.call_count, mock_get.call_count - 1)

    @patch('pyerp.direct_api.auth.Session.refresh')
    def test_get_cookie_valid(self, mock_refresh):
        """Test get_cookie with valid session."""
        # Set up a valid session
        self.session.cookie = 'test-cookie'
        self.session.created_at = datetime.datetime.now()
        self.session.expires_at = self.session.created_at + \
            datetime.timedelta(seconds=API_SESSION_EXPIRY)

        # Call get_cookie
        cookie = self.session.get_cookie()

        # Verify the result and that refresh wasn't called
        self.assertEqual(cookie, 'test-cookie')
        mock_refresh.assert_not_called()

    @patch('pyerp.direct_api.auth.Session.refresh')
    def test_get_cookie_invalid(self, mock_refresh):
        """Test get_cookie with invalid session."""
        # Call get_cookie on a new session
        cookie = self.session.get_cookie()  # noqa: F841

        # Verify refresh was called
        mock_refresh.assert_called_once()


class TestSessionPool(TestCase):
    """Tests for the SessionPool class."""

    def setUp(self):
        """Set up test environment."""
        self.pool = SessionPool()

    @patch('pyerp.direct_api.auth.Session')
    def test_get_session_new(self, mock_session_class):
        """Test get_session with no cached session."""
        # Set up mock session
        mock_session = MagicMock()
        mock_session.cookie = 'test-cookie'
        mock_session.created_at = datetime.datetime.now()
        mock_session.expires_at = mock_session.created_at + \
            datetime.timedelta(seconds=API_SESSION_EXPIRY)
        mock_session_class.return_value = mock_session

        # Call get_session
        session = self.pool.get_session('test')  # noqa: F841

        # Verify a new session was created and refreshed
        mock_session_class.assert_called_once_with('test')
        mock_session.refresh.assert_called_once()

        # Clear any sessions from cache
        self.pool.clear_sessions()

    @patch('pyerp.direct_api.auth.Session')
    def test_get_session_cached_valid(self, mock_session_class):
        """Test get_session with valid cached session."""
        # Set up mock session
        mock_session = MagicMock()
        mock_session.is_valid.return_value = True
        mock_session_class.return_value = mock_session

        # Create a session in cache
        now = datetime.datetime.now()
        self.pool.cache.set(
            'legacy_api_session_test',
            {
                'cookie': 'test-cookie',
                'created_at': now,
                'expires_at': now + datetime.timedelta(seconds=API_SESSION_EXPIRY)  # noqa: E501
            },
            API_SESSION_EXPIRY
        )

        # Call get_session
        session = self.pool.get_session('test')  # noqa: F841

        # Verify a session was created from cache and not refreshed
        mock_session_class.assert_called_once_with('test')
        mock_session.refresh.assert_not_called()

        # Clear any sessions from cache
        self.pool.clear_sessions()

    @patch('pyerp.direct_api.auth.Session')
    def test_get_session_cached_invalid(self, mock_session_class):
        """Test get_session with invalid cached session."""
        # Set up mock session
        mock_session = MagicMock()
        mock_session.is_valid.return_value = False
        mock_session_class.return_value = mock_session

        # Create an expired session in cache
        now = datetime.datetime.now()
        self.pool.cache.set(
            'legacy_api_session_test',
            {
                'cookie': 'test-cookie',
                'created_at': now - datetime.timedelta(seconds=API_SESSION_EXPIRY + 1),  # noqa: E501
                'expires_at': now - datetime.timedelta(seconds=1)
            },
            API_SESSION_EXPIRY
        )

        # Call get_session
        session = self.pool.get_session('test')  # noqa: F841

        # Verify a session was created from cache but then refreshed
        # Session is called twice because cache miss creates a new session
        self.assertEqual(mock_session_class.call_count, 2)
        self.assertEqual(mock_session_class.call_args_list[0], call('test'))
        mock_session.refresh.assert_called_once()

        # Clear any sessions from cache
        self.pool.clear_sessions()

    def test_clear_sessions(self):
        """Test clear_sessions method."""
        # Create sessions in cache
        now = datetime.datetime.now()
        for env in ['live', 'test']:
            self.pool.cache.set(
                f'legacy_api_session_{env}',
                {
                    'cookie': f'{env}-cookie',
                    'created_at': now,
                    'expires_at': now + datetime.timedelta(seconds=API_SESSION_EXPIRY)  # noqa: E501
                },
                API_SESSION_EXPIRY
            )

        # Call clear_sessions
        self.pool.clear_sessions()

        # Verify sessions were cleared
        for env in ['live', 'test']:
            self.assertIsNone(self.pool.cache.get(f'legacy_api_session_{env}'))


class TestGlobalFunctions(TestCase):
    """Tests for the global functions in auth.py."""

    @patch('pyerp.direct_api.auth.session_pool.get_session')
    def test_get_session(self, mock_get_session):
        """Test get_session global function."""
        # Set up mock
        mock_session = MagicMock()
        mock_get_session.return_value = mock_session

        # Call get_session
        session = get_session('test')

        # Verify the pool's get_session was called and the result passed
        # through
        mock_get_session.assert_called_once_with('test')
        self.assertEqual(session, mock_session)

    @patch('pyerp.direct_api.auth.get_session')
    def test_get_session_cookie(self, mock_get_session):
        """Test get_session_cookie global function."""
        # Set up mock
        mock_session = MagicMock()
        mock_session.get_cookie.return_value = 'test-cookie'
        mock_get_session.return_value = mock_session

        # Call get_session_cookie
        cookie = get_session_cookie('test')

        # Verify get_session was called and the cookie was retrieved
        mock_get_session.assert_called_once_with('test')
        mock_session.get_cookie.assert_called_once()
        self.assertEqual(cookie, 'test-cookie')
