"""
Base classes for legacy ERP API clients.

This module provides base classes and common functionality for interacting
with the legacy ERP system.
"""

import os
import json
from datetime import datetime
from typing import Optional, Dict, Any
import time
import urllib.parse

import pandas as pd
import requests
from pyerp.external_api.legacy_erp.settings import (
    API_ENVIRONMENTS,
    API_REQUEST_TIMEOUT,
    API_REST_ENDPOINT,
)
from pyerp.external_api.legacy_erp.auth import (
    read_cookie_file_safe,
    write_cookie_file_safe,
)
from pyerp.utils.logging import (
    get_logger,
    log_api_request,
    log_performance,
)

# Get logger for this module
logger = get_logger(__name__)

# File for storing the session cookie globally
COOKIE_FILE_PATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    ".global_session_cookie",
)


class BaseAPIClient:
    """Base class for legacy ERP API clients."""

    def __init__(self, environment: str = "live", timeout: int = None):
        """
        Initialize a new client instance.

        Args:
            environment: Which API environment to use ('live', 'test', etc.)
            timeout: Optional custom timeout for API requests (in seconds)
        """
        self.environment = environment
        self.timeout = timeout or API_REQUEST_TIMEOUT
        self.session = requests.Session()
        self.session_id = None

        # Validate environment configuration
        if environment not in API_ENVIRONMENTS:
            available_envs = list(API_ENVIRONMENTS.keys())
            error_msg = (
                f"Invalid environment: '{environment}'. "
                f"Available: {available_envs}"
            )
            logger.error(error_msg)
            raise ValueError(error_msg)

        env_config = API_ENVIRONMENTS[environment]
        if "base_url" not in env_config:
            error_msg = (
                f"Missing URL configuration for environment '{environment}'"
            )
            logger.error(error_msg)
            raise ValueError(error_msg)

        self.base_url = env_config["base_url"]
        self.username = env_config.get("username")
        self.password = env_config.get("password")

        logger.info(
            "Initialized %s for environment: %s",
            self.__class__.__name__,
            environment,
        )

    def _make_request(self, method: str, endpoint: str, **kwargs) -> requests.Response:
        """Make an HTTP request to the API with logging and timing."""
        # Always prefix with REST endpoint
        endpoint = f"{API_REST_ENDPOINT}/{endpoint.lstrip('/')}"

        # REVERTED BACK: Use base_request_url
        base_request_url = f"{self.base_url}/{endpoint.lstrip('/')}"

        # Log the session cookie being used (safely showing only part of it)
        if self.session_id:
            safe_id = (
                f"{self.session_id[:5]}...{self.session_id[-5:]}"
                if len(self.session_id) > 10
                else self.session_id
            )
            logger.info(f"Using session cookie WASID4D={safe_id}")
        else:
            logger.info("No session cookie available")

        # Extract params for logging and request
        params = kwargs.get("params")
        encoded_filter_part = None

        # --- RE-ADD: Manually URL-encode and append $filter --- 
        if params and "$filter" in params:
            filter_value = params.pop("$filter")
            if isinstance(filter_value, str):
                # safe='' ensures even special chars like = / etc. are encoded
                encoded_filter_part = f"$filter={urllib.parse.quote(filter_value, safe='')}"
                logger.info(f"Manually URL-encoded filter part: {encoded_filter_part}")
            else:
                logger.warning("Filter value is not a string, skipping manual encoding/appending.")
                # Put it back if not encoded? Or maybe error? For now, just log.
        # --- End Re-Add ---

        # Construct final URL # RE-ADD logic
        final_url = base_request_url
        # Append manually encoded filter if present
        if encoded_filter_part:
            # Check if base_request_url already has query params
            query_separator = "&" if "?" in final_url else "?"
            final_url += query_separator + encoded_filter_part
            logger.info(f"URL with manually appended filter: {final_url}")
        
        # Log the intended URL and parameters that will be automatically handled by requests # RE-ADD
        logger.info(f"Request URL (base): {base_request_url}")
        logger.info(f"Request URL (final): {final_url}")
        if params: # Log remaining params
            logger.info(f"Request Params (handled by requests): {params}")
        else:
            logger.info("Request Params (handled by requests): None")

        start_time = time.time()

        try:
            # Use the final URL, pass remaining params directly to requests library # RE-ADD
            response = self.session.request(
                method=method,
                url=final_url,
                params=params,
                timeout=kwargs.get("timeout", self.timeout),
            )

            duration_ms = int((time.time() - start_time) * 1000)

            # Log the API request using our centralized logging
            log_api_request(
                api_name="legacy_erp",
                endpoint=endpoint,
                status_code=response.status_code,
                response_time_ms=duration_ms,
                extra_context={
                    "method": method,
                    "environment": self.environment,
                    "url": final_url,
                    "params": params if params else {},
                },
            )

            # Log performance metrics for slow requests
            if duration_ms > 1000:  # Log requests taking more than 1 second
                log_performance(
                    name=f"legacy_erp_{method}_{endpoint}",
                    duration_ms=duration_ms,
                    extra_context={"url": final_url, "params": params if params else {}},
                )

            return response

        except requests.RequestException as e:
            error_msg = f"API request failed: {str(e)}"
            logger.error(
                error_msg,
                extra={
                    "method": method,
                    "url": final_url,
                    "error": str(e),
                },
            )
            raise

    def _set_session_header(self, request_kwargs):
        """Set the session cookie in the request headers if available."""
        if self.session_id:
            headers = request_kwargs.get("headers", {})
            cookie_header = f"WASID4D={self.session_id}"
            if "Cookie" in headers:
                headers["Cookie"] += f"; {cookie_header}"
            else:
                headers["Cookie"] = cookie_header
            request_kwargs["headers"] = headers
            logger.debug("Added session cookie to request headers")
        return request_kwargs

    def _log_cookies(self, prefix="Current cookies"):
        """Log the current cookies in the session."""
        cookies = self.session.cookies.get_dict()
        if not cookies:
            logger.info(f"{prefix}: No cookies")
            return
        logger.info(f"{prefix}: {len(cookies)} cookie(s)")

    def _log_response_cookies(self, response, prefix="Response cookies"):
        """Log cookies received in a response."""
        if not response.cookies:
            logger.info(f"{prefix}: No cookies")
            return
        cookies = response.cookies.get_dict()
        logger.info(f"{prefix}: {len(cookies)} cookie(s)")

    def load_session_cookie(self):
        """Load session cookie value from file if it exists."""
        if not os.path.exists(COOKIE_FILE_PATH):
            logger.info("No session cookie file found")
            return False

        if not hasattr(self, "base_url") or not self.base_url:
            logger.warning("Base URL not initialized")
            return False

        # Use thread-safe function to read cookie data
        cookie_data = read_cookie_file_safe()
        if cookie_data is None:
            return False

        # Handle old format (single cookie object)
        if isinstance(cookie_data, dict) and "value" in cookie_data:
            logger.info("Found cookie file in old format, converting to new format")
            # Convert to new format
            timestamp = cookie_data.get("timestamp", datetime.now().isoformat())
            new_format = [
                {
                    "base_url": self.base_url,
                    "session_id": cookie_data["value"],
                    "timestamp": timestamp,
                }
            ]

            # Save in new format using thread-safe function
            if not write_cookie_file_safe(new_format):
                logger.warning("Failed to convert cookie file format")
                return False

            # Set the session cookie
            self.session_id = cookie_data["value"]
            self._clear_cookies("WASID4D")
            self.session.cookies.set("WASID4D", self.session_id)
            logger.info("Converted and loaded session ID")
            return True

        # Handle new format (list of sessions)
        if isinstance(cookie_data, list):
            # Find the session for the current base URL
            for entry in cookie_data:
                if not isinstance(entry, dict):
                    continue

                if entry.get("base_url") == self.base_url and "session_id" in entry:
                    self.session_id = entry["session_id"]
                    self._clear_cookies("WASID4D")
                    self.session.cookies.set("WASID4D", self.session_id)
                    logger.info(f"Loaded session ID for base URL: {self.base_url}")
                    return True

            logger.info(f"No session found for base URL: {self.base_url}")
            return False

        logger.warning(f"Cookie file has invalid format: {type(cookie_data)}")
        return False

    def _clear_cookies(self, cookie_name):
        """Clear all cookies with the specified name to prevent duplicates."""
        try:
            if cookie_name in self.session.cookies:
                logger.info(
                    f"Clearing existing {cookie_name} cookies to prevent duplicates",
                )
                cookies_to_remove = []
                for cookie in self.session.cookies:
                    if cookie.name == cookie_name:
                        cookies_to_remove.append(cookie)

                # Remove each cookie
                for cookie in cookies_to_remove:
                    self.session.cookies.clear(cookie.domain, cookie.path, cookie.name)

                # Verify they're cleared
                remaining = sum(
                    1 for c in self.session.cookies if c.name == cookie_name
                )
                if remaining > 0:
                    logger.warning(
                        f"Failed to clear all {cookie_name} cookies, {remaining} remain",
                    )
                else:
                    logger.info(f"Successfully cleared all {cookie_name} cookies")
        except Exception as e:
            logger.warning(f"Error while clearing cookies: {e}")

    def save_session_cookie(self):
        """Save current session ID to file."""
        # Extract session ID from cookies
        wasid_cookie = self.session.cookies.get("WASID4D")
        dsid_cookie = self.session.cookies.get("4DSID_WSZ-DB")

        # Prefer WASID4D cookie, fall back to 4DSID_WSZ-DB
        session_id = wasid_cookie or dsid_cookie

        if not session_id:
            logger.warning("No session ID found in cookies")
            return False

        # Create the new session entry
        new_entry = {
            "base_url": self.base_url,
            "session_id": session_id,
            "timestamp": datetime.now().isoformat(),
        }

        # Read existing sessions using thread-safe function
        cookie_data = read_cookie_file_safe()
        existing_sessions = []

        # Convert old format or use existing sessions
        if cookie_data is None:
            # No data or error reading - start with empty list
            existing_sessions = []
        elif isinstance(cookie_data, dict) and "value" in cookie_data:
            # Old format - convert to new format
            existing_sessions = []
        elif isinstance(cookie_data, list):
            # New format - use as is
            existing_sessions = cookie_data
        else:
            logger.warning(f"Invalid cookie file format: {type(cookie_data)}")
            existing_sessions = []

        # Update or add new session
        updated = False
        for entry in existing_sessions:
            if isinstance(entry, dict) and entry.get("base_url") == self.base_url:
                entry.update(new_entry)
                updated = True
                break

        if not updated:
            existing_sessions.append(new_entry)
        logger.info(f"existing_sessions : {existing_sessions}")
        # Save using thread-safe function
        success = write_cookie_file_safe(existing_sessions)
        if success:
            logger.info(f"Saved session ID for base URL: {self.base_url}")
        return success

    def validate_session(self):
        """
        Validate the current session by making a test request to the $info endpoint.

        Returns:
            bool: True if the session is valid, False otherwise
        """
        logger.debug("Validating current session")

        if not self.session_id:
            logger.debug("No session ID available")
            return False

        try:
            # Make a lightweight request to $info endpoint to validate the session
            response = self._make_request(
                "GET",
                "$info",
                timeout=self.timeout,
            )
            if not self.load_session_cookie():
                logger.info(
                    "No valid session found for this base URL, attempting login"
                )
                return self.login()

            self._log_response_cookies(response)

            is_valid = response.status_code == 200
            if is_valid:
                logger.debug("Session is valid")

                # Check for new session cookie in the response
                wasid_cookie = None
                for cookie in response.cookies:
                    if cookie.name == "WASID4D":
                        wasid_cookie = cookie.value
                        logger.info(
                            f"Found new session cookie in response: {cookie.name}"
                        )
                        break

                # If we received a new cookie, update our session
                if wasid_cookie:
                    logger.info("Updating session with new cookie from response")
                    self.session.cookies.clear()
                    logger.info("Cleared all existing cookies")

                    # Set the new cookie value
                    self.session_id = wasid_cookie
                    self.session.cookies.set("WASID4D", wasid_cookie)
                    logger.info(
                        "Set single new cookie WASID4D with value from response"
                    )

                    # Save the updated cookie
                    self.save_session_cookie()
                else:
                    logger.info("No new session cookie received, keeping existing one")
                    if self.session_id and not self.session.cookies.get("WASID4D"):
                        logger.info("Re-adding existing session cookie")
                        self.session.cookies.clear()
                        self.session.cookies.set("WASID4D", self.session_id)
            else:
                logger.warning(
                    "Session validation failed with status code %d",
                    response.status_code,
                )
            return is_valid

        except requests.RequestException as e:
            logger.warning("Session validation request failed: %s", str(e))
            return False

    def login(self):
        """Log in to the legacy ERP system and obtain a session cookie."""
        logger.info("Attempting login to legacy ERP system")
        try:

            self.session.cookies.clear()
            logger.info("Cleared existing cookies")

            # Check if a session already exists for this base URL
            if self.load_session_cookie():
                logger.info("Existing session found for this base URL, reusing it")
                return True

            response = self._make_request(
                "GET",
                "$info",
                timeout=self.timeout,
            )

            if response.status_code == 200:
                # Extract session ID from cookies
                wasid_cookie = self.session.cookies.get("WASID4D")
                dsid_cookie = self.session.cookies.get("4DSID_WSZ-DB")

                if wasid_cookie or dsid_cookie:
                    self.session_id = wasid_cookie or dsid_cookie
                    self.save_session_cookie()
                    logger.info("Successfully logged in and saved session cookie")
                    return True
                else:
                    logger.info("Login successful but no session cookie received, continuing without authentication")
                    return True
            else:
                logger.error(
                    "Login failed with status code %d: %s",
                    response.status_code,
                    response.text,
                )
                return False

        except requests.RequestException as e:
            logger.error("Login request failed: %s", str(e))
            return False

    def ensure_session(self):
        """
        Ensure we have a valid session, creating one if necessary.

        Returns:
            bool: True if a valid session is available, False otherwise
        """
        logger.debug("Ensuring valid session is available")

        # First try loading an existing session
        if not self.session_id and self.load_session_cookie():
            logger.info("Loaded existing session from cookie file")

        # Validate the current session if we have one
        if self.session_id and self.validate_session():
            logger.debug("Current session is valid")
            return True

        # Try to establish a new session
        logger.info("Current session invalid or missing, attempting to login")
        return self.login()

    def _parse_legacy_date(self, date_str: str) -> Optional[datetime]:
        """
        Parse a date string from the legacy ERP system.

        The legacy system uses various date formats, this method attempts to
        parse them into a standard datetime object.

        Args:
            date_str: The date string to parse

        Returns:
            datetime object if parsing succeeds, None otherwise
        """
        if not date_str or not isinstance(date_str, str):
            return None

        # Handle DD!MM!YYYY format (primary legacy format)
        if "!" in date_str:
            try:
                day, month, year = map(int, date_str.split("!"))
                if year > 0 and month > 0 and day > 0:
                    return datetime(year, month, day)
            except (ValueError, IndexError):
                pass

        # Common date formats in the legacy system
        formats = [
            "%Y-%m-%d",
            "%Y-%m-%d %H:%M:%S",
            "%d.%m.%Y",
            "%d.%m.%Y %H:%M:%S",
            "%Y%m%d",
        ]

        for fmt in formats:
            try:
                return datetime.strptime(date_str.strip(), fmt)
            except ValueError:
                continue

        logger.debug("Could not parse date string '%s' with any known format", date_str)
        return None

    def _transform_dates_in_record(self, record: Dict[str, Any]) -> Dict[str, Any]:
        """
        Transform date strings in a record to datetime objects.
        Only transforms fields that are known to contain dates.

        Args:
            record: Dictionary containing record data

        Returns:
            Dictionary with date strings converted to datetime objects
        """
        if not isinstance(record, dict):
            logger.warning(
                "Expected dict for date transformation, got %s", type(record).__name__
            )
            return record

        transformed = {}
        # Fields that are known to contain dates
        date_fields = {
            "__TIMESTAMP",  # Standard timestamp field
            "modified_date",
            "created_date",
            "Release_date",
            "Auslaufdatum",  # Discontinuation date
            "last_modified",
            "CREATIONDATE",
            "MODIFICATIONDATE",
            "UStID_Dat",
            "letzteLieferung",
            "Druckdatum",
            "Release_Date",
            'Termin',
            'eingestellt',
            'Artikel_Termin',
            'Datum_begin',

        }

        for key, value in record.items():
            if key in date_fields and isinstance(value, str):
                try:
                    parsed_date = self._parse_legacy_date(value)
                    transformed[key] = (
                        parsed_date if parsed_date is not None else value
                    )
                except ValueError as e:
                    logger.debug(
                        "Failed to parse date for field %s: %s", key, str(e)
                    )
                    transformed[key] = value
            else:
                transformed[key] = value

        return transformed

    def fetch_table(
        self,
        table_name: str,
        top: Optional[int] = None,
        skip: int = 0,
        filter_query: Optional[str] = None,
        all_records: bool = False,
        new_data_only: bool = True,
        date_created_start: Optional[str] = None,
        fail_on_filter_error: bool = False,
    ) -> pd.DataFrame:
        """
        Fetch records from a table in the legacy ERP system, handling pagination
        if all_records is True.

        Args:
            table_name: Name of the table to fetch from
            top: Max number of records to fetch per request if not fetching all.
                 When all_records=True, this acts as the page size (defaulting to 100).
            skip: Initial number of records to skip.
            filter_query: Filter criteria (list of lists or string).
            all_records: If True, fetch all records using pagination.
            new_data_only: Currently unused in this base method.
            date_created_start: Currently unused.
            fail_on_filter_error: Whether to raise an error on filter issues.

        Returns:
            DataFrame containing the fetched records.
        """
        logger.info(
            "Fetching table %s (all_records=%s, top=%s, skip=%d, filter=%s)",
            table_name,
            all_records,
            top if top is not None else "API Default",
            skip,
            filter_query or "None",
        )

        try:
            if not self.ensure_session():
                raise RuntimeError("Failed to establish a valid session")

            all_fetched_records = []
            current_skip = skip
            page_size = top if top is not None else 100  # Use top as page size or default

            while True:
                params = {"$skip": current_skip}
                request_top = page_size if all_records else top
                if request_top is not None:
                    params["$top"] = request_top

                # --- Filter Query Processing (REVERTED AND FIXED) ---
                if filter_query:
                    if isinstance(filter_query, list):
                        filter_parts = []
                        for filter_item in filter_query:
                            try:
                                if len(filter_item) != 3:
                                    logger.warning(
                                        f"Invalid filter item format: {filter_item}. "
                                        "Expected [field, operator, value]."
                                    )
                                    continue
                                field, operator, value = filter_item
                                # Format value appropriately (e.g., quote strings)
                                if isinstance(value, str):
                                    # Escape single quotes within the string value
                                    safe_value = value # REMOVED manual escaping
                                    # Quote the string value using double quotes
                                    formatted_value = f'"{safe_value}"'
                                elif hasattr(value, "strftime"):
                                    formatted_value = value.strftime("%Y-%m-%d")
                                else:
                                    formatted_value = value

                                # Construct the filter part
                                if isinstance(value, str) and operator == '=':
                                    filter_part_str = f"'{field} {operator} {formatted_value}'"
                                else:
                                    filter_part_str = f"{field} {operator} {formatted_value}"
                                filter_parts.append(filter_part_str)
                            except Exception as e:
                                error_msg = f"Error processing filter item {filter_item}: {str(e)}"
                                logger.error(error_msg)
                                if fail_on_filter_error:
                                    raise RuntimeError(error_msg) from e
                        if filter_parts:
                            # Check if all filters are for the same field
                            is_multi_field = False
                            if len(filter_parts) > 1:
                                first_field = None
                                if filter_query and len(filter_query[0]) == 3:
                                    first_field = filter_query[0][0]
                                if first_field:
                                    is_multi_field = any(
                                        item[0] != first_field for item in filter_query
                                        if len(item) == 3
                                    )

                            # Use 'or' if all filters target the same field, 'and' otherwise
                            joiner = " and " if is_multi_field else " or "
                            params["$filter"] = joiner.join(filter_parts)
                        else:
                            logger.warning("No valid filter parts found in filter query")
                    else:
                        # Assumes filter_query is already a string if not a list
                        params["$filter"] = filter_query
                # --- End Filter Query Processing ---

                logger.debug(
                    f"Fetching page for {table_name}: skip={current_skip}, "
                    f"top={params.get('$top')}"
                )
                response = self._make_request(
                    "GET",
                    table_name,
                    params=params,
                    timeout=self.timeout,
                )

                if response.status_code != 200:
                    error_msg = (
                        f"Failed to fetch table {table_name} "
                        f"(page starting at {current_skip}): "
                        f"Status {response.status_code}"
                    )
                    logger.error(error_msg)
                    raise RuntimeError(error_msg)

                try:
                    data = response.json()
                except json.JSONDecodeError as e:
                    error_msg = f"Failed to parse JSON response (page starting at {current_skip}): {str(e)}"
                    logger.error(error_msg)
                    raise RuntimeError(error_msg)

                records = data.get("__ENTITIES", [])
                num_fetched = len(records)
                logger.debug(f"Fetched {num_fetched} records for this page.")

                if num_fetched > 0:
                    # Transform dates before adding
                    transformed_records = [
                        self._transform_dates_in_record(record) for record in records
                    ]
                    all_fetched_records.extend(transformed_records)

                # --- Loop termination logic ---
                if not all_records:
                    break

                if num_fetched < page_size:
                    logger.info(f"Last page reached for {table_name}, fetched {num_fetched} records.")
                    break

                if num_fetched == 0:
                    logger.info(f"Empty page received for {table_name}, assuming end of data.")
                    break
                # --- End Loop termination logic ---

                # Prepare for the next iteration
                current_skip += num_fetched

            # --- End While Loop ---

            total_records_fetched = len(all_fetched_records)
            logger.info(
                "Finished fetching for table %s. Total records retrieved: %d",
                table_name,
                total_records_fetched,
            )

            if not all_fetched_records:
                return pd.DataFrame()  # Return empty DataFrame if no records found

            return pd.DataFrame(all_fetched_records)

        except Exception as e:
            # Catch any other unexpected errors during the process
            error_msg = f"Error fetching table {table_name}: {str(e)}"
            logger.exception(error_msg)  # Use exception to log traceback
            raise RuntimeError(error_msg) from e
