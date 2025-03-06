"""
Authentication and session management for the direct_api module.

This module handles authentication with the legacy API and maintains session information.  # noqa: E501
"""

import logging
import threading
import time
import datetime
import requests
import os
import json
from typing import Dict, Optional, Any  # noqa: F401
from urllib.parse import urljoin
from django.core.cache import caches  # noqa: F401

from pyerp.direct_api.exceptions import (  # noqa: F401
    AuthenticationError, ConnectionError, ResponseError, SessionError  # noqa: E128
)
from pyerp.direct_api.settings import (  # noqa: F401
    API_ENVIRONMENTS,  # noqa: E128
    API_REQUEST_TIMEOUT,
    API_MAX_RETRIES,
    API_RETRY_BACKOFF_FACTOR,
    API_SESSION_EXPIRY,
    API_SESSION_CACHE_NAME,
    API_SESSION_CACHE_KEY_PREFIX,
    API_INFO_ENDPOINT
)

# Configure logging
logger = logging.getLogger(__name__)

# File for storing the session cookie globally - single cookie for all environments  # noqa: E501
COOKIE_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), '.global_session_cookie')  # noqa: E501

# Global lock for file operations
file_lock = threading.RLock()

# Global flag to track if we've hit session limits across the system
_SESSION_LIMIT_REACHED = False
_session_limit_lock = threading.RLock()


def set_session_limit_reached(reached=True):
    """
    Set the global session limit reached flag.

    Args:
        reached: Whether the session limit has been reached
    """
    global _SESSION_LIMIT_REACHED
    with _session_limit_lock:
        if reached and not _SESSION_LIMIT_REACHED:
            logger.warning("SESSION LIMIT REACHED: Setting global flag to prevent new session creation")  # noqa: E501
        _SESSION_LIMIT_REACHED = reached


def is_session_limit_reached():
    """
    Check if the session limit has been reached.

    Returns:
        bool: True if the session limit has been reached
    """
    with _session_limit_lock:
        return _SESSION_LIMIT_REACHED


