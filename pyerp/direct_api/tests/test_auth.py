"""Tests for authentication module."""
from datetime import datetime
from unittest.mock import MagicMock, patch, call
import requests
from urllib.parse import urljoin

from django.test import TestCase, override_settings

from pyerp.direct_api.auth import (
    Session,
    SessionPool,
    get_session,
    get_session_cookie,
)
from pyerp.direct_api.exceptions import AuthenticationError, ConnectionError
from pyerp.direct_api.settings import (
    API_SESSION_EXPIRY,
    API_SESSION_REFRESH_MARGIN,
    API_MAX_RETRIES,
    API_REQUEST_TIMEOUT,
    API_INFO_ENDPOINT,
)


TEST_API_ENVIRONMENTS = {
    "test": {
        "base_url": "http://192.168.73.26:8090",
        "username": "test",
        "password": "test",
    },
    "live": {
        "base_url": "http://192.168.73.26:8090",
        "username": "live",
        "password": "live",
    },
}


@override_settings(LEGACY_API_ENVIRONMENTS=TEST_API_ENVIRONMENTS)
class TestSession(TestCase):
    """Test cases for Session class."""

    def setUp(self):
        """Set up test environment."""
        self.session = Session(environment="test")

    def test_init(self):
        """Test initialization with default and custom parameters."""
        session = Session()
        self.assertEqual(session.environment, "live")
        self.assertIsNone(session.cookie)
        self.assertIsNone(session.created_at)
        self.assertIsNone(session.expires_at)

        # Test with custom parameters
        session = Session(environment="test")
        self.assertEqual(session.environment, "test")
        self.assertIsNone(session.cookie)
        self.assertIsNone(session.created_at)
        self.assertIsNone(session.expires_at)

    def test_init_invalid_environment(self):
        """Test initialization with invalid environment."""
        with self.assertRaises(ValueError):
            Session(environment="invalid")

    def test_is_valid_no_cookie(self):
        """Test is_valid with no cookie."""
        self.assertFalse(self.session.is_valid())

    def test_is_valid_no_expiry(self):
        """Test is_valid with cookie but no expiry."""
        self.session.cookie = "test-cookie"
        self.assertFalse(self.session.is_valid())

    def test_is_valid_expired(self):
        """Test is_valid with expired cookie."""
        self.session.cookie = "test-cookie"
        self.session.created_at = datetime.datetime.now() - datetime.timedelta(
            seconds=API_SESSION_EXPIRY + 1,
        )
        self.session.expires_at = self.session.created_at + datetime.timedelta(
            seconds=API_SESSION_EXPIRY,
        )
        self.assertFalse(self.session.is_valid())

    def test_is_valid_near_expiry(self):
        """Test is_valid with cookie near expiry (within refresh margin)."""
        self.session.cookie = "test-cookie"
        self.session.created_at = datetime.datetime.now() - datetime.timedelta(
            seconds=API_SESSION_EXPIRY - API_SESSION_REFRESH_MARGIN / 2,
        )
        self.session.expires_at = self.session.created_at + datetime.timedelta(
            seconds=API_SESSION_EXPIRY,
        )
        self.assertFalse(self.session.is_valid())

    def test_is_valid_good(self):
        """Test is_valid with valid cookie."""
        self.session.cookie = "test-cookie"
        self.session.created_at = datetime.datetime.now()
        self.session.expires_at = self.session.created_at + datetime.timedelta(
            seconds=API_SESSION_EXPIRY,
        )
        self.assertTrue(self.session.is_valid())

    @patch("pyerp.direct_api.auth.requests.get")
    def test_refresh_success(self, mock_get):
        """Test refresh with successful response."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.headers = {"Set-Cookie": "session=test-cookie"}
        mock_get.return_value = mock_response

        # Call refresh
        self.session.refresh()

        # Verify the result
        self.assertEqual(self.session.cookie, "session=test-cookie")
        self.assertIsNotNone(self.session.created_at)
        self.assertIsNotNone(self.session.expires_at)
        self.assertEqual(
            self.session.expires_at - self.session.created_at,
            datetime.timedelta(seconds=API_SESSION_EXPIRY),
        )

        # Verify the call
        mock_get.assert_called_once_with(
            "http://192.168.73.26:8090/$info",
            timeout=30,
        )

    @patch("pyerp.direct_api.auth.requests.get")
    def test_refresh_no_cookie(self, mock_get):
        """Test refresh with successful response but no cookie."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.headers = {}
        mock_get.return_value = mock_response

        # Call refresh and expect an exception
        with self.assertRaises(AuthenticationError):
            self.session.refresh()

    @patch("pyerp.direct_api.auth.requests.get")
    def test_refresh_error_response(self, mock_get):
        """Test refresh with error response."""
        mock_response = MagicMock()
        mock_response.status_code = 401
        mock_response.text = "Unauthorized"
        mock_get.return_value = mock_response

        # Call refresh and expect an exception
        with self.assertRaises(AuthenticationError):
            self.session.refresh()

        # Verify the call
        mock_get.assert_called_once_with(
            "http://192.168.73.26:8090/$info",
            timeout=30,
        )

    @patch("pyerp.direct_api.auth.requests.get")
    @patch("pyerp.direct_api.auth.time.sleep")
    def test_refresh_connection_error_retry(self, mock_sleep, mock_get):
        """Test refresh with connection error that succeeds on retry."""
        mock_get.side_effect = [
            requests.RequestException("Connection error"),
            MagicMock(
                status_code=200,
                headers={"Set-Cookie": "session=test-cookie"},
            ),
        ]

        # Call refresh
        self.session.refresh()

        # Verify the result
        self.assertEqual(self.session.cookie, "session=test-cookie")
        self.assertIsNotNone(self.session.created_at)
        self.assertIsNotNone(self.session.expires_at)

        # Verify the calls
        self.assertEqual(mock_get.call_count, 2)
        mock_sleep.assert_called_once()

    @patch("pyerp.direct_api.auth.requests.get")
    @patch("pyerp.direct_api.auth.time.sleep")
    @override_settings(LEGACY_API_MAX_RETRIES=3)
    def test_refresh_connection_error_max_retries(self, mock_sleep, mock_get):
        """Test refresh with connection error that fails even after retries.
        
        This test verifies that:
        1. The session attempts to connect 4 times (1 initial + 3 retries)
        2. Each retry uses exponential backoff for delays
        3. After all retries fail, a ConnectionError is raised
        """
        # Ensure we're using the correct number of retries
        self.assertEqual(
            API_MAX_RETRIES,
            3,
            "API_MAX_RETRIES should be 3",
        )
        
        # Set up mock to consistently raise RequestException
        mock_get.side_effect = requests.RequestException(
            "Connection error",
        )

        # Verify that refresh() raises ConnectionError with correct message
        expected_msg = "Unable to connect to the API after 3 retries"
        with self.assertRaisesRegex(ConnectionError, expected_msg):
            self.session.refresh()

        # Verify exactly 4 calls were made (1 initial + 3 retries)
        self.assertEqual(
            mock_get.call_count,
            4,
            "Expected 4 connection attempts (1 initial + 3 retries)",
        )

        # Verify sleep was called 3 times with exponential backoff
        expected_sleep_calls = [
            call(0.5),  # First retry
            call(1.0),  # Second retry
            call(2.0),  # Third retry
        ]
        mock_sleep.assert_has_calls(expected_sleep_calls)
        self.assertEqual(
            mock_sleep.call_count,
            3,
            "Expected 3 sleep calls",
        )

        # Verify all calls were made with correct URL and timeout
        base_url = TEST_API_ENVIRONMENTS["test"]["base_url"]
        expected_url = urljoin(base_url, API_INFO_ENDPOINT)
        for call_args in mock_get.call_args_list:
            args, kwargs = call_args
            self.assertEqual(
                args[0],
                expected_url,
                "Incorrect URL used for refresh",
            )
            self.assertEqual(
                kwargs.get("timeout"),
                API_REQUEST_TIMEOUT,
                "Incorrect timeout used for refresh",
            )

    @patch("pyerp.direct_api.auth.Session.refresh")
    def test_get_cookie_valid(self, mock_refresh):
        """Test get_cookie with valid session."""
        self.session.cookie = "test-cookie"
        self.session.created_at = datetime.datetime.now()
        self.session.expires_at = self.session.created_at + datetime.timedelta(
            seconds=API_SESSION_EXPIRY,
        )

        # Call get_cookie
        cookie = self.session.get_cookie()

        # Verify the result and that refresh wasn't called
        self.assertEqual(cookie, "test-cookie")
        mock_refresh.assert_not_called()

    @patch("pyerp.direct_api.auth.Session.refresh")
    def test_get_cookie_invalid(self, mock_refresh):
        """Test get_cookie with invalid session."""
        self.session.get_cookie()

        # Verify refresh was called
        mock_refresh.assert_called_once()


