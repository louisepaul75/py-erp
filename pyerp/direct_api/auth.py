"""
Authentication and session management for the direct_api module.

This module handles authentication with the legacy API and maintains session information.
"""

import logging
import threading
import time
import datetime
import requests
from typing import Dict, Optional, Any
from urllib.parse import urljoin
from django.core.cache import caches

from pyerp.direct_api.exceptions import (
    AuthenticationError, ConnectionError, ResponseError, SessionError
)
from pyerp.direct_api.settings import (
    API_ENVIRONMENTS, 
    API_REQUEST_TIMEOUT,
    API_MAX_RETRIES,
    API_RETRY_BACKOFF_FACTOR,
    API_SESSION_EXPIRY,
    API_SESSION_REFRESH_MARGIN,
    API_SESSION_CACHE_NAME,
    API_SESSION_CACHE_KEY_PREFIX,
    API_INFO_ENDPOINT
)

# Configure logging
logger = logging.getLogger(__name__)


class Session:
    """
    Represents an API session with the legacy system.
    
    This class handles authentication, session validity checking, and automatic refresh.
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
        self.expires_at = None
        
        # Load environment configuration
        try:
            self.config = API_ENVIRONMENTS[environment]
        except KeyError:
            raise ValueError(f"Unknown environment: {environment}. "
                            f"Available environments: {', '.join(API_ENVIRONMENTS.keys())}")
        
        # Check if we have required configuration
        if not self.config.get('base_url'):
            raise ValueError(f"Missing base_url in environment configuration for {environment}")
            
    def is_valid(self) -> bool:
        """
        Check if the current session is valid and not expired.
        
        Returns:
            bool: True if the session is valid, False otherwise
        """
        if not self.cookie or not self.expires_at:
            return False
        
        # Add a margin to ensure we refresh before expiry
        refresh_time = self.expires_at - datetime.timedelta(seconds=API_SESSION_REFRESH_MARGIN)
        return datetime.datetime.now() < refresh_time
    
    def refresh(self) -> None:
        """
        Refresh the session by authenticating with the legacy API.
        
        Raises:
            AuthenticationError: If authentication fails
            ConnectionError: If unable to connect to the API
            ResponseError: If the API returns an error response
        """
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
                    auth_url,
                    timeout=API_REQUEST_TIMEOUT
                )
                
                # Check if we got a successful response
                if response.status_code == 200:
                    # Extract the session cookie
                    if 'Set-Cookie' in response.headers:
                        cookie_header = response.headers['Set-Cookie']
                        # Parse the cookie and store the value
                        # This is a simplification - in reality you'd want to parse the cookie properly
                        self.cookie = cookie_header
                        self.created_at = datetime.datetime.now()
                        self.expires_at = self.created_at + datetime.timedelta(seconds=API_SESSION_EXPIRY)
                        logger.info(f"Successfully obtained session cookie for {self.environment}")
                        return
                    else:
                        raise AuthenticationError("No session cookie returned by the API")
                else:
                    # Handle error responses
                    error_msg = f"Authentication failed with status {response.status_code}"
                    logger.error(error_msg)
                    raise ResponseError(response.status_code, error_msg, response.text)
                    
            except requests.RequestException as e:
                # Handle connection errors
                last_error = e
                logger.warning(f"Connection error during authentication: {e}")
                
                # Calculate backoff time for retry
                backoff = API_RETRY_BACKOFF_FACTOR * (2 ** retries)
                retries += 1
                
                if retries <= API_MAX_RETRIES:
                    logger.info(f"Retrying authentication in {backoff:.2f} seconds (attempt {retries}/{API_MAX_RETRIES})")
                    time.sleep(backoff)
                else:
                    logger.error(f"Authentication failed after {retries-1} retries")
                    raise ConnectionError(f"Unable to connect to the API after {retries-1} retries") from last_error
                    
            except Exception as e:
                # Handle other exceptions
                logger.error(f"Unexpected error during authentication: {e}")
                raise
        
        # This should not be reached due to the retry logic above, but just in case
        if last_error:
            raise ConnectionError(f"Unable to connect to the API") from last_error
    
    def get_cookie(self) -> str:
        """
        Get the session cookie, refreshing if necessary.
        
        Returns:
            str: The session cookie for API requests
            
        Raises:
            AuthenticationError: If authentication fails
        """
        if not self.is_valid():
            self.refresh()
        return self.cookie


class SessionPool:
    """
    Pool of API sessions for different environments.
    
    This class manages a pool of sessions and ensures they are properly cached
    and thread-safe.
    """
    
    def __init__(self):
        """Initialize the session pool."""
        self.lock = threading.RLock()
        self.cache = caches[API_SESSION_CACHE_NAME]
    
    def get_session(self, environment: str = 'live') -> Session:
        """
        Get a session for the specified environment, creating a new one if needed.
        
        Args:
            environment: The environment to use ('live', 'test', etc.)
            
        Returns:
            Session: A valid session for the specified environment
        """
        cache_key = f"{API_SESSION_CACHE_KEY_PREFIX}{environment}"
        
        with self.lock:
            # Try to get the session from cache
            session_data = self.cache.get(cache_key)
            
            if session_data:
                # Deserialize the session data
                session = Session(environment)
                session.cookie = session_data.get('cookie')
                session.created_at = session_data.get('created_at')
                session.expires_at = session_data.get('expires_at')
                
                # Check if the session is still valid
                if session.is_valid():
                    logger.debug(f"Using cached session for {environment}")
                    return session
                else:
                    logger.debug(f"Cached session for {environment} expired, refreshing")
            else:
                logger.debug(f"No cached session for {environment}, creating new one")
            
            # Create a new session
            session = Session(environment)
            session.refresh()
            
            # Cache the session data
            session_data = {
                'cookie': session.cookie,
                'created_at': session.created_at,
                'expires_at': session.expires_at,
            }
            self.cache.set(cache_key, session_data, API_SESSION_EXPIRY)
            
            return session
    
    def clear_sessions(self):
        """Clear all sessions from the cache."""
        # This is primarily for testing purposes
        for env in API_ENVIRONMENTS.keys():
            cache_key = f"{API_SESSION_CACHE_KEY_PREFIX}{env}"
            self.cache.delete(cache_key)
        logger.debug("Cleared all sessions from cache")


# Create a global session pool
session_pool = SessionPool()

def get_session(environment: str = 'live') -> Session:
    """
    Get a session for the specified environment.
    
    This is a convenience function that uses the global session pool.
    
    Args:
        environment: The environment to use ('live', 'test', etc.)
        
    Returns:
        Session: A valid session for the specified environment
    """
    return session_pool.get_session(environment)

def get_session_cookie(environment: str = 'live') -> str:
    """
    Get a session cookie for the specified environment.
    
    This is a compatibility function for the legacy WSZ_api.auth.get_session_cookie.
    
    Args:
        environment: The environment to use ('live', 'test', etc.)
        
    Returns:
        str: The session cookie for API requests
    """
    return get_session(environment).get_cookie() 