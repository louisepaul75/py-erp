"""Customer data extractor from legacy ERP system."""

import logging
from typing import Any, Dict, List, Optional

from pyerp.external_api.legacy_erp.scripts.simple_client import SimpleAPIClient
from .base import BaseExtractor


logger = logging.getLogger(__name__)


class CustomerExtractor(BaseExtractor):
    """Extracts customer data from the legacy Kunden table."""

    def get_required_config_fields(self) -> List[str]:
        """Get required configuration fields.
        
        Returns:
            List of required field names
        """
        return ["environment"]

    def connect(self) -> None:
        """Establish connection to legacy ERP API.
        
        Raises:
            ConnectionError: If connection cannot be established
        """
        try:
            self.connection = SimpleAPIClient(
                environment=self.config["environment"]
            )
            logger.info(
                f"Connected to legacy API ({self.config['environment']})"
            )
        except Exception as e:
            raise ConnectionError(f"Failed to connect to legacy API: {e}")

    def extract(
        self, query_params: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """Extract customer data from legacy system.
        
        Args:
            query_params: Optional parameters for filtering/pagination
                - modified_since: datetime to filter by modification date
                - limit: Maximum number of records to return
                - offset: Number of records to skip
        
        Returns:
            List of dictionaries containing customer data
        
        Raises:
            RuntimeError: If extraction fails
        """
        try:
            # Set up query parameters
            top = query_params.get("limit", 100) if query_params else 100
            skip = query_params.get("offset", 0) if query_params else 0
            filter_query = None

            # Add modified_since filter if provided
            if query_params and query_params.get("modified_since"):
                modified_since = query_params["modified_since"]
                filter_query = f"modified_date >= '{modified_since}'"

            # Fetch data from legacy API
            df = self.connection.fetch_table(
                "Kunden",
                top=top,
                skip=skip,
                filter_query=filter_query,
            )

            # Convert DataFrame to list of dictionaries
            records = df.to_dict("records") if not df.empty else []
            
            logger.info(
                f"Extracted {len(records)} customer records from legacy system"
            )
            return records

        except Exception as e:
            logger.error(f"Failed to extract customer data: {e}")
            raise RuntimeError(f"Customer data extraction failed: {e}")

    def close(self) -> None:
        """Close the connection to the legacy system."""
        self.connection = None 