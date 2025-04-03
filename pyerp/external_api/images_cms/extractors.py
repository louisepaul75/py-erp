"""
Extractors for image data from the external CMS.
"""

from typing import Any, Dict, List, Optional

from pyerp.sync.extractors.base import BaseExtractor
from pyerp.utils.logging import get_logger
from .client import ImageAPIClient


logger = get_logger(__name__)


class ImageApiExtractor(BaseExtractor):
    """Extractor for image data from the external CMS API."""

    def __init__(self, config: Dict[str, Any]):
        """Initialize the extractor with configuration.
        
        Args:
            config: Dictionary containing configuration parameters
        """
        super().__init__(config)
        self.total_count = 0
        self.client = None

    def get_required_config_fields(self) -> List[str]:
        """Get required configuration fields.

        Returns:
            List of required field names
        """
        return []  # No required fields, using Django settings

    def connect(self) -> None:
        """Establish connection to image API.

        Raises:
            ConnectionError: If connection cannot be established
        """
        try:
            self.client = ImageAPIClient()
            self.connection = self.client  # For compatibility with BaseExtractor
            logger.info("Successfully connected to Image API")
        except Exception as e:
            error_msg = f"Failed to connect to Image API: {e}"
            logger.error(error_msg)
            raise ConnectionError(error_msg)

    def extract(
        self, query_params: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """Extract image data from the API.

        Args:
            query_params: Optional parameters for the query:
                - page: Page number to fetch (default: 1)
                - page_size: Number of results per page (default: 100)
                - product_id: Optional product ID to filter by

        Returns:
            List of dictionaries containing image data

        Raises:
            ConnectionError: If not connected to the API
            ValueError: If query parameters are invalid
        """
        if not self.connection:
            raise ConnectionError("Not connected to Image API")

        # Set default values and extract from query_params
        page = 1
        page_size = 100
        product_id = None

        if query_params:
            if 'page' in query_params:
                page = int(query_params['page'])
            if 'page_size' in query_params:
                page_size = int(query_params['page_size'])
            if 'product_id' in query_params:
                product_id = query_params['product_id']

        try:
            # If product_id is provided, use product-specific endpoint
            if product_id:
                logger.info(f"Extracting images for product ID: {product_id}")
                # Implement product-specific extraction if API supports it
                # For now, return an empty list
                return []
            else:
                # Get all files with pagination
                logger.info(f"Extracting images (page {page}, size {page_size})")
                response = self.connection.get_all_files(page=page, page_size=page_size)
                
                if not response:
                    logger.warning("No data returned from Image API")
                    return []
                
                # Extract results array
                results = response.get('results', [])
                
                # Store total count for pagination
                self.total_count = response.get('count', 0)
                
                # Log some statistics
                logger.info(f"Extracted {len(results)} images (total available: {self.total_count})")
                
                return results
        except Exception as e:
            error_msg = f"Error extracting data from Image API: {e}"
            logger.error(error_msg)
            raise ValueError(error_msg)
            
    def close(self) -> None:
        """Close connection to the API."""
        # No explicit close method needed for this client
        # But we implement it for compatibility with BaseExtractor
        self.connection = None
        self.client = None 