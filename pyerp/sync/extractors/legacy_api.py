"""Legacy API data extractor implementation."""

import os
from datetime import datetime, time, timezone, date
from typing import Any, Dict, List, Optional
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

    def _build_date_filter_query(self, date_key: str, date_filter_dict: Dict[str, Any]) -> List[List[str]]:
        """Build a filter query list for date-based filtering."""
        if not date_filter_dict:
            return []

        logger.info(
            "Building date filter conditions for key: %s with dict: %s",
            date_key, date_filter_dict
        )

        filter_query = []
        operator_map = {
            'gt': '>',
            'gte': '>=',
            'lt': '<',
            'lte': '<=',
            'eq': '=',
            'ge': '>=',
            'le': '<='
        }

        for op_key, date_value in date_filter_dict.items():
            api_op = operator_map.get(op_key)
            if not api_op:
                logger.warning(
                    "Unknown date filter operator '%s' for key '%s', skipping.",
                    op_key, date_key
                )
                continue

            # Determine if this is an end-of-day comparison
            is_end_of_day = op_key in ('lt', 'lte', 'le')
            formatted_date = self._format_date_for_api(date_value, is_end_of_day)
            if formatted_date is None: # Handle formatting errors
                logger.warning(
                    "Could not format date value '%s' for key '%s' and op '%s', skipping filter.",
                    date_value, date_key, op_key
                )
                continue
            filter_query.append([date_key, api_op, formatted_date])

        return filter_query

    def _format_date_for_api(self, date_input: Any, end_of_day: bool = False) -> Optional[str]:
        """
        Format a date input (string, date, datetime) into an ISO 8601 UTC string.
        For 'less than' comparisons, set time to end of day (23:59:59).

        Args:
            date_input: The date value (str, date, datetime).
            end_of_day: If True, set the time to 23:59:59 for the given date.

        Returns:
            Formatted ISO 8601 UTC string (e.g., "YYYY-MM-DDTHH:MM:SSZ") or None if formatting fails.
        """
        naive_dt: Optional[datetime] = None
        original_type = type(date_input)
        try:
            # 1. Parse input into naive datetime
            if isinstance(date_input, datetime):
                # If already datetime, check if naive or aware
                if date_input.tzinfo is None or date_input.tzinfo.utcoffset(date_input) is None:
                    naive_dt = date_input # Already naive
                else:
                    # Convert aware to naive UTC datetime first
                    naive_dt = date_input.astimezone(timezone.utc).replace(tzinfo=None)
            elif isinstance(date_input, date):
                # Combine date with min time
                naive_dt = datetime.combine(date_input, time.min)
            elif isinstance(date_input, str):
                # Try parsing common ISO formats
                try:
                    parsed_dt = datetime.fromisoformat(date_input.replace("Z", "+00:00"))
                    if parsed_dt.tzinfo is None or parsed_dt.tzinfo.utcoffset(parsed_dt) is None:
                         naive_dt = parsed_dt
                    else:
                         naive_dt = parsed_dt.astimezone(timezone.utc).replace(tzinfo=None)
                except ValueError:
                     # Fallback for YYYY-MM-DD format
                    parsed_date = datetime.strptime(date_input, "%Y-%m-%d").date()
                    naive_dt = datetime.combine(parsed_date, time.min)
            else:
                logger.warning("Unsupported date type for formatting: %s", type(date_input))
                return None

            if naive_dt is None: # Should not happen if parsing worked
                 logger.warning("Failed to parse date input: %s", date_input)
                 return None

            # 2. Determine target time based on original type and end_of_day
            target_time: time
            if end_of_day:
                target_time = time(23, 59, 59) # Use specific time for end of day
            elif original_type is datetime:
                target_time = naive_dt.time() # Preserve original time only for datetime inputs
            else: # Default to start of day for date or string inputs
                 target_time = time.min

            # 3. Combine date part with target time
            final_naive_dt = datetime.combine(naive_dt.date(), target_time)

            # 4. Make aware in UTC
            aware_dt = final_naive_dt.replace(tzinfo=timezone.utc)

            # 5. Format as ISO 8601 with Z for UTC
            return aware_dt.strftime("%Y-%m-%dT%H:%M:%SZ")

        except (ValueError, TypeError) as e:
            logger.warning("Error formatting date '%s': %s", date_input, e)
            return None

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
