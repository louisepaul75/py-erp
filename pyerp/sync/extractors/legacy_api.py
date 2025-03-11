"""Legacy API data extractor implementation."""

import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

from pyerp.external_api.legacy_erp import LegacyERPClient
from .base import BaseExtractor
import pandas as pd


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
            self.connection = LegacyERPClient(
                environment=self.config['environment']
            )
            logger.info(
                f"Connected to legacy API ({self.config['environment']})"
            )
        except Exception as e:
            raise ConnectionError(
                f"Failed to connect to legacy API: {e}"
            )

    def extract(
        self, query_params: Optional[Dict[str, Any]] = None,
        fail_on_filter_error: bool = False
    ) -> List[Dict[str, Any]]:
        """Extract data from legacy API.
        
        Args:
            query_params: Query parameters for filtering data
            fail_on_filter_error: Whether to fail if filter doesn't work
            
        Returns:
            List of extracted records
            
        Raises:
            ConnectionError: If not connected to API
            ValueError: If query parameters are invalid
            RuntimeError: If filter doesn't work and fail_on_filter_error is True
        """
        if not self.connection:
            raise ConnectionError("Not connected to legacy API")

        try:
            # Initialize filter query
            filter_query = None
            filter_requested = False
            
            # Process query parameters for date filtering
            if query_params and 'modified_date' in query_params:
                filter_query = self._build_date_filter_query(query_params)
                filter_requested = True
                logger.info(f"Using date filter query: {filter_query}")
                logger.info(f"Query params: {query_params}")
                logger.info(
                    f"Modified date value: {query_params.get('modified_date')}"
                )
                if isinstance(query_params.get('modified_date'), dict):
                    for op, val in query_params.get('modified_date').items():
                        logger.info(f"  - {op}: {val}")
                
                # Add more detailed logging
                logger.info(f"DETAILED FILTER QUERY: {filter_query}")
                logger.info(f"FILTER FORMAT FROM CONFIG: {self.config.get('timestamp_filter_format')}")
                logger.info(f"TIMESTAMP FIELD FROM CONFIG: {self.config.get('modified_date_field', 'modified_date')}")

            # Extract data with pagination
            all_records = []
            page_size = self.config.get('page_size', 100)
            all_records_enabled = self.config.get('all_records', False)
            
            logger.info(
                f"Fetching data from {self.config['table_name']} "
                f"with page size {page_size}"
            )
            
            # First try with a small request to test connection
            total_pages = 1
            
            for page in range(total_pages):
                # Calculate current skip
                skip = page * page_size
                
                # Fetch page of records
                logger.info(
                    f"Fetching page {page+1} (skip={skip}, top={page_size})"
                )
                logger.info(f"Final filter query: {filter_query}")
                
                try:
                    records_df = self.connection.fetch_table(
                        table_name=self.config['table_name'],
                        top=page_size,
                        skip=skip,
                        filter_query=filter_query,
                        all_records=all_records_enabled,
                        fail_on_filter_error=fail_on_filter_error
                    )
                    
                    # Check if we got too many records when a filter was requested
                    if (filter_requested and fail_on_filter_error and 
                            len(records_df) >= page_size and page == 0):
                        # This might indicate the filter wasn't applied
                        # Let's check if the records match our filter criteria
                        if 'modified_date' in query_params:
                            # Get the date field from config
                            date_field = self.config.get('modified_date_field', 'modified_date')
                            if date_field in records_df.columns:
                                # Check if any records don't match our filter
                                if isinstance(query_params['modified_date'], dict):
                                    for op, val in query_params['modified_date'].items():
                                        date_val = datetime.fromisoformat(val.replace('Z', '+00:00'))
                                        if op == 'gt':
                                            # Convert string dates to datetime objects for comparison
                                            try:
                                                # Check if the column contains string dates
                                                if records_df[date_field].dtype == 'object':
                                                    # Try to convert to datetime
                                                    date_series = pd.to_datetime(
                                                        records_df[date_field], 
                                                        errors='coerce'
                                                    )
                                                    # Check for any records that don't match our filter
                                                    invalid_records = date_series <= date_val
                                                    if invalid_records.any():
                                                        raise RuntimeError(
                                                            f"Filter not applied correctly. Found records older than {val}"
                                                        )
                                            except Exception as e:
                                                logger.warning(
                                                    f"Could not validate date filter: {e}"
                                                )
                                        elif op == 'gte':
                                            # Convert string dates to datetime objects for comparison
                                            try:
                                                # Check if the column contains string dates
                                                if records_df[date_field].dtype == 'object':
                                                    # Try to convert to datetime
                                                    date_series = pd.to_datetime(
                                                        records_df[date_field], 
                                                        errors='coerce'
                                                    )
                                                    # Check for any records that don't match our filter
                                                    invalid_records = date_series < date_val
                                                    if invalid_records.any():
                                                        raise RuntimeError(
                                                            f"Filter not applied correctly. Found records older than {val}"
                                                        )
                                            except Exception as e:
                                                logger.warning(
                                                    f"Could not validate date filter: {e}"
                                                )
                                        elif op == 'lt':
                                            # Convert string dates to datetime objects for comparison
                                            try:
                                                # Check if the column contains string dates
                                                if records_df[date_field].dtype == 'object':
                                                    # Try to convert to datetime
                                                    date_series = pd.to_datetime(
                                                        records_df[date_field], 
                                                        errors='coerce'
                                                    )
                                                    # Check for any records that don't match our filter
                                                    invalid_records = date_series >= date_val
                                                    if invalid_records.any():
                                                        raise RuntimeError(
                                                            f"Filter not applied correctly. Found records newer than {val}"
                                                        )
                                            except Exception as e:
                                                logger.warning(
                                                    f"Could not validate date filter: {e}"
                                                )
                                        elif op == 'lte':
                                            # Convert string dates to datetime objects for comparison
                                            try:
                                                # Check if the column contains string dates
                                                if records_df[date_field].dtype == 'object':
                                                    # Try to convert to datetime
                                                    date_series = pd.to_datetime(
                                                        records_df[date_field], 
                                                        errors='coerce'
                                                    )
                                                    # Check for any records that don't match our filter
                                                    invalid_records = date_series > date_val
                                                    if invalid_records.any():
                                                        raise RuntimeError(
                                                            f"Filter not applied correctly. Found records newer than {val}"
                                                        )
                                            except Exception as e:
                                                logger.warning(
                                                    f"Could not validate date filter: {e}"
                                                )
                except Exception as e:
                    logger.error(f"Error fetching records: {e}")
                    # If we're supposed to fail on filter errors and a filter was requested,
                    # don't silently fall back to getting all records
                    if filter_requested and fail_on_filter_error:
                        raise RuntimeError(
                            f"Filter error: {e}. The command was configured to fail on filter errors."
                        )
                    raise
                
                # Convert DataFrame to list of dictionaries
                if not records_df.empty:
                    page_records = records_df.to_dict('records')
                    record_count = len(page_records)
                    
                    all_records.extend(page_records)
                    logger.info(
                        f"Fetched {record_count} records on page {page+1}"
                    )
                    
                    # If we got a full page and all_records is not enabled,
                    # we might need another page
                    if (not all_records_enabled and record_count == page_size
                            and page == total_pages - 1):
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
        
        for filter in modified_date.keys():
            try:
                modified_date[filter] = modified_date[filter].strftime("%Y-%m-%d")
            except:
                pass

        # Get the field name from config or use default
        date_field = self.config.get('modified_date_field', 'modified_date')
        logger.info(f"Date field from config: {date_field}")
        

        print(f"Modified date: {modified_date}")
        

        # Handle various filter formats
        if isinstance(modified_date, dict):
            # Process operators: gt, gte, lt, lte
            date_conditions = []
            
            # Greater than
            if 'gt' in modified_date:
                date_str = self._format_date_for_api(modified_date['gt'])
                logger.info(f"Formatted date for 'gt': {date_str}")
                
                # Use the exact format that works with the legacy API
                filter_str = f"&$filter='{date_field} > '{date_str}''"
                logger.info(f"Constructed filter string for 'gt': {filter_str}")
                date_conditions.append(filter_str)
                print(filter_str)
                
                
            # Greater than or equal
            if 'gte' in modified_date:
                date_str = self._format_date_for_api(modified_date['gte'])
                logger.info(f"Formatted date for 'gte': {date_str}")
                
                # Use the exact format that works with the legacy API
                filter_str = f"&$filter='{date_field} >= '{date_str}''"
                logger.info(f"Constructed filter string for 'gte': {filter_str}")
                date_conditions.append(filter_str)
                
            # Less than
            if 'lt' in modified_date:
                date_str = self._format_date_for_api(modified_date['lt'])
                logger.info(f"Formatted date for 'lt': {date_str}")
                
                # Use the exact format that works with the legacy API
                filter_str = f"&$filter='{date_field} < '{date_str}''"
                logger.info(f"Constructed filter string for 'lt': {filter_str}")
                date_conditions.append(filter_str)
                
            # Less than or equal
            if 'lte' in modified_date:
                date_str = self._format_date_for_api(modified_date['lte'])
                logger.info(f"Formatted date for 'lte': {date_str}")
                
                # Use the exact format that works with the legacy API
                filter_str = f"&$filter='{date_field} <= '{date_str}''"
                logger.info(f"Constructed filter string for 'lte': {filter_str}")
                date_conditions.append(filter_str)
                
            if date_conditions:
                # Return first condition (we don't support multiple conditions yet)
                return date_conditions[0]
            return None
        
        # Handle direct value (equality)
        elif isinstance(modified_date, str):
            date_str = self._format_date_for_api(modified_date)
            logger.info(f"Formatted date for equality: {date_str}")
            
            # Use the exact format that works with the legacy API
            filter_str = f"&$filter='{date_field} = '{date_str}''"
            logger.info(f"Constructed filter string for equality: {filter_str}")
            return filter_str
            
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
            # date_format = self.config.get('date_format', '%Y-%m-%d')
            return dt.strftime('%Y-%m-%d')
            
        except Exception as e:
            logger.warning(f"Error formatting date: {str(e)}")
            return date_str  # Return original if parsing fails 