"""Legacy API data extractor implementation."""

import os
import json
import logging # Import logging
from datetime import datetime, time, timezone, date
from typing import Any, Dict, List, Optional
import pandas as pd

from pyerp.external_api.legacy_erp import LegacyERPClient
from pyerp.utils.logging import get_logger, log_data_sync_event
from pyerp.sync.exceptions import ExtractError

from .base import BaseExtractor

# Configure logger for this module
logger = logging.getLogger("pyerp.sync.extractors.legacy_api")
logger.setLevel(logging.DEBUG)  # Ensure DEBUG level is set

# Add console handler if not already present (to ensure output)
if not any(isinstance(h, logging.StreamHandler) for h in logger.handlers):
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter("%(name)s - %(levelname)s - %(message)s")
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    logger.propagate = False  # Prevent duplicate messages from root logger


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
                    f"Using environment variable LEGACY_ERP_ENVIRONMENT: "
                    f"{env_value}"
                )
                self.config["environment"] = env_value

        if "table_name" not in self.config:
            env_value = os.environ.get("LEGACY_ERP_TABLE_NAME")
            if env_value:
                logger.info(
                    f"Using environment variable LEGACY_ERP_TABLE_NAME: "
                    f"{env_value}"
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
                f"Filtering by parent record IDs: "
                f"{len(parent_ids)} IDs provided"
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
                    f"Created parent filter with {len(parent_filter)} "
                    f"conditions"
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
            has_parent_filter = bool(parent_filter)  # Check if parent filter exists

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

            # 3. Add date filters ONLY IF no parent filter is applied
            if not has_parent_filter:
                for date_key in self.KNOWN_DATE_KEYS:
                    if date_key in query_params and isinstance(
                        query_params[date_key], dict
                    ):
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
            else:
                logger.info(
                    "Skipping date filters as parent ID filter is active."
                    )

            # Determine pagination settings
            top = query_params.get("$top")  # Can be None
            all_records = self.config.get("all_records", True) and not top
            if top:
                logger.info(f"Using top limit: {top} - disabling pagination")

            # Execute the fetch with combined filters
            records = client.fetch_table(
                table_name=table_name,
                all_records=all_records,
                filter_query=final_filter_query 
                if final_filter_query else None,
                top=top
            )

            # Ensure we have a list of dictionaries before caching
            if hasattr(records, 'to_dict') and callable(records.to_dict):
                try:
                    result = records.to_dict(orient="records")
                    logger.info(
                        f"Converted DataFrame to {len(result)} dictionary "
                        f"records"
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

    def extract_batched(self, batch_size: int = 10000, query_params: Optional[Dict[str, Any]] = None):
        """
        Extract data from the API in batches using pagination.

        Args:
            batch_size: The number of records to fetch per API call.
            query_params: Additional query parameters, similar to extract(),
                          but $top and $skip will be managed internally.

        Yields:
            List of records (each batch) from the API.

        Raises:
            ExtractError: If data extraction fails during pagination.
        """
        client = self.connection
        table_name = self.config["table_name"]
        query_params = query_params or {}
        skip = 0
        processed_records = 0
        top_limit = None
        if "$top" in query_params:
             top_limit = int(query_params.pop("$top"))  # Remove from params passed to fetch_table
             logger.info(
                 f"Applying overall top limit of {top_limit} "
                 f"to batched extraction."
             )

        logger.info(
            f"Starting batched extraction from {table_name} "
            f"with batch size {batch_size}"
        )

        # --- Client-Side Filtering Setup ---
        client_filters = {}
        # Extract date filters for client-side check
        filter_date_key = None
        filter_date_gte = None
        filter_date_lte = None
        for date_key in self.KNOWN_DATE_KEYS:
            if date_key in query_params and isinstance(query_params[date_key], dict):
                filter_date_key = date_key
                date_filter_dict = query_params[date_key]
                if 'gte' in date_filter_dict:
                    filter_date_gte = pd.to_datetime(date_filter_dict['gte']).tz_localize(None)
                    logger.info(f"Client-side filter: {date_key} >= {filter_date_gte}")
                elif 'gt' in date_filter_dict: # Also consider gt
                     # Convert gt to gte for easier comparison logic
                     filter_date_gte = pd.to_datetime(date_filter_dict['gt']).tz_localize(None) + pd.Timedelta(seconds=1)
                     logger.info(f"Client-side filter (from gt): {date_key} >= {filter_date_gte}")

                if 'lte' in date_filter_dict:
                    filter_date_lte = pd.to_datetime(date_filter_dict['lte']).tz_localize(None)
                    logger.info(f"Client-side filter: {date_key} <= {filter_date_lte}")
                elif 'lt' in date_filter_dict:
                    # Convert lt to lte for easier comparison logic
                    filter_date_lte = pd.to_datetime(date_filter_dict['lt']).tz_localize(None) - pd.Timedelta(seconds=1)
                    logger.info(f"Client-side filter (from lt): {date_key} <= {filter_date_lte}")
                
                client_filters['date'] = {
                    'key': filter_date_key,
                    'gte': filter_date_gte,
                    'lte': filter_date_lte
                }
                # Assuming only one primary date key is used for filtering
                break 

        # Extract parent ID filter for client-side check
        filter_parent_ids = None
        filter_parent_field = None
        if "parent_record_ids" in query_params:
            filter_parent_ids = set(query_params["parent_record_ids"]) # Use set for faster lookups
            filter_parent_field = query_params.get("parent_field", "AbsNr")
            client_filters['parent'] = {
                'key': filter_parent_field,
                'ids': filter_parent_ids
            }
            logger.info(f"Client-side filter: {filter_parent_field} in {len(filter_parent_ids)} IDs")

        # --- Build API filter query (still send original, might help slightly) ---
        # We keep this logic to send the filter to the API, even if it doesn't 
        # handle it correctly with pagination. It might reduce some data transfer.
        final_filter_query = []
        has_parent_filter_batched = False

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
        if "parent_record_ids" in query_params:
            parent_ids = query_params["parent_record_ids"]
            parent_field = query_params.get("parent_field", "AbsNr") 
            parent_filter_part = [[parent_field, "=", pid] for pid in parent_ids]
            final_filter_query.extend(parent_filter_part)
            has_parent_filter_batched = True  

        # 3. Add date filters (send to API even if handled client-side)
        # if not has_parent_filter_batched: # Keep sending date filter regardless? Or respect the old logic?
        # Let's keep sending date filter even with parent filter for now.
        for date_key in self.KNOWN_DATE_KEYS:
            if date_key in query_params and isinstance(
                query_params[date_key], dict
            ):
                date_filter_dict = query_params[date_key]
                date_conditions = self._build_date_filter_query(
                    date_key, date_filter_dict
                )
                if date_conditions:
                    logger.info(
                        f"Adding date filter for key '{date_key}' "
                        f"(API query): {date_conditions}"
                    )
                    final_filter_query.extend(date_conditions)
                    # Removed break to allow multiple date filters if needed

        # --- Log Initial Filter --- 
        logger.info(f"API filter query for batching: {final_filter_query}")

        # --- Pagination loop ---
        while True:
            # Determine the size for the current API call
            current_batch_size = batch_size
            if top_limit is not None:
                remaining = top_limit - processed_records
                if remaining <= 0:
                    logger.info(
                        f"Reached overall top limit of {top_limit}. "
                        f"Stopping batch fetch."
                    )
                    break
                # Request only the remaining number if it's less than the full batch size
                current_batch_size = min(batch_size, remaining)

            logger.debug(
                f"Fetching batch: table={table_name}, skip={skip}, "
                f"top={current_batch_size}"
            )
            try:
                # Assuming fetch_table supports skip and top for pagination
                # We set all_records=False to enable pagination behaviour
                # Pass the pre-built filter_query
                batch = client.fetch_table(
                    table_name=table_name,
                    all_records=False,  # Explicitly disable fetching all records
                    filter_query=final_filter_query 
                    if final_filter_query else None,
                    skip=skip,
                    top=current_batch_size
                    # Pass other relevant params from query_params if needed,
                    # e.g., select, orderby
                    # select=query_params.get('$select'),
                    # orderby=query_params.get('$orderby')
                )

                # Check if batch is None or empty list/DataFrame
                if batch is None:
                    logger.warning(
                        f"Received None batch for skip={skip}, "
                        f"top={current_batch_size}. Stopping."
                    )
                    break

                # Convert to list of dicts if necessary
                records_list = []
                batch_record_count = 0
                if hasattr(batch, 'empty') and batch.empty:  # Handle empty DataFrame
                    logger.debug(f"Received empty DataFrame batch for skip={skip}.")
                    batch_record_count = 0
                    records_list = []
                elif hasattr(batch, 'to_dict') and callable(batch.to_dict):
                    try:
                        records_list = batch.to_dict(orient="records")
                        batch_record_count = len(records_list)
                    except Exception as e:
                        logger.error(
                            f"Error converting DataFrame batch: {e}. "
                            f"Stopping batch fetch."
                         )
                        break # Stop processing if conversion fails

                    # Handle case where conversion results in an empty list
                    if not records_list:
                       logger.debug(f"Converted DataFrame batch is empty for skip={skip}.")
                       batch_record_count = 0
                elif isinstance(batch, list):
                    records_list = batch
                    batch_record_count = len(records_list)
                else:
                    logger.warning(
                        f"Received unexpected batch type: {type(batch)}. "
                        f"Stopping batch fetch."
                    )
                    break

                logger.debug(
                    f"Received raw batch of {batch_record_count} records "
                    f"for skip={skip}, top={current_batch_size}"
                )

                # --- Apply Client-Side Filtering ---
                filtered_batch = []
                if client_filters and records_list:
                    for record in records_list:
                        passes_filter = True

                        # Check date filter
                        if 'date' in client_filters:
                            date_filter = client_filters['date']
                            record_date_val = record.get(date_filter['key'])
                            if record_date_val is not None:
                                try:
                                    # Convert record date to naive datetime for comparison
                                    record_date = pd.to_datetime(record_date_val).tz_localize(None)
                                    
                                    if date_filter['gte'] and not (record_date >= date_filter['gte']):
                                        passes_filter = False
                                    if passes_filter and date_filter['lte'] and not (record_date <= date_filter['lte']):
                                         passes_filter = False
                                except (ValueError, TypeError) as date_err:
                                     logger.warning(f"Could not parse date '{record_date_val}' in record for filtering key '{date_filter['key']}': {date_err}. Skipping record.")
                                     passes_filter = False # Treat parse error as filter fail for this record
                            else:
                                # Decide how to handle missing date key: fail filter or allow?
                                # For now, let's fail the filter if the key is expected but missing.
                                logger.warning(f"Date filter key '{date_filter['key']}' missing in record. Failing filter for record.")
                                passes_filter = False 
                        
                        # Check parent ID filter
                        if passes_filter and 'parent' in client_filters:
                            parent_filter = client_filters['parent']
                            record_parent_val = record.get(parent_filter['key'])
                            if record_parent_val is None or record_parent_val not in parent_filter['ids']:
                                passes_filter = False

                        # Add more client-side filters here if needed...

                        if passes_filter:
                            filtered_batch.append(record)
                    
                    logger.info(f"Client-side filtering: Received {batch_record_count} records, filtered down to {len(filtered_batch)} records.")
                    yield_list = filtered_batch
                else:
                    # No client filters defined, yield the raw batch
                    yield_list = records_list
                    logger.debug("No client-side filters active, yielding raw batch.")


                # Yield the filtered batch
                if yield_list:
                    yield yield_list
                    processed_records += len(yield_list) # Count processed AFTER filtering
                else:
                    # If the filtered batch is empty, but the raw batch wasn't, 
                    # continue fetching pages in case later pages have matching data.
                    # However, if the *raw* batch was empty or smaller than requested,
                    # the API is done sending data, so we should break.
                    if not batch_record_count:
                        logger.info(
                            "Received empty batch from API (or conversion failed). "
                            "Stopping batch fetch."
                        )
                        break
                    if batch_record_count < current_batch_size:
                        logger.info(
                            f"Received last batch from API ({batch_record_count} < "
                            f"{current_batch_size}). Stopping batch fetch."
                        )
                        break
                    # Continue loop if filtered batch is empty but raw batch was full

                # Check if the API returned fewer records than requested, indicating the end
                if batch_record_count < current_batch_size:
                    logger.info(
                        f"Received last batch ({batch_record_count} < "
                        f"{current_batch_size}). Stopping pagination."
                    )
                    break

                # Prepare for the next batch
                skip += batch_size # Increment skip by the requested batch size, not the filtered count

            except ExtractError as e:
                logger.error(f"Extraction error during batch fetch: {e}")
                raise  # Re-raise the specific error
            except Exception as e:
                logger.error(
                    f"Unexpected error during batch fetch "
                    f"(table: {table_name}, skip: {skip}): {e}"
                )
                # Depending on requirements, maybe raise ExtractError or just log
                raise ExtractError(
                    f"Unexpected error during batch fetch: {e}"
                ) from e

        logger.info(
            f"Finished batched extraction from {table_name}. "
            f"Total records yielded after filtering: {processed_records}"
        )

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
            'ge': '>=',  # Alias for gte
            'le': '<='   # Alias for lte
        }

        for op_key, date_value in date_filter_dict.items():
            api_op = operator_map.get(op_key)
            if not api_op:
                logger.warning(
                    f"Unknown date filter operator '{op_key}' for key "
                    f"'{date_key}', skipping."
                )
                continue

            formatted_date: Optional[str] = None
            try:
                # --- Start: Use YYYY-MM-DD format for >= and <= --- 
                if api_op in ('>=', '<='):
                    # Convert input to date object if needed
                    if isinstance(date_value, datetime):
                        date_obj = date_value.date()
                    elif isinstance(date_value, date):
                        date_obj = date_value
                    elif isinstance(date_value, str):
                        # Try parsing common ISO formats
                        try:
                            date_obj = datetime.fromisoformat(
                                date_value.replace("Z", "+00:00")
                            ).date()
                        except ValueError:
                            date_obj = datetime.strptime(
                                date_value, "%Y-%m-%d"
                            ).date()
                    else:
                        raise TypeError(
                            f"Unsupported type for date conversion: "
                            f"{type(date_value)}"
                        )
                    
                    formatted_date = date_obj.strftime("%Y-%m-%d")
                    logger.debug(
                        f"Using simple date format '{formatted_date}' "
                        f"for operator '{api_op}'"
                    )
                # --- End: Use YYYY-MM-DD format for >= and <= ---
                else:
                    # For other operators (like eq, gt, lt), 
                    # use the full timestamp format
                    # Note: Tests indicate gt/lt might not work reliably 
                    # with the API
                    is_end_of_day = api_op in ('<', '<=')  # Use end of day only for lt/le
                    formatted_date = self._format_date_for_api(
                        date_value, is_end_of_day
                    )
                    if formatted_date:
                        logger.debug(
                             f"Using full timestamp format '{formatted_date}' "
                             f"for operator '{api_op}'"
                         )

            except (ValueError, TypeError) as e:
                logger.warning(
                     f"Could not format/convert date value '{date_value}' "
                     f"for key '{date_key}' and op '{op_key}', skipping filter. "
                     f"Error: {e}",
                 )
                continue  # Skip this specific filter condition

            # Ensure formatting succeeded before appending
            if formatted_date is None:
                logger.warning(
                     f"Date formatting resulted in None for key '{date_key}' "
                     f"and op '{op_key}', skipping filter.",
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
            Formatted ISO 8601 UTC string 
            (e.g., "YYYY-MM-DDTHH:MM:SSZ") or None if formatting fails.
        """
        naive_dt: Optional[datetime] = None
        original_type = type(date_input)
        try:
            # 1. Parse input into naive datetime
            if isinstance(date_input, datetime):
                # If already datetime, check if naive or aware
                if (date_input.tzinfo is None or 
                        date_input.tzinfo.utcoffset(date_input) is None):
                    naive_dt = date_input  # Already naive
                else:
                    # Convert aware to naive UTC datetime first
                    naive_dt = date_input.astimezone(timezone.utc).replace(
                        tzinfo=None
                    )
            elif isinstance(date_input, date):
                # Combine date with min time
                naive_dt = datetime.combine(date_input, time.min)
            elif isinstance(date_input, str):
                # Try parsing common ISO formats
                try:
                    parsed_dt = datetime.fromisoformat(
                        date_input.replace("Z", "+00:00")
                    )
                    if (parsed_dt.tzinfo is None or 
                            parsed_dt.tzinfo.utcoffset(parsed_dt) is None):
                        naive_dt = parsed_dt
                    else:
                        naive_dt = parsed_dt.astimezone(timezone.utc).replace(
                            tzinfo=None
                        )
                except ValueError:
                     # Fallback for YYYY-MM-DD format
                    parsed_date = datetime.strptime(
                        date_input, "%Y-%m-%d"
                    ).date()
                    naive_dt = datetime.combine(parsed_date, time.min)
            else:
                logger.warning(
                    f"Unsupported date type for formatting: {type(date_input)}"
                    )
                return None

            if naive_dt is None:  # Should not happen if parsing worked
                logger.warning(f"Failed to parse date input: {date_input}")
                return None

            # 2. Determine target time based on original type and end_of_day
            target_time: time
            if end_of_day:
                # Use specific time for end of day
                target_time = time(23, 59, 59)  
            elif original_type is datetime:
                # Preserve original time only for datetime inputs
                target_time = naive_dt.time()  
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
