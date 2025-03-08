"""
Main API client for interacting with the legacy 4D-based ERP system.

This module provides the LegacyERPClient class which handles all interactions
with the legacy API, including data retrieval and updates.
"""

import json
import logging
import os
import socket
import time
from typing import Any
from urllib.parse import urljoin

import pandas as pd
import requests

from pyerp.external_api.legacy_erp.auth import (
    get_session,
    invalidate_session,
    is_session_limit_reached,
    set_session_limit_reached,
)
from pyerp.external_api.legacy_erp.exceptions import (
    ConnectionError,
    DataError,
    LegacyERPError,
    ResponseError,
    ServerUnavailableError,
)
from pyerp.external_api.legacy_erp.settings import (
    API_ENVIRONMENTS,
    API_MAX_RETRIES,
    API_PAGINATION_ENABLED,
    API_REQUEST_TIMEOUT,
    API_REST_ENDPOINT,
    API_RETRY_BACKOFF_FACTOR,
)

# Configure logging
logger = logging.getLogger(__name__)


class LegacyERPClient:
    """
    Client for directly interacting with the legacy 4D-based ERP system.

    This class provides methods for fetching data from and pushing data to
    the legacy system, handling authentication and error handling.
    """

    def __init__(self, environment: str = "live", timeout: int = None):
        """
        Initialize a new client instance.

        Args:
            environment: Which API environment to use ('live', 'test', etc.)
            timeout: Optional custom timeout for API requests (in seconds)
        """
        self.environment = environment
        self.timeout = timeout or API_REQUEST_TIMEOUT
        logger.debug(
            "Initialized LegacyERPClient for environment: %s", environment
        ) 