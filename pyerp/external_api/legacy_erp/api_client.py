"""
Legacy API client for the legacy ERP system.

This module provides functionality for interacting with the legacy ERP system
using the API client from direct_api, adapted for the legacy_sync package.
"""

from django.conf import settings

from pyerp.external_api.legacy_erp.client import LegacyERPClient
from pyerp.external_api.legacy_erp.exceptions import LegacyERPError
from pyerp.utils.logging import get_logger

# Configure logging using the centralized logging system
logger = get_logger(__name__)

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

    def check_connection(self) -> bool:
        """
        Check if the connection to the legacy ERP API is working.

        This method is used by the health check system to verify
        that the API is accessible and responding correctly.

        Returns:
            bool: True if connection is successful, False otherwise

        Raises:
            LegacyERPError: If an unexpected error occurs during validation
        """
        try:
            logger.info("Checking API client connection to legacy ERP API")
            return self.client.check_connection()
        except Exception as e:
            logger.error(f"API client connection check failed: {e}")
            raise LegacyERPError(f"Failed to check API client connection: {e}")
