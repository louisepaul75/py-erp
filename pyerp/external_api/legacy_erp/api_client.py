"""
Legacy API client for the legacy ERP system.

This module provides functionality for interacting with the legacy ERP system
using the API client from direct_api, adapted for the legacy_sync package.
"""

import logging
from typing import Any, Dict, List, Optional

from django.conf import settings

from pyerp.external_api.legacy_erp.client import LegacyERPClient
from pyerp.external_api.legacy_erp.exceptions import (
    ConnectionError,
    DataError,
    LegacyERPError,
    ResponseError,
    ServerUnavailableError,
)

# Configure logging
logger = logging.getLogger(__name__)

# Default API environment
DEFAULT_ENVIRONMENT = getattr(settings, "LEGACY_API_DEFAULT_ENVIRONMENT", "live")


class APIClient:
    """
    API client for the legacy ERP system.
    
    This class acts as a bridge between the legacy_sync functionality and
    the new LegacyERPClient implementation, providing compatibility with
    existing code that uses legacy_sync.api_client.
    """

    def __init__(self, environment: str = DEFAULT_ENVIRONMENT):
        """
        Initialize a new API client.

        Args:
            environment: The API environment to use ('live', 'test', etc.)
        """
        self.client = LegacyERPClient(environment=environment)
        self.environment = environment
        logger.debug("Initialized APIClient with environment: %s", environment) 