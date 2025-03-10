"""Address data extractor from legacy ERP system."""

import logging
from typing import Any, Dict, List, Optional

from pyerp.external_api.legacy_erp.simple_client import SimpleAPIClient
from .base import BaseExtractor


logger = logging.getLogger(__name__)


class AddressExtractor(BaseExtractor):
    """Extracts address data from the legacy Adressen table."""

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
        """Extract address data from legacy system.
        
        Args:
            query_params: Optional parameters for filtering/pagination
                - modified_since: datetime to filter by modification date
                - limit: Maximum number of records to return
                - offset: Number of records to skip
                - address_numbers: List of AdrNr values to fetch
        
        Returns:
            List of dictionaries containing address data
        
        Raises:
            RuntimeError: If extraction fails
        """
        try:
            # Set up query parameters
            top = query_params.get("limit", 100) if query_params else 100
            skip = query_params.get("offset", 0) if query_params else 0
            filter_parts = []

            # Add modified_since filter if provided
            if query_params and query_params.get("modified_since"):
                modified_since = query_params["modified_since"]
                filter_parts.append(f"modified_date >= '{modified_since}'")

            # Add address numbers filter if provided
            if query_params and query_params.get("address_numbers"):
                numbers = query_params["address_numbers"]
                numbers_str = ", ".join(f"'{n}'" for n in numbers)
                filter_parts.append(f"AdrNr IN ({numbers_str})")

            # Combine filter parts
            filter_query = " AND ".join(filter_parts) if filter_parts else None

            # Fetch data from legacy API
            df = self.connection.fetch_table(
                "Adressen",
                top=top,
                skip=skip,
                filter_query=filter_query,
            )

            # Convert DataFrame to list of dictionaries
            records = df.to_dict("records") if not df.empty else []
            
            logger.info(
                f"Extracted {len(records)} address records from legacy system"
            )
            return records

        except Exception as e:
            logger.error(f"Failed to extract address data: {e}")
            raise RuntimeError(f"Address data extraction failed: {e}")

    def close(self) -> None:
        """Close the connection to the legacy system."""
        self.connection = None 