"""
Image API Client for external product image database.

This module provides a client for interacting with the
external image database APIlocated at webapp.zinnfiguren.de.
It handles authentication, connection management,
and parsing of API responses.
"""

import json
import logging
import requests
import urllib3
from urllib3.util import Retry
from requests.adapters import HTTPAdapter
from requests.auth import HTTPBasicAuth

from django.conf import settings
from django.core.cache import cache

from pyerp.business_modules.products.models import ParentProduct, Product
from .constants import (
    MIN_THUMBNAIL_RESOLUTION,
    MAX_THUMBNAIL_RESOLUTION,
    MIN_RESOLUTION_ARRAY_LENGTH,
    DEFAULT_TIMEOUT,
    DEFAULT_CACHE_TIMEOUT,
    DEFAULT_PAGE_SIZE,
    MAX_RETRIES,
    BACKOFF_FACTOR,
    RETRY_STATUS_CODES,
    HTTP_OK,
)
from .exceptions import (
    NoResponseError,
    InvalidResponseFormatError,
    MissingFieldsError,
)
from pyerp.external_api import connection_manager

logger = logging.getLogger(__name__)


class ImageAPIClient:
    """
    Client for interacting with the external image database API.

    This client handles:
    - Authentication with the API
    - Connection management (retries, timeouts)
    - Caching of API responses
    - Parsing API responses into a usable format
    - Retrieving product images by article number
    - Image prioritization based on format and type
    """

    def __init__(self):
        """Initialize the API client with settings from Django configuration."""
        self.base_url = settings.IMAGE_API_URL.rstrip("/") + "/"
        self.username = settings.IMAGE_API_USERNAME
        self.password = settings.IMAGE_API_PASSWORD
        self.timeout = getattr(settings, "IMAGE_API_TIMEOUT", 30)
        self.verify_ssl = getattr(settings, "IMAGE_API_VERIFY_SSL", True)

        # Set up session with retry strategy
        self.session = requests.Session()
        retry_strategy = Retry(
            total=3,
            backoff_factor=0.5,
            status_forcelist=[500, 502, 503, 504],
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
        self.session.auth = HTTPBasicAuth(self.username, self.password)

        if not self.verify_ssl:
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

        logger.debug(
            "ImageAPIClient initialized with username: %s",
            self.username
        )
        
    def check_connection(self) -> bool:
        """
        Check if the connection to the Images CMS API is working.
        
        This method is used by the health check system to verify 
        that the API is accessible and responding correctly.
        
        Returns:
            bool: True if connection is successful, False otherwise
            
        Raises:
            Exception: If an unexpected error occurs during validation
        """
        try:
            logger.info("Checking connection to Images CMS API")
            
            # First check if the connection is enabled
            if not connection_manager.is_connection_enabled("images_cms"):
                logger.info("Images CMS API connection is disabled")
                return False
            
            # Use a simple API endpoint to test connection
            endpoint = "all-files-and-articles/"
            params = {
                "page": 1,
                "page_size": 1
            }
            
            response = self.session.get(
                f"{self.base_url}{endpoint}",
                params=params,
                verify=self.verify_ssl,
                timeout=self.timeout
            )
            
            if response.status_code != HTTP_OK:
                logger.error(
                    "Connection check failed. Status: %d, Response: %s",
                    response.status_code,
                    response.text
                )
                return False
                
            # If we made it here, connection is working
            return True
            
        except Exception as e:
            logger.error(f"Connection check failed with exception: {e}")
            raise

    def get_all_files(self, page=1, page_size=DEFAULT_PAGE_SIZE):
        """
        Fetch all files from the API with pagination.

        Args:
            page (int): Page number to fetch (1-based)
            page_size (int): Number of records per page

        Returns:
            dict: API response containing 'count' and 'results' fields
        """
        endpoint = "all-files-and-articles/"
        params = {
            "page": page,
            "page_size": page_size
        }

        try:
            response = self.session.get(
                f"{self.base_url}{endpoint}",
                params=params,
                verify=self.verify_ssl,
                timeout=self.timeout
            )

            if response.status_code != HTTP_OK:
                logger.error(
                    "Failed to fetch files. Status: %d, Response: %s",
                    response.status_code,
                    response.text
                )
                return None

            data = response.json()
            if not isinstance(data, dict) or 'count' not in data:
                raise InvalidResponseFormatError(
                    "Response missing required fields"
                )

            return data

        except requests.exceptions.RequestException as e:
            logger.error("Request failed: %s", str(e))
            return None
        except json.JSONDecodeError as e:
            logger.error("Failed to parse JSON response: %s", str(e))
            return None
        except Exception as e:
            logger.error("Unexpected error: %s", str(e))
            return None 