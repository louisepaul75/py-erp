"""
Authentication and session management for the legacy ERP API.

This module handles authentication with the legacy API and maintains session info.
"""

import logging
import os
import threading
import warnings

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


# Placeholder functions for backward compatibility
def get_session(environment="live"):
    """
    Placeholder function for getting a session.
    This will be fully implemented when the auth module is completed.
    """
    warnings.warn(
        "This is a placeholder implementation. Full implementation pending.",
        RuntimeWarning,
    )
    return None


def invalidate_session(environment="live"):
    """
    Placeholder function for invalidating a session.
    This will be fully implemented when the auth module is completed.
    """
    warnings.warn(
        "This is a placeholder implementation. Full implementation pending.",
        RuntimeWarning,
    )
    return None 