class Session:
    """
    Represents an API session with the legacy system.

    This class handles authentication, session validity checking, and automatic refresh.  # noqa: E501
    """

    def __init__(self, environment: str = 'live'):
        """
        Initialize a new session.

        Args:
            environment: The environment to use ('live', 'test', etc.)
        """
        self.environment = environment
        self.cookie = None
        self.created_at = None

        # Load environment configuration
        try:
            self.config = API_ENVIRONMENTS[environment]
        except KeyError:
            raise ValueError(f"Unknown environment: {environment}. "
                            f"Available environments: {', '.join(API_ENVIRONMENTS.keys())}")  # noqa: E501

        # Check if we have required configuration
        if not self.config.get('base_url'):
            raise ValueError(f"Missing base_url in environment configuration for {environment}")  # noqa: E501

    def _load_cookie_from_file(self):
        """
        Load a session cookie from file.
        """
        with file_lock:
            if not os.path.exists(COOKIE_FILE):
                return False

            try:
                with open(COOKIE_FILE, 'r') as f:
                    cookie_data = json.load(f)

                # Very basic validation - just check if required fields exist
                if 'name' in cookie_data and 'value' in cookie_data:
                    self.cookie = cookie_data['value']
                    self.created_at = datetime.datetime.fromisoformat(cookie_data['created_at']) if 'created_at' in cookie_data else datetime.datetime.now()  # noqa: E501
                    logger.info(f"Loaded session cookie from file: {self.cookie[:30]}...")  # noqa: E501
                    return True

                return False
            except Exception as e:
                logger.warning(f"Error loading cookie from file: {e}")
                return False

    def _save_cookie_to_file(self):
        """
        Save the session cookie to file.
        """
        with file_lock:
            try:
                cookie_data = {
                    'name': 'WASID4D',  # Always use WASID4D as the cookie name  # noqa: E128
                    'value': self.cookie,
                    'created_at': self.created_at.isoformat() if self.created_at else datetime.datetime.now().isoformat()  # noqa: E501
                }

                with open(COOKIE_FILE, 'w') as f:
                    json.dump(cookie_data, f)

                logger.info(f"Saved session cookie to file: {self.cookie[:10]}...")  # noqa: E501
                return True
            except Exception as e:
                logger.warning(f"Error saving cookie to file: {e}")
                return False

    def is_valid(self) -> bool:
        """
        Check if the current session has a cookie.

        Returns:
            bool: True if the session has a cookie, False otherwise
        """
        return self.cookie is not None

    def refresh(self) -> None:
        """
        Refresh the session by authenticating with the legacy API.

        Raises:
            AuthenticationError: If authentication fails
            ConnectionError: If unable to connect to the API
            ResponseError: If the API returns an error response
        """
        # Check if we've hit the session limit - if so, don't create a new session  # noqa: E501
        if is_session_limit_reached():
            error_msg = "Cannot create a new session because the session limit has been reached (402 error)"  # noqa: E501
            logger.error(error_msg)
            raise AuthenticationError(error_msg)

        # Build the authentication URL
        base_url = self.config['base_url']
        auth_url = urljoin(base_url, API_INFO_ENDPOINT)

        # Prepare for retries
        retries = 0
        last_error = None

        while retries <= API_MAX_RETRIES:
            try:
                # Make the authentication request
                logger.debug(f"Authenticating with {auth_url}")
                response = requests.get(
                    auth_url,  # noqa: E128
                    timeout=API_REQUEST_TIMEOUT  # noqa: F841
  # noqa: F841
                )

                # Check if we got a 402 error - if so, mark that we've hit the session limit  # noqa: E501
                if response.status_code == 402:
                    set_session_limit_reached(True)
                    error_msg = "Too many sessions error (402) during authentication"  # noqa: E501
                    logger.error(error_msg)
                    raise AuthenticationError(error_msg)

                # Check if we got a cookie (even with 404 status)
                if 'Set-Cookie' in response.headers:
                    cookie_header = response.headers['Set-Cookie']

                    # Extract just the cookie value by parsing the Set-Cookie header  # noqa: E501
                    # Set-Cookie header format is typically: name=value; path=/; domain=.example.com; ...  # noqa: E501
                    # We want to extract just the value part
                    if '=' in cookie_header:
                        # Check specifically for WASID4D in the Set-Cookie header  # noqa: E501
                        if 'WASID4D=' in cookie_header:
                            # Extract WASID4D value
                            start_index = cookie_header.find('WASID4D=') + 8  # Length of 'WASID4D='  # noqa: E501
                            end_index = cookie_header.find(';', start_index)
                            if end_index == -1:  # No semicolon found, take the rest of the string  # noqa: E501
                                end_index = len(cookie_header)

                            cookie_value = cookie_header[start_index:end_index].strip()  # noqa: E501
                            logger.info("Found WASID4D in Set-Cookie header")

                            # Store just the value
                            self.cookie = cookie_value
                            logger.info(f"Stored WASID4D cookie value: {cookie_value[:10]}...")  # noqa: E501
                            self.created_at = datetime.datetime.now()

                            # Save the cookie to file for persistence
                            self._save_cookie_to_file()
                            return

                        # If no WASID4D found, fall back to general parsing
                        cookie_parts = cookie_header.split(';')[0].split('=', 1)  # noqa: E501
                        if len(cookie_parts) == 2:
                            cookie_name = cookie_parts[0].strip()
                            cookie_value = cookie_parts[1].strip()
                            logger.info(f"Extracted cookie name: {cookie_name}")  # noqa: E501


  # noqa: F841
                            self.cookie = cookie_value
                            logger.info(f"Stored cookie value: {cookie_value[:10]}...")  # noqa: E501
                        else:
                            # Fallback to the full header if parsing fails
                            logger.warning("Failed to parse cookie header, using full header as fallback")  # noqa: E501
                            self.cookie = cookie_header
                    else:
                        # Fallback to the full header if format is unexpected
                        logger.warning("Unexpected cookie format, using full header as fallback")  # noqa: E501
                        self.cookie = cookie_header

                    self.created_at = datetime.datetime.now()
                    logger.info(f"Successfully obtained session cookie for {self.environment}")  # noqa: E501

                    # Save the cookie to file for persistence
                    self._save_cookie_to_file()
                    return

                # Also check if cookies were set in the response's cookies attribute  # noqa: E501
                elif response.cookies:
                    # Always prioritize WASID4D cookies
                    if 'WASID4D' in response.cookies:
                        # Extract just the value
                        cookie_value = response.cookies['WASID4D']
                        logger.info("Found WASID4D cookie in response.cookies")

                        # Store just the value
                        self.cookie = cookie_value
                        logger.info(f"Stored WASID4D cookie value: {cookie_value[:10]}...")  # noqa: E501
                        self.created_at = datetime.datetime.now()

                        # Save the cookie to file for persistence
                        self._save_cookie_to_file()
                        return
                    # Fall back to 4DSID_WSZ-DB only if WASID4D is not available  # noqa: E501
                    elif '4DSID_WSZ-DB' in response.cookies:
                        # Extract just the value
                        cookie_value = response.cookies['4DSID_WSZ-DB']
                        logger.info("Found 4DSID_WSZ-DB cookie in response.cookies (will use as WASID4D)")  # noqa: E501

                        # Store just the value
                        self.cookie = cookie_value
                        logger.info(f"Stored 4DSID_WSZ-DB cookie value as WASID4D: {cookie_value[:10]}...")  # noqa: E501
                        self.created_at = datetime.datetime.now()

                        # Save the cookie to file for persistence
                        self._save_cookie_to_file()
                        return

                # No cookie found in response
                error_msg = f"No session cookie returned by the API (status {response.status_code})"  # noqa: E501
                logger.error(error_msg)
                raise AuthenticationError(error_msg)

            except requests.RequestException as e:
                # Handle connection errors
                last_error = e
                logger.warning(f"Connection error during authentication: {e}")

                # Calculate backoff time for retry
                backoff = API_RETRY_BACKOFF_FACTOR * (2 ** retries)
                retries += 1

                if retries <= API_MAX_RETRIES:
                    logger.info(f"Retrying authentication in {backoff:.2f} seconds (attempt {retries}/{API_MAX_RETRIES})")  # noqa: E501
                    time.sleep(backoff)
                else:
                    logger.error(f"Authentication failed after {retries-1} retries")  # noqa: E501
                    raise ConnectionError(f"Unable to connect to the API after {retries-1} retries") from last_error  # noqa: E501

            except Exception as e:
                # Handle other exceptions
                logger.error(f"Unexpected error during authentication: {e}")
                raise

        # This should not be reached due to the retry logic above, but just in case  # noqa: E501
        if last_error:
            raise ConnectionError("Unable to connect to the API") from last_error  # noqa: E501

    def get_cookie(self) -> str:
        """
        Get the session cookie, refreshing if necessary.

        Returns:
            str: The session cookie for API requests

        Raises:
            AuthenticationError: If authentication fails
            ConnectionError: If unable to connect to the API
        """
        # Refresh if we don't have a cookie
        if not self.is_valid():
            # Check if we've hit the session limit
            if is_session_limit_reached():
                error_msg = "Cannot create a new session because the session limit has been reached (402 error)"  # noqa: E501
                logger.error(error_msg)
                raise AuthenticationError(error_msg)

            logger.debug("No cookie available, refreshing session")
            self.refresh()

        return self.cookie

    def ensure_valid(self) -> None:
        """
        Ensure that the session is valid, refreshing if necessary.

        Raises:
            AuthenticationError: If authentication fails
            ConnectionError: If unable to connect to the API
        """
        # Try to load an existing cookie from file if we don't have one yet
        if not self.is_valid() and not self._load_cookie_from_file():
            # Check if we've hit the session limit
            if is_session_limit_reached():
                error_msg = "Cannot create a new session because the session limit has been reached (402 error)"  # noqa: E501
                logger.error(error_msg)
                raise AuthenticationError(error_msg)

            logger.debug("No valid cookie found, refreshing session")
            self.refresh()

    def invalidate(self) -> None:
        """
        Invalidate the current session.
        """
        self.cookie = None
        self.created_at = None
  # noqa: F841

        # Remove the cookie file if it exists
        with file_lock:
            if os.path.exists(COOKIE_FILE):
                try:
                    os.remove(COOKIE_FILE)
                    logger.info(f"Removed session cookie file: {COOKIE_FILE}")
                except Exception as e:
                    logger.warning(f"Failed to remove session cookie file: {e}")  # noqa: E501


