"""Legacy API data extractor implementation."""

import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

from pyerp.external_api.legacy_erp.simple_client import SimpleAPIClient
from .base import BaseExtractor


logger = logging.getLogger(__name__)


class LegacyAPIExtractor(BaseExtractor):
    """Extractor for legacy 4D API data source."""

    def get_required_config_fields(self) -> List[str]:
        """Get required configuration fields.
        
        Returns:
            List of required field names
        """
        return ['environment', 'table_name']

    def connect(self) -> None:
        """Establish connection to legacy API.
        
        Raises:
            ConnectionError: If connection cannot be established
        """
        try:
            self.connection = SimpleAPIClient(
                environment=self.config['environment']
            )
            logger.info(
                f"Connected to legacy API ({self.config['environment']})"
            )
        except Exception as e:
            raise ConnectionError(
                f"Failed to connect to legacy API: {e}"
            ) from e

    def extract(
        self, query_params: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """Extract data from legacy API.
        
        Args:
            query_params: Optional parameters to filter data
                Supports modified_date filtering with operators:
                - gt: Greater than (date)
                - gte: Greater than or equal (date)
                - lt: Less than (date)
                - lte: Less than or equal (date)
            
        Returns:
            List of extracted records
            
        Raises:
            ConnectionError: If not connected to API
            ValueError: If query parameters are invalid
        """
        if not self.connection:
            raise ConnectionError("Not connected to legacy API")

        try:
            # Initialize filter query
            filter_query = None
            
            # Process query parameters for date filtering
            if query_params and 'modified_date' in query_params:
                filter_query = self._build_date_filter_query(query_params)
                logger.info(f"Using date filter query: {filter_query}")

            # Extract data with pagination
            all_records = []
            page_size = self.config.get('page_size', 100)
            
            logger.info(f"Fetching data from {self.config['table_name']} with page size {page_size}")
            
            # First try with a small request to test connection
            total_pages = 1  # Start with at least one page
            
            for page in range(total_pages):
                # Calculate current skip
                skip = page * page_size
                
                # Fetch page of records
                logger.info(f"Fetching page {page+1} (skip={skip}, top={page_size})")
                
                records_df = self.connection.fetch_table(
                    table_name=self.config['table_name'],
                    top=page_size,
                    skip=skip,
                    filter_query=filter_query,
                    all_records=False
                )
                
                # Convert DataFrame to list of dictionaries
                if not records_df.empty:
                    page_records = records_df.to_dict('records')
                    record_count = len(page_records)
                    all_records.extend(page_records)
                    logger.info(f"Fetched {record_count} records on page {page+1}")
                    
                    # If we got a full page, we might need another page
                    if record_count == page_size and page == total_pages - 1:
                        total_pages += 1
                else:
                    logger.info(f"No records returned on page {page+1}")
                    break

            logger.info(
                f"Extracted {len(all_records)} records from "
                f"{self.config['table_name']}"
            )
                
            return all_records

        except Exception as e:
            raise ValueError(
                f"Failed to extract data from legacy API: {e}"
            ) from e
            
    def _build_date_filter_query(self, query_params: Dict[str, Any]) -> str:
        """Build a date filter query string for the legacy API.
        
        Args:
            query_params: Query parameters with date filters
            
        Returns:
            OData filter query string
        """
        modified_date = query_params.get('modified_date')
        if not modified_date:
            return None
            
        # Get the field name from config or use default
        date_field = self.config.get('modified_date_field', 'modified_date')
        
        # Handle various filter formats
        if isinstance(modified_date, dict):
            # Process operators: gt, gte, lt, lte
            date_conditions = []
            
            # Greater than
            if 'gt' in modified_date:
                date_str = self._format_date_for_api(modified_date['gt'])
                date_conditions.append(f"{date_field} gt '{date_str}'")
                
            # Greater than or equal
            if 'gte' in modified_date:
                date_str = self._format_date_for_api(modified_date['gte'])
                date_conditions.append(f"{date_field} ge '{date_str}'")
                
            # Less than
            if 'lt' in modified_date:
                date_str = self._format_date_for_api(modified_date['lt'])
                date_conditions.append(f"{date_field} lt '{date_str}'")
                
            # Less than or equal
            if 'lte' in modified_date:
                date_str = self._format_date_for_api(modified_date['lte'])
                date_conditions.append(f"{date_field} le '{date_str}'")
                
            if date_conditions:
                # Combine conditions with OData 'and'
                return ' and '.join(date_conditions)
            return None
        
        # Handle direct value (equality)
        elif isinstance(modified_date, str):
            date_str = self._format_date_for_api(modified_date)
            return f"{date_field} eq '{date_str}'"
            
        return None
    
    def _format_date_for_api(self, date_str: str) -> str:
        """Format a date string for the legacy API.
        
        Args:
            date_str: ISO format date string
            
        Returns:
            Formatted date string compatible with legacy API
        """
        try:
            # Parse ISO format date
            if isinstance(date_str, str):
                dt = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
            else:
                dt = date_str
                
            # Format for legacy API (check config for format or use ISO format)
            date_format = self.config.get('date_format', '%Y-%m-%dT%H:%M:%S')
            return dt.strftime(date_format)
            
        except Exception as e:
            logger.warning(f"Error formatting date: {str(e)}")
            return date_str  # Return original if parsing fails 