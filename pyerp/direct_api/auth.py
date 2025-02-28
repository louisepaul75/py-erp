"""
Authentication and session management for the direct_api module.

This module handles authentication with the legacy API and maintains session information.
"""

import logging
import threading
import time
import datetime
import requests
import os
import json
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
    API_SESSION_CACHE_NAME,
    API_SESSION_CACHE_KEY_PREFIX,
    API_INFO_ENDPOINT
)

# Configure logging
logger = logging.getLogger(__name__)

# File for storing the session cookie globally - single cookie for all environments
COOKIE_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), '.global_session_cookie')

# Global lock for file operations
file_lock = threading.RLock()


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
        
        # Load environment configuration
        try:
            self.config = API_ENVIRONMENTS[environment]
        except KeyError:
            raise ValueError(f"Unknown environment: {environment}. "
                            f"Available environments: {', '.join(API_ENVIRONMENTS.keys())}")
        
        # Check if we have required configuration
        if not self.config.get('base_url'):
            raise ValueError(f"Missing base_url in environment configuration for {environment}")
    
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
                    self.created_at = datetime.datetime.fromisoformat(cookie_data['created_at']) if 'created_at' in cookie_data else datetime.datetime.now()
                    logger.info(f"Loaded session cookie from file: {self.cookie[:30]}...")
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
                    'name': 'session_cookie',
                    'value': self.cookie,
                    'created_at': self.created_at.isoformat() if self.created_at else datetime.datetime.now().isoformat()
                }
                
                with open(COOKIE_FILE, 'w') as f:
                    json.dump(cookie_data, f)
                
                logger.info(f"Saved session cookie to file: {self.cookie[:30]}...")
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
                
                # Check if we got a cookie (even with 404 status)
                if 'Set-Cookie' in response.headers:
                    cookie_header = response.headers['Set-Cookie']
                    # Parse the cookie and store the value
                    self.cookie = cookie_header
                    self.created_at = datetime.datetime.now()
                    logger.info(f"Successfully obtained session cookie for {self.environment}")
                    
                    # Save the cookie to file for persistence
                    self._save_cookie_to_file()
                    return
                else:
                    # No cookie in response
                    error_msg = f"No session cookie returned by the API (status {response.status_code})"
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
            # Try to load from file first
            if not self._load_cookie_from_file():
                # If not in file, refresh
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
        self.sessions = {}
    
    def get_session(self, environment: str = 'live') -> Session:
        """
        Get a session for the specified environment, creating a new one if needed.
        
        Args:
            environment: The environment to use ('live', 'test', etc.)
            
        Returns:
            Session: A valid session for the specified environment
        """
        with self.lock:
            # Check if we already have a session object in memory
            if environment in self.sessions:
                logger.debug(f"Using existing session object for {environment}")
                return self.sessions[environment]
            
            # Create a new session
            session = Session(environment)
            
            # Try to get a cookie (will load from file or refresh if needed)
            session.get_cookie()
            
            # Store in memory
            self.sessions[environment] = session
            
            return session
    
    def invalidate_session(self, environment: str = 'live'):
        """
        Invalidate the session for the specified environment.
        
        Args:
            environment: The environment to invalidate the session for
        """
        with self.lock:
            # Remove from memory
            if environment in self.sessions:
                del self.sessions[environment]
            
            # Remove from cache
            cache_key = f"{API_SESSION_CACHE_KEY_PREFIX}{environment}"
            self.cache.delete(cache_key)
            
            # Remove from file
            if os.path.exists(COOKIE_FILE):
                try:
                    os.remove(COOKIE_FILE)
                    logger.info(f"Removed session cookie file")
                except Exception as e:
                    logger.warning(f"Error removing cookie file: {e}")
            
            logger.info(f"Invalidated session for {environment}")
    
    def clear_sessions(self):
        """Clear all sessions from the cache."""
        with self.lock:
            # Clear memory
            self.sessions = {}
            
            # Clear cache
            for env in API_ENVIRONMENTS.keys():
                cache_key = f"{API_SESSION_CACHE_KEY_PREFIX}{env}"
                self.cache.delete(cache_key)
            
            # Clear file
            if os.path.exists(COOKIE_FILE):
                try:
                    os.remove(COOKIE_FILE)
                    logger.info(f"Removed session cookie file")
                except Exception as e:
                    logger.warning(f"Error removing cookie file: {e}")
            
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

def invalidate_session(environment: str = 'live'):
    """
    Invalidate the session for the specified environment.
    
    Args:
        environment: The environment to invalidate the session for
    """
    session_pool.invalidate_session(environment)

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