"""
Authentication and session management for the legacy API.

This module handles authentication with the legacy API and maintains session
info.
"""

import logging
import os
import threading
import json
import requests
from datetime import datetime

from pyerp.external_api.legacy_erp.settings import (
    API_ENVIRONMENTS,
    API_SESSION_EXPIRY,
)

# Configure logging
logger = logging.getLogger(__name__)

# File for storing the session cookie globally
COOKIE_FILE = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    ".global_session_cookie",
)

# Global lock for file operations
file_lock = threading.RLock()

# Global flag to track if we've hit session limits across the system
_SESSION_LIMIT_REACHED = False
_session_limit_lock = threading.RLock()

# Global session cache
_sessions = {}
_sessions_lock = threading.RLock()


def set_session_limit_reached(reached=True):
    """
    Set the global session limit reached flag.
    
    Args:
        reached: Whether the session limit has been reached
    """
    global _SESSION_LIMIT_REACHED
    with _session_limit_lock:
        _SESSION_LIMIT_REACHED = reached
        if reached:
            logger.warning("Session limit reached flag has been set")
        else:
            logger.info("Session limit reached flag has been cleared")


def is_session_limit_reached():
    """
    Check if the global session limit reached flag is set.
    
    Returns:
        bool: Whether the session limit has been reached
    """
    with _session_limit_lock:
        return _SESSION_LIMIT_REACHED


def _create_session(environment="live"):
    """
    Create a new session by authenticating with the legacy API.
    
    Args:
        environment: Which API environment to use ('live', 'test', etc.)
        
    Returns:
        requests.Session: Authenticated session object
        
    Raises:
        ValueError: If environment config is invalid
        ConnectionError: If authentication fails
    """
    env_config = API_ENVIRONMENTS.get(environment)
    if not env_config:
        raise ValueError(f"Invalid environment: {environment}")
        
    base_url = env_config.get('base_url')
    username = env_config.get('username')
    password = env_config.get('password')
    
    if not all([base_url, username, password]):
        raise ValueError(
            f"Missing required credentials for environment: {environment}"
        )
    
    session = requests.Session()
    session.auth = (username, password)
    session.headers.update({
        'Content-Type': 'application/json',
        'Accept': 'application/json',
    })
    
    # Store session creation time
    session.created_at = datetime.now()
    
    return session


def get_session(environment="live"):
    """
    Get an authenticated session for the legacy API.
    Creates a new session if one doesn't exist or has expired.
    
    Args:
        environment: Which API environment to use ('live', 'test', etc.)
        
    Returns:
        requests.Session: Authenticated session object
        
    Raises:
        ValueError: If environment config is invalid
        ConnectionError: If authentication fails
    """
    with _sessions_lock:
        session = _sessions.get(environment)
        
        # Check if session exists and is still valid
        if session:
            age = datetime.now() - session.created_at
            if age.total_seconds() < API_SESSION_EXPIRY:
                return session
                
        # Create new session
        try:
            session = _create_session(environment)
            _sessions[environment] = session
            return session
        except Exception as e:
            logger.error(f"Failed to create session: {e}")
            return None


def invalidate_session(environment="live"):
    """
    Invalidate the session for the given environment.
    
    Args:
        environment: Which API environment to use ('live', 'test', etc.)
    """
    with _sessions_lock:
        if environment in _sessions:
            session = _sessions.pop(environment)
            try:
                session.close()
            except Exception:
                pass
            logger.info(f"Invalidated session for environment: {environment}") 