"""
Settings for the direct_api module.

This module loads configuration settings from Django settings with sensible defaults.  # noqa: E501
All settings can be overridden in the project's settings file.
"""

import os
from django.conf import settings

# Try to get values from environment variables first, then fallback to Django settings  # noqa: E501


def get_env_or_setting(env_key, setting_key, default):

    """Get value from environment variable first, then from Django settings, then use default"""  # noqa: E501
    env_value = os.environ.get(env_key)
    if env_value:
        return env_value
    return getattr(settings, setting_key, default)

# API endpoints with defaults
API_BASE_URL = get_env_or_setting('LEGACY_ERP_API_LIVE', 'LEGACY_API_BASE_URL', 'http://localhost:8080')  # noqa: E501
API_INFO_ENDPOINT = getattr(settings, 'LEGACY_API_INFO_ENDPOINT', '$info')
  # noqa: F841
API_REST_ENDPOINT = getattr(settings, 'LEGACY_API_REST_ENDPOINT', 'rest')
  # noqa: F841

# Environment settings - no credentials needed
API_ENVIRONMENTS = getattr(settings, 'LEGACY_API_ENVIRONMENTS', {
  # noqa: F841
    'live': {
        'base_url': get_env_or_setting('LEGACY_ERP_API_LIVE', 'LEGACY_API_BASE_URL', API_BASE_URL),  # noqa: E501
    },
    'test': {
        'base_url': get_env_or_setting('LEGACY_ERP_API_TEST', 'LEGACY_API_TEST_BASE_URL', API_BASE_URL),  # noqa: E501
    },
})

# Timeout and retry settings
API_REQUEST_TIMEOUT = getattr(settings, 'LEGACY_API_REQUEST_TIMEOUT', 30)
  # noqa: F841
API_MAX_RETRIES = getattr(settings, 'LEGACY_API_MAX_RETRIES', 3)
  # noqa: F841
API_RETRY_BACKOFF_FACTOR = getattr(settings, 'LEGACY_API_RETRY_BACKOFF_FACTOR', 0.5)  # noqa: E501
  # noqa: E501, F841

# Session settings
API_SESSION_EXPIRY = getattr(settings, 'LEGACY_API_SESSION_EXPIRY', 3600 * 24 * 7)  # noqa: E501
  # noqa: E501, F841

# Cache settings for session storage
API_SESSION_CACHE_NAME = getattr(settings, 'LEGACY_API_SESSION_CACHE_NAME', 'default')  # noqa: E501
  # noqa: E501, F841
API_SESSION_CACHE_KEY_PREFIX = getattr(settings, 'LEGACY_API_SESSION_CACHE_KEY_PREFIX', 'legacy_api_session_')  # noqa: E501
  # noqa: E501, F841

# Logging settings
API_LOGGING_ENABLED = getattr(settings, 'LEGACY_API_LOGGING_ENABLED', True)
  # noqa: F841
API_LOGGING_LEVEL = getattr(settings, 'LEGACY_API_LOGGING_LEVEL', 'INFO')
  # noqa: F841

# Advanced settings
API_PAGINATION_ENABLED = getattr(settings, 'LEGACY_API_PAGINATION_ENABLED', True)  # noqa: E501
  # noqa: E501, F841
API_PAGINATION_SIZE = getattr(settings, 'LEGACY_API_PAGINATION_SIZE', 100)
  # noqa: F841
API_RESPONSE_FORMAT = getattr(settings, 'LEGACY_API_RESPONSE_FORMAT', 'json')
  # noqa: F841