# Session pool for reusing sessions
_session_pool = {}
_session_pool_lock = threading.RLock()


def get_session(environment: str = 'live') -> Session:
    """
    Get a session for the specified environment.

    Args:
        environment: The environment to use ('live', 'test', etc.)

    Returns:
        Session: A session for the specified environment
    """
    with _session_pool_lock:
        if environment not in _session_pool:
            _session_pool[environment] = Session(environment)

        return _session_pool[environment]


def invalidate_session(environment: str = 'live') -> None:
    """
    Invalidate the session for the specified environment.

    Args:
        environment: The environment to use ('live', 'test', etc.)
    """
    with _session_pool_lock:
        if environment in _session_pool:
            _session_pool[environment].invalidate()
            del _session_pool[environment]


def get_session_cookie(environment: str = 'live') -> str:
    """
    Get a session cookie for the specified environment.

    This is a compatibility function for the legacy WSZ_api.auth.get_session_cookie.  # noqa: E501

    Args:
        environment: The environment to use ('live', 'test', etc.)

    Returns:
        str: The session cookie for API requests
    """
    # Check if we've hit the session limit
    if is_session_limit_reached():
        error_msg = "Cannot get session cookie because the session limit has been reached (402 error)"  # noqa: E501
        logger.error(error_msg)
        raise AuthenticationError(error_msg)

    return get_session(environment).get_cookie()