class TestSessionPool(TestCase):
    """Tests for the SessionPool class."""

    def setUp(self):
        """Set up test environment."""
        self.pool = SessionPool()

    @patch("pyerp.direct_api.auth.Session")
    def test_get_session_new(self, mock_session_class):
        """Test get_session with no cached session."""
        mock_session = MagicMock()
        mock_session.cookie = "test-cookie"
        mock_session.created_at = datetime.datetime.now()
        mock_session.expires_at = mock_session.created_at + datetime.timedelta(
            seconds=API_SESSION_EXPIRY,
        )
        mock_session_class.return_value = mock_session

        # Call get_session
        session = self.pool.get_session("test")

        # Verify a new session was created and refreshed
        mock_session_class.assert_called_once_with("test")
        self.assertEqual(session, mock_session)
        mock_session.ensure_valid.assert_called_once()

        # Clear any sessions from cache
        self.pool.clear_sessions()

    @patch("pyerp.direct_api.auth.Session")
    def test_get_session_cached_valid(self, mock_session_class):
        """Test get_session with valid cached session."""
        mock_session = MagicMock()
        mock_session.is_valid.return_value = True
        mock_session_class.return_value = mock_session

        # Store session in cache dictionary
        self.pool.cache["test"] = mock_session

        # Call get_session
        session = self.pool.get_session("test")

        # Verify cached session was returned
        self.assertEqual(session, mock_session)
        mock_session_class.assert_not_called()

        # Clear any sessions from cache
        self.pool.clear_sessions()

    @patch("pyerp.direct_api.auth.Session")
    def test_get_session_cached_invalid(self, mock_session_class):
        """Test get_session with invalid cached session."""
        mock_session = MagicMock()
        mock_session.is_valid.return_value = False
        mock_session_class.return_value = mock_session

        # Store invalid session in cache dictionary
        self.pool.cache["test"] = mock_session

        # Call get_session
        session = self.pool.get_session("test")

        # Verify new session was created
        mock_session_class.assert_called_once_with("test")
        self.assertEqual(session, mock_session)
        mock_session.ensure_valid.assert_called_once()

        # Clear any sessions from cache
        self.pool.clear_sessions()

    def test_clear_sessions(self):
        """Test clear_sessions method."""
        # Add some sessions to the cache dictionary
        self.pool.cache["live"] = MagicMock()
        self.pool.cache["test"] = MagicMock()

        # Call clear_sessions
        self.pool.clear_sessions()

        # Verify sessions were cleared
        self.assertEqual(len(self.pool.cache), 0)
        self.assertEqual(len(self.pool._sessions), 0)


class TestGlobalFunctions(TestCase):
    """Tests for the global functions in auth.py."""

    @patch("pyerp.direct_api.auth._session_pool.get_session")
    def test_get_session(self, mock_get_session):
        """Test get_session global function."""
        mock_session = MagicMock()
        mock_get_session.return_value = mock_session

        # Call get_session
        session = get_session("test")

        # Verify the pool's get_session was called and result passed through
        mock_get_session.assert_called_once_with("test")
        self.assertEqual(session, mock_session)

    @patch("pyerp.direct_api.auth.get_session")
    def test_get_session_cookie(self, mock_get_session):
        """Test get_session_cookie global function."""
        mock_session = MagicMock()
        mock_session.get_cookie.return_value = "test-cookie"
        mock_get_session.return_value = mock_session

        # Call get_session_cookie and verify result
        self.assertEqual(get_session_cookie("test"), "test-cookie")

        # Verify get_session was called and the cookie was retrieved
        mock_get_session.assert_called_once_with("test")
        mock_session.get_cookie.assert_called_once()
