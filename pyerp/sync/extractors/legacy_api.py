"""Legacy API data extractor implementation."""

import os
from datetime import datetime
from typing import Any, Dict, List
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

    # Known date keys to check for in query_params
    # Extend this list if other date fields need filtering
    KNOWN_DATE_KEYS = ["Datum", "modified_date"]

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
        """Validate extractor config, checking env vars as fallback.

        Overrides the base class method to also check environment variables.

        Raises:
            ValueError: If required configuration is missing
        """
        # Check environment variables and add them to config if available
        if "environment" not in self.config:
            env_value = os.environ.get("LEGACY_ERP_ENVIRONMENT")
            if env_value:
                logger.info(
                    f"Using environment variable LEGACY_ERP_ENVIRONMENT: {env_value}"
                )
                self.config["environment"] = env_value

        if "table_name" not in self.config:
            env_value = os.environ.get("LEGACY_ERP_TABLE_NAME")
            if env_value:
                logger.info(
                    f"Using environment variable LEGACY_ERP_TABLE_NAME: {env_value}"
                )
                self.config["table_name"] = env_value

        # Proceed with normal validation
        required_fields = self.get_required_config_fields()
        missing = [
            field for field in required_fields if field not in self.config
        ]
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
            self.connection = LegacyERPClient(
                environment=self.config["environment"]
            )
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

        # Ensure query_params is a dictionary
        query_params = query_params or {}

        # Check if we need to limit results
        top_limit = None
        if "$top" in query_params:
            top_limit = int(query_params["$top"])
            logger.info(f"Will limit results to top {top_limit} records")

        # Handle parent record IDs filtering if provided
        parent_filter = None
        if "parent_record_ids" in query_params:
            parent_ids = query_params["parent_record_ids"]
            logger.info(
                f"Filtering by parent record IDs: {len(parent_ids)} IDs provided"
            )
            parent_field = query_params.get("parent_field", "AbsNr")
            if len(parent_ids) == 1:
                parent_filter = [[parent_field, "=", parent_ids[0]]]
            elif len(parent_ids) > 1:
                parent_filter = [
                    [parent_field, "=", pid] for pid in parent_ids
                ]
            if parent_filter:
                logger.info(
                    f"Created parent filter with {len(parent_filter)} conditions"
                )

        # Generate a cache key based on table name and query params
        cache_key = self._generate_cache_key(query_params)

        # Check cache
        if cache_key in self.__class__._response_cache:
            cached_data = self.__class__._response_cache[cache_key]
            logger.info(f"Using cached data for {self.config['table_name']}")
            # Apply top limit if needed
            if top_limit and isinstance(cached_data, list):
                return cached_data[:int(top_limit)]
            return cached_data

        # Execute query and fetch data
        try:
            table_name = self.config["table_name"]
            logger.info(f"Extracting data from {table_name} (cache miss)")

            # --- Build final filter_query --- 
            final_filter_query = []

            # 1. Get base filter from query_params["filter_query"]
            base_filter = query_params.get("filter_query")
            if base_filter:
                if isinstance(base_filter, list):
                    final_filter_query.extend(base_filter)
                else:
                    logger.warning(
                        f"Expected list for filter_query, got "
                        f"{type(base_filter)}. Ignoring."
                    )

            # 2. Add parent filter
            if parent_filter:
                final_filter_query.extend(parent_filter)

            # 3. Add date filters
            for date_key in self.KNOWN_DATE_KEYS:
                if date_key in query_params and isinstance(query_params[date_key], dict):
                    date_filter_dict = query_params[date_key]
                    date_conditions = self._build_date_filter_query(
                        date_key, date_filter_dict
                    )
                    if date_conditions:
                        logger.info(
                            f"Adding date filter for key '{date_key}': "
                            f"{date_conditions}"
                        )
                        final_filter_query.extend(date_conditions)
                    break  # Assume only one date filter key is used per query

            # Determine pagination settings
            top = query_params.get("$top")  # Can be None
            all_records = self.config.get("all_records", True) and not top
            if top:
                logger.info(f"Using top limit: {top} - disabling pagination")

            # Execute the fetch with combined filters
            records = client.fetch_table(
                table_name=table_name,
                all_records=all_records,
                filter_query=final_filter_query if final_filter_query else None,
                top=top
            )

            # Ensure we have a list of dictionaries before caching
            if hasattr(records, 'to_dict') and callable(records.to_dict):
                try:
                    result = records.to_dict(orient="records")
                    logger.info(
                        f"Converted DataFrame to {len(result)} dictionary records"
                    )

                    # Store in cache for future use
                    self.__class__._response_cache[cache_key] = result
                    logger.info(
                        f"Cached {len(result)} records for {table_name}"
                    )
                    return result
                except Exception as e:
                    logger.error(f"Error converting DataFrame: {e}")
                    # Store the original format in the cache
                    self.__class__._response_cache[cache_key] = records
                    logger.warning("Stored original DataFrame format in cache")
                    return records

            # Store in cache for future use
            self.__class__._response_cache[cache_key] = records
            logger.info(
                f"Fetched {len(records)} records (total: {len(records)})"
            )
            return records
        except Exception as e:
            logger.error(
                f"Error extracting data from {self.config['table_name']}: {e}"
            )
            if fail_on_filter_error:
                raise ExtractError(f"Extraction failed: {e}")
            return []

    def _build_date_filter_query(
        self, date_key: str, date_filter_dict: Dict[str, Any]
    ) -> List[List[Any]]:
        """Build filter query conditions for a specific date key and filter dictionary.
        
        Args:
            date_key: The field name for the date filter (e.g., "Datum").
            date_filter_dict: Dictionary with operators and values 
                              (e.g., {"gt": "2023-01-01"}).

        Returns:
            List of filter conditions in the format [[field, operator, value], ...]
        """
        if not date_filter_dict or not isinstance(date_filter_dict, dict):
            return []

        logger.info(
            f"Building date filter conditions for key: {date_key} "
            f"with dict: {date_filter_dict}"
        )

        filter_conditions = []
        operator_map = {
            "gt": ">", "lt": "<", "gte": ">=", "lte": "<=", "eq": "=", "ne": "!=",
        }

        for filter_op, value in date_filter_dict.items():
            operator = operator_map.get(filter_op)
            if not operator:
                logger.warning(
                    f"Unknown date filter operator '{filter_op}' for key "
                    f"'{date_key}', skipping."
                )
                continue

            # Format the value (basic string check, can be expanded)
            formatted_value = str(value)  # Ensure string representation
            try:
                # Attempt basic date format check/conversion
                if isinstance(value, datetime):
                    formatted_value = value.strftime("%Y-%m-%d")
                elif isinstance(value, str) and len(value) >= 10:
                    # Assume YYYY-MM-DD format is okay, maybe validate?
                    formatted_value = value[:10]
                else:
                    # Log potential issue if format is unexpected
                    logger.debug(
                        f"Using potentially unformatted date value '{value}' "
                        f"for key '{date_key}'"
                    )
            except Exception as fmt_err:
                logger.warning(
                    f"Could not format date value '{value}' for key "
                    f"'{date_key}': {fmt_err}"
                )

            filter_conditions.append([date_key, operator, formatted_value])

        return filter_conditions

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
                params_str = str(
                    sorted([(k, str(v)) for k, v in query_params.items()])
                )
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
            logger.info(
                f"Will limit cached results to top {top_limit} records"
            )

        # Create a cache key without needing a full instance
        if query_params:
            try:
                # Sort the keys to ensure consistent ordering
                sorted_params = sorted(query_params.items())
                params_str = json.dumps(sorted_params)
            except (TypeError, ValueError):
                # If we can't serialize the params, use their string representation
                params_str = str(
                    sorted([(k, str(v)) for k, v in query_params.items()])
                )
        else:
            params_str = "none"

        # Create a unique cache key based on table name and parameters
        cache_key = f"{table_name}_{params_str}"

        # Return cached data if available
        if cache_key in cls._response_cache:
            data = cls._response_cache[cache_key]
            logger.info(
                f"Using cached data for {table_name} (cache key: "
                f"{cache_key[:50]}...)"
            )

            # Convert to list of dictionaries if needed
            if hasattr(data, 'to_dict') and callable(data.to_dict):
                try:
                    result = data.to_dict(orient="records")
                except Exception as e:
                    logger.error(f"Error converting DataFrame: {e}")
                    try:
                        result = data.to_dict('records')
                    except Exception:
                        # Manual conversion
                        result = []
                        for i in range(len(data)):
                            result.append(dict(data.iloc[i]))
            else:
                result = data

            # Apply top limit if specified
            if top_limit and isinstance(result, list):
                logger.info(
                    f"Limiting cached results to top {top_limit} records "
                    f"(from {len(result)} total)"
                )
                return result[:int(top_limit)]

            return result

        return None
