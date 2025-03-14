"""Legacy API data extractor implementation."""

from datetime import datetime
from typing import Any, Dict, List

from pyerp.external_api.legacy_erp import LegacyERPClient
from pyerp.utils.logging import get_logger, log_data_sync_event
from pyerp.sync.exceptions import ExtractError

from .base import BaseExtractor


logger = get_logger(__name__)


class LegacyAPIExtractor(BaseExtractor):
    """Extractor for legacy API data."""

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
            log_data_sync_event(
                source=f"legacy_api_{self.config['environment']}",
                destination="pyerp",
                record_count=0,
                status="connected",
                details={"table": self.config['table_name']}
            )
        except ConnectionError as e:
            raise ConnectionError(
                f"Failed to connect to legacy API: {e}"
            )

    def extract(
        self,
        query_params: Dict[str, Any] = None,
        fail_on_filter_error: bool = False
    ) -> List[Dict[str, Any]]:
        """Extract data from the legacy API.
        
        Args:
            query_params: Query parameters for filtering data
            fail_on_filter_error: Whether to raise an error if filter 
                construction fails
            
        Returns:
            List of dictionaries containing the extracted data
            
        Raises:
            ExtractError: If data extraction fails or if filter construction 
                fails and fail_on_filter_error is True
        """
        # Initialize filter parts list
        filter_parts = []
        filter_query = None
        
        try:
            # Handle SKU filter
            if query_params and "Nummer" in query_params:
                filter_parts.append(
                    f"Nummer eq '{query_params['Nummer']}'"
                )
                
            # Handle date filter
            if query_params and "modified_date" in query_params:
                if "gt" in query_params["modified_date"]:
                    date_val = query_params["modified_date"]["gt"]
                    filter_parts.append(
                        f"modified_date gt datetime'{date_val}'"
                    )
            
            # Combine all filter parts with 'and'
            if filter_parts:
                filter_query = " and ".join(filter_parts)
                
        except (ValueError, KeyError) as e:
            error_msg = f"Error constructing filter query: {e}"
            logger.error(error_msg)
            if fail_on_filter_error:
                raise ExtractError(error_msg)
        
        try:
            # Get client from connection manager
            client = self.connection
            
            # Get page size from config or use default
            page_size = self.config.get("page_size", 1000)
            all_records = self.config.get("all_records", False)
            
            # Initialize variables for pagination
            skip = 0
            all_records_list = []
            
            while True:
                # Fetch data using the constructed filter
                df = client.fetch_table(
                    table_name=self.config["table_name"],
                    filter_query=filter_query,
                    top=page_size,
                    skip=skip,
                    all_records=all_records,
                )
                
                if df is None or df.empty:
                    break
                    
                # Convert DataFrame to list of dictionaries and append
                records = df.to_dict(orient="records")
                all_records_list.extend(records)
                
                # Log progress
                logger.info(
                    f"Fetched {len(records)} records (total: {len(all_records_list)})"
                )
                
                # If we got fewer records than page_size, we've reached the end
                if len(records) < page_size:
                    break
                    
                # Increment skip for next page
                skip += page_size
                
            record_count = len(all_records_list)
            logger.info(
                f"Extracted {record_count} total records from legacy API"
            )
            
            return all_records_list
            
        except (ConnectionError, ValueError) as e:
            error_msg = (
                f"Error extracting data from legacy API: {e}"
            )
            logger.error(error_msg)
            raise ExtractError(error_msg)
            
    def _build_date_filter_query(self, query_params: Dict[str, Any]) -> str:
        """Build OData filter query for date filtering."""
        modified_date = query_params.get('modified_date')
        if not modified_date:
            return None
        
        # Get the field name from config or use default
        date_field = self.config.get('modified_date_field', 'modified_date')
        logger.info(f"Date field from config: {date_field}")
        
        # Convert date values to proper format if needed
        for filter_op in modified_date.keys():
            try:
                if hasattr(modified_date[filter_op], 'strftime'):
                    # It's already a datetime object, no need to convert
                    pass
            except:
                pass

        print(f"Modified date: {modified_date}")
        
        # Create filter conditions in the new format: [[field, operator, value], ...]
        filter_conditions = []
        
        # Handle various filter formats
        if isinstance(modified_date, dict):
            # Process operators: gt, gte, lt, lte
            
            # Greater than
            if 'gt' in modified_date:
                date_val = modified_date['gt']
                logger.info(
                    f"Adding 'gt' filter condition: {date_field} > {date_val}"
                )
                filter_conditions.append([date_field, ">", date_val])
                
            # Greater than or equal
            if 'gte' in modified_date:
                date_val = modified_date['gte']
                logger.info(
                    f"Adding 'gte' filter condition: {date_field} >= {date_val}"
                )
                filter_conditions.append([date_field, ">=", date_val])
                
            # Less than
            if 'lt' in modified_date:
                date_val = modified_date['lt']
                logger.info(
                    f"Adding 'lt' filter condition: {date_field} < {date_val}"
                )
                filter_conditions.append([date_field, "<", date_val])
                
            # Less than or equal
            if 'lte' in modified_date:
                date_val = modified_date['lte']
                logger.info(
                    f"Adding 'lte' filter condition: {date_field} <= {date_val}"
                )
                filter_conditions.append([date_field, "<=", date_val])
                
            if filter_conditions:
                logger.info(f"Created filter conditions: {filter_conditions}")
                return filter_conditions
            return None
        
        # Handle direct value (equality)
        elif isinstance(modified_date, str):
            date_val = modified_date
            logger.info(
                f"Adding equality filter condition: {date_field} = {date_val}"
            )
            return [[date_field, "=", date_val]]
            
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