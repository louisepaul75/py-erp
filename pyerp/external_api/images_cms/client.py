"""
Image API Client for external product image database.

This module provides a client for interacting with the external image database API
located at webapp.zinnfiguren.de. It handles authentication, connection management,
and parsing of API responses.
"""

import hashlib
import json
import logging
from typing import Any

import requests
import urllib3
from django.conf import settings
from django.core.cache import cache
from requests.adapters import HTTPAdapter
from requests.auth import HTTPBasicAuth
from urllib3.util.retry import Retry

from pyerp.products.models import ParentProduct, Product
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

    def __init__(self) -> None:
        """Initialize the client with settings from Django configuration."""
        # Get the base URL from settings, with a fallback
        self.base_url = settings.IMAGE_API.get(
            "BASE_URL",
            "http://webapp.zinnfiguren.de/api/",
        )

        # Log the base URL for debugging
        logger.debug("Initializing ImageAPIClient with base URL: %s", self.base_url)

        self.username = settings.IMAGE_API.get("USERNAME")
        self.password = settings.IMAGE_API.get("PASSWORD")
        self.timeout = settings.IMAGE_API.get(
            "TIMEOUT",
            DEFAULT_TIMEOUT,
        )
        self.cache_enabled = settings.IMAGE_API.get("CACHE_ENABLED", True)
        self.cache_timeout = settings.IMAGE_API.get(
            "CACHE_TIMEOUT",
            DEFAULT_CACHE_TIMEOUT,
        )
        self.verify_ssl = settings.IMAGE_API.get(
            "VERIFY_SSL",
            False,
        )

        # Ensure the base URL ends with a slash
        if not self.base_url.endswith("/"):
            self.base_url += "/"
            logger.debug("Added trailing slash to base URL: %s", self.base_url)

        # Set up retry strategy
        retry_strategy = Retry(
            total=MAX_RETRIES,
            backoff_factor=BACKOFF_FACTOR,
            status_forcelist=RETRY_STATUS_CODES,
        )

        # Create a session with the retry strategy
        self.session = requests.Session()
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
        self.session.auth = HTTPBasicAuth(self.username, self.password)

        # Disable SSL verification warnings if verify_ssl is False
        if not self.verify_ssl:
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

        logger.debug("ImageAPIClient initialized with username: %s", self.username) 