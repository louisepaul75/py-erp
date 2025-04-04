"""Legacy API data extractor implementation."""

import os
from datetime import datetime
from typing import Any, Dict, List
import hashlib
import json

from pyerp.external_api.legacy_erp import LegacyERPClient
from pyerp.utils.logging import get_logger, log_data_sync_event
from pyerp.sync.exceptions import ExtractError

from .base import BaseExtractor


logger = get_logger(__name__)

# Add a response cache to the LegacyAPIExtractor class
_response_cache = {}


class LegacyAPIExtractor(BaseExtractor):
    """Extractor for legacy API data."""

    # Class level cache to store API responses between instances
    _response_cache = {}

    def __init__(self, config):
        """Initialize with configuration.

        Args:
            config: Configuration dictionary
        """
        super().__init__(config)

    def get_required_config_fields(self) -> List[str]:
        """Get required configuration fields.

        Returns:
            List of required field names
        """
        return ["environment", "table_name"]

    def _validate_config(self) -> None:
        """Validate the extractor configuration, checking environment variables as fallback.

        Overrides the base class method to also check environment variables.

        Raises:
            ValueError: If required configuration is missing
        """
        # First check for environment variables and add them to config if available
        if "environment" not in self.config:
            env_value = os.environ.get("LEGACY_ERP_ENVIRONMENT")
            if env_value:
                logger.info(f"Using environment variable LEGACY_ERP_ENVIRONMENT: {env_value}")
                self.config["environment"] = env_value

        if "table_name" not in self.config:
            env_value = os.environ.get("LEGACY_ERP_TABLE_NAME")
            if env_value:
                logger.info(f"Using environment variable LEGACY_ERP_TABLE_NAME: {env_value}")
                self.config["table_name"] = env_value

        # Now proceed with normal validation
        required_fields = self.get_required_config_fields()
        missing = [field for field in required_fields if field not in self.config]
        if missing:
            raise ValueError(
                f"Missing required configuration fields: {', '.join(missing)}"
            )

    def connect(self) -> None:
        """Establish connection to legacy API.

        Raises:
            ConnectionError: If connection cannot be established
        """
        try:
            self.connection = LegacyERPClient(environment=self.config["environment"])
            log_data_sync_event(
                source=f"legacy_api_{self.config['environment']}",
                destination="pyerp",
                record_count=0,
                status="connected",
                details={"table": self.config["table_name"]},
            )
        except ConnectionError as e:
            raise ConnectionError(f"Failed to connect to legacy API: {e}")

    def extract(self, query_params=None, fail_on_filter_error=False):
        """Extract data from the API.

        Args:
            query_params: Additional query parameters
            fail_on_filter_error: Whether to fail if filter doesn't work

        Returns:
            List of records from the API
        """
        # Initialize client if needed
        client = self.connection
        
        # Check if we need to limit results
        top_limit = None
        if query_params and "$top" in query_params:
            top_limit = int(query_params["$top"])
            logger.info(f"Will limit results to top {top_limit} records")
        
        # Handle parent record IDs filtering if provided
        parent_filter = None
        if query_params and "parent_record_ids" in query_params:
            parent_ids = query_params["parent_record_ids"]
            logger.info(f"Filtering by parent record IDs: {len(parent_ids)} IDs provided")
            # Default parent field is AbsNr, but can be overridden
            parent_field = query_params.get("parent_field", "AbsNr")
            
            # Build filter query for parent IDs
            if len(parent_ids) == 1:
                # Simple case - just one parent ID
                parent_filter = [[parent_field, "=", parent_ids[0]]]
            else:
                # We need a complex filter for multiple parent IDs
                # The OData filter syntax would be "(Field eq value1 or Field eq value2 or ...)"
                # We'll build this as [[field, op, value], ...] format for the client
                parent_filter = []
                for parent_id in parent_ids:
                    parent_filter.append([parent_field, "=", parent_id])
            
            logger.info(f"Created parent filter with {len(parent_filter)} conditions")
        
        # Generate a cache key based on table name and query params
        cache_key = self._generate_cache_key(query_params)
        
        # Check if we have cached data for this query
        if cache_key in self.__class__._response_cache:
            data = self.__class__._response_cache[cache_key]
            logger.info(f"Using cached data for {self.config['table_name']} (cache key: {cache_key[:50]}...)")
            
            # Ensure we return a list of records
            if hasattr(data, 'to_dict') and callable(data.to_dict):
                # Convert DataFrame to list of dictionaries
                try:
                    result = data.to_dict(orient="records")
                except Exception as e:
                    logger.error(f"Error converting DataFrame to records: {e}")
                    # Try another way
                    try:
                        result = data.to_dict('records')
                    except:
                        # Last resort - manual conversion
                        result = []
                        for i in range(len(data)):
                            result.append(dict(data.iloc[i]))
            else:
                # Already a list
                result = data
            
            # Apply top limit if specified
            if top_limit and isinstance(result, list):
                logger.info(f"Limiting cached results to top {top_limit} records (from {len(result)} total)")
                return result[:int(top_limit)]
            
            return result
        
        # Execute query and fetch data
        try:
            # Only extract if we don't have cached data
            table_name = self.config["table_name"]
            logger.info(f"Extracting data from {table_name} (cache miss)")
            
            # Handle query params - convert to format expected by client
            if query_params:
                # Handle $top parameter for limiting results
                top = None
                all_records = self.config.get("all_records", True)
                filter_query = None
                
                if "$top" in query_params:
                    top = query_params["$top"]
                    logger.info(f"Using top limit: {top} - disabling pagination")
                    # Disable pagination in the client when top is specified
                    all_records = False
                
                # Get filter query if provided
                if "filter_query" in query_params:
                    filter_query = query_params["filter_query"]
                
                # Apply parent filter if we have one 
                if parent_filter:
                    if filter_query:
                        # If we already have a filter, combine with parent filter
                        logger.info("Combining existing filter with parent record filter")
                        # This assumes filter_query is a list of filter conditions
                        if isinstance(filter_query, list):
                            filter_query.extend(parent_filter)
                        else:
                            filter_query = parent_filter
                    else:
                        filter_query = parent_filter
                
                # Execute the fetch with modified parameters
                records = client.fetch_table(
                    table_name=table_name,
                    all_records=all_records,
                    filter_query=filter_query,
                    top=top
                )
            else:
                # No query params, simple fetch
                records = client.fetch_table(
                    table_name=table_name,
                    all_records=self.config.get("all_records", True),
                )
            
            # Ensure we have a list of dictionaries before caching
            if hasattr(records, 'to_dict') and callable(records.to_dict):
                try:
                    result = records.to_dict(orient="records")
                    logger.info(f"Converted DataFrame to {len(result)} dictionary records")
                    
                    # Store in cache for future use
                    self.__class__._response_cache[cache_key] = result
                    logger.info(f"Cached {len(result)} records for {table_name}")
                    return result
                except Exception as e:
                    logger.error(f"Error converting DataFrame: {e}")
                    # Store the original format in the cache
                    self.__class__._response_cache[cache_key] = records
                    logger.warning("Stored original DataFrame format in cache")
                    return records
            
            # Store in cache for future use
            self.__class__._response_cache[cache_key] = records
            logger.info(f"Fetched {len(records)} records (total: {len(records)})")
            return records
        except Exception as e:
            logger.error(f"Error extracting data from {self.config['table_name']}: {e}")
            if fail_on_filter_error:
                raise
            return []

    def _build_date_filter_query(self, query_params: Dict[str, Any]) -> str:
        """Build OData filter query for date filtering."""
        modified_date = query_params.get("modified_date")
        if not modified_date:
            return None

        # Get the field name from config or use default
        date_field = self.config.get("modified_date_field", "modified_date")
        logger.info(f"Date field from config: {date_field}")

        # Convert date values to proper format if needed
        for filter_op in modified_date.keys():
            try:
                if hasattr(modified_date[filter_op], "strftime"):
                    # It's already a datetime object, no need to convert
                    pass
            except (TypeError, ValueError, AttributeError):
                pass

        print(f"Modified date: {modified_date}")

        # Create filter conditions in the new format: [[field, operator, value], ...]
        filter_conditions = []

        # Common operators mapping
        operator_map = {
            "gt": ">",
            "lt": "<",
            "gte": ">=",
            "lte": "<=",
            "eq": "=",
            "ne": "!=",
        }

        # Process each filter operator
        for filter_op, value in modified_date.items():
            # Map the operator
            operator = operator_map.get(filter_op)
            if not operator:
                logger.warning(f"Unknown operator '{filter_op}', skipping")
                continue

            # Format the value if it's a datetime
            if hasattr(value, "strftime"):
                value = value.strftime("%Y-%m-%d")

            # Add the condition
            filter_conditions.append([date_field, operator, value])

        return filter_conditions or None

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
                dt = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
            else:
                dt = date_str

            # Format for legacy API (check config for format or use ISO format)
            # date_format = self.config.get('date_format', '%Y-%m-%d')
            return dt.strftime("%Y-%m-%d")

        except Exception as e:
            logger.warning(f"Error formatting date: {str(e)}")
            return date_str  # Return original if parsing fails

    def _generate_cache_key(self, query_params=None):
        """Generate a cache key based on table name and query params.
        
        Args:
            query_params: Query parameters for filtering
            
        Returns:
            A string cache key
        """
        # Create a sorted, deterministic representation of query_params
        if query_params:
            # Convert query_params to a sorted, deterministic string representation
            try:
                # Sort the keys to ensure consistent ordering
                sorted_params = sorted(query_params.items())
                params_str = json.dumps(sorted_params)
            except (TypeError, ValueError):
                # If we can't serialize the params, use their string representation
                params_str = str(sorted([(k, str(v)) for k, v in query_params.items()]))
        else:
            params_str = "none"
        
        # Create a unique cache key based on table name and parameters
        table_name = self.config.get('table_name', '')
        return f"{table_name}_{params_str}"

    @classmethod
    def clear_cache(cls):
        """Clear the response cache."""
        cls._response_cache.clear()
        logger.info("Cleared LegacyAPIExtractor response cache")

    @classmethod
    def get_cached_data(cls, table_name, query_params=None):
        """Retrieve data from cache if available.
        
        Args:
            table_name: Table name to retrieve data for
            query_params: Query parameters used for the cache key
            
        Returns:
            Cached data if available, None otherwise
        """
        # Extract top limit if present
        top_limit = None
        if query_params and "$top" in query_params:
            top_limit = query_params["$top"]
            logger.info(f"Will limit cached results to top {top_limit} records")
        
        # Create a cache key without needing a full instance
        if query_params:
            try:
                # Sort the keys to ensure consistent ordering
                sorted_params = sorted(query_params.items())
                params_str = json.dumps(sorted_params)
            except (TypeError, ValueError):
                # If we can't serialize the params, use their string representation
                params_str = str(sorted([(k, str(v)) for k, v in query_params.items()]))
        else:
            params_str = "none"
        
        # Create a unique cache key based on table name and parameters
        cache_key = f"{table_name}_{params_str}"
        
        # Return cached data if available
        if cache_key in cls._response_cache:
            data = cls._response_cache[cache_key]
            logger.info(f"Using cached data for {table_name} (cache key: {cache_key[:50]}...)")
            
            # Convert to list of dictionaries if needed
            if hasattr(data, 'to_dict') and callable(data.to_dict):
                try:
                    result = data.to_dict(orient="records")
                except Exception as e:
                    logger.error(f"Error converting DataFrame: {e}")
                    try:
                        result = data.to_dict('records')
                    except:
                        # Manual conversion
                        result = []
                        for i in range(len(data)):
                            result.append(dict(data.iloc[i]))
            else:
                result = data
            
            # Apply top limit if specified
            if top_limit and isinstance(result, list):
                logger.info(f"Limiting cached results to top {top_limit} records (from {len(result)} total)")
                return result[:int(top_limit)]
            
            return result
        
        return None
