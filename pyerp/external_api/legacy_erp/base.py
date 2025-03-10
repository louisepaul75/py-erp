"""
Base classes for legacy ERP API clients.

This module provides base classes and common functionality for interacting
with the legacy ERP system.
"""

import logging
import os
import json
from datetime import datetime
from typing import Optional, Dict, Any

import pandas as pd
import requests
from requests.auth import HTTPBasicAuth

from pyerp.external_api.legacy_erp.settings import (
    API_ENVIRONMENTS,
    API_REQUEST_TIMEOUT,
)

# Configure logging
logger = logging.getLogger(__name__)

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
            raise ValueError(
                f"Invalid environment: '{environment}'. "
                f"Available: {available_envs}",
            )

        env_config = API_ENVIRONMENTS[environment]
        if "base_url" not in env_config:
            raise ValueError(
                f"Missing URL configuration for environment '{environment}'"
            )

        self.base_url = env_config["base_url"]
        self.username = env_config.get("username")
        self.password = env_config.get("password")
        
        if not self.username or not self.password:
            raise ValueError(
                f"Missing credentials for environment '{environment}'"
            )
        
        logger.debug(
            "Initialized %s for environment: %s",
            self.__class__.__name__,
            environment,
        )

    def _set_session_header(self, request_kwargs):
        """Set the session cookie in the request headers if available."""
        if self.session_id:
            headers = request_kwargs.get("headers", {})

            # Create the cookie header with WASID4D=value format
            cookie_header = f"WASID4D={self.session_id}"

            # Add to existing cookies if present
            if "Cookie" in headers:
                headers["Cookie"] += f"; {cookie_header}"
            else:
                headers["Cookie"] = cookie_header

            request_kwargs["headers"] = headers

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

        try:
            with open(COOKIE_FILE_PATH) as f:
                cookie_data = json.load(f)

                if "value" in cookie_data:
                    # Extract the cookie value
                    self.session_id = cookie_data["value"]

                    # Clear any existing WASID4D cookies to prevent duplicates
                    self._clear_cookies("WASID4D")

                    # Set the WASID4D cookie with the loaded value
                    self.session.cookies.set("WASID4D", self.session_id)

                    logger.info(f"Loaded session ID from {COOKIE_FILE_PATH}")
                    return True
                logger.warning("Cookie file has invalid format (missing 'value' field)")
                return False

        except Exception as e:
            logger.warning(f"Failed to load session cookie: {e}")
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

        # Store just the value, not the name=value format
        self.session_id = session_id

        # Create the cookie data in the simpler format that worked before
        cookie_data = {"timestamp": datetime.now().isoformat(), "value": session_id}

        # Ensure directory exists
        os.makedirs(os.path.dirname(COOKIE_FILE_PATH), exist_ok=True)

        # Save the cookie data
        try:
            with open(COOKIE_FILE_PATH, "w") as f:
                json.dump(cookie_data, f)
            logger.info(f"Saved session ID to {COOKIE_FILE_PATH}")
            return True
        except Exception as e:
            logger.warning(f"Failed to save session ID: {e}")
            return False

    def validate_session(self):
        """Validate the current session by making a simple API request."""
        try:
            logger.info("------ VALIDATING SESSION ------")
            self._log_cookies("Cookies before validation")

            # Try a simple API request to check if our session is valid
            url = f"{self.base_url}/rest/$info"
            logger.info(f"Validation request URL: {url}")

            # Make the request, ensuring the session cookie is used
            response = self.session.get(url)

            # Log response and cookies
            logger.info(f"Validation response status: {response.status_code}")
            self._log_response_cookies(response)

            # Check if we got a successful response
            if response.status_code == 200:
                logger.info("Session validated successfully")

                # Get the new session cookie from the response
                wasid_cookie = None
                for cookie in response.cookies:
                    if cookie.name == "WASID4D":
                        wasid_cookie = cookie.value
                        logger.info("Found new session cookie in response")
                        break

                # If we received a new cookie, update our session
                if wasid_cookie:
                    logger.info("Updating session with new cookie from response")
                    self.session.cookies.clear()
                    logger.info("Cleared all existing cookies")

                    # Set the new cookie value
                    self.session_id = wasid_cookie
                    self.session.cookies.set("WASID4D", wasid_cookie)
                    logger.info("Set single new cookie WASID4D")
                    return True
                else:
                    logger.info("No new session cookie in response")
                    return True
            else:
                logger.warning(
                    f"Session validation failed with status {response.status_code}"
                )
                return False

        except Exception as e:
            logger.error(f"Error validating session: {e}")
            return False

    def login(self):
        """Attempt to log in and get a new session cookie."""
        try:
            logger.info("------ LOGGING IN ------")
            self.session.cookies.clear()
            logger.info("Cleared existing cookies")

            # Attempt to access an endpoint that will set a cookie
            url = f"{self.base_url}/rest/$info"
            logger.info(f"Login request URL: {url}")

            # Make the request with basic auth
            auth = HTTPBasicAuth(self.username, self.password)
            response = self.session.get(url, auth=auth)

            # Log response details
            logger.info(f"Login response status: {response.status_code}")
            self._log_response_cookies(response)

            # Check if we got cookies in the response
            wasid_cookie = None
            for cookie in response.cookies:
                if cookie.name == "WASID4D":
                    wasid_cookie = cookie.value
                    break

            dsid_cookie = self.session.cookies.get("4DSID_WSZ-DB")

            # Log what we found
            logger.info(f"Found WASID4D cookie: {'Yes' if wasid_cookie else 'No'}")
            logger.info(f"Found 4DSID_WSZ-DB cookie: {'Yes' if dsid_cookie else 'No'}")

            # Use either cookie (prefer WASID4D)
            if wasid_cookie:
                self.session.cookies.clear()
                self.session_id = wasid_cookie
                self.session.cookies.set("WASID4D", wasid_cookie)
                safe_id = (
                    f"{wasid_cookie[:5]}...{wasid_cookie[-5:]}"
                    if len(wasid_cookie) > 10
                    else wasid_cookie
                )
                logger.info(f"Set single WASID4D cookie: {safe_id}")
                self.save_session_cookie()
                return True
            if dsid_cookie:
                self.session.cookies.clear()
                self.session_id = dsid_cookie
                self.session.cookies.set("WASID4D", dsid_cookie)
                safe_id = (
                    f"{dsid_cookie[:5]}...{dsid_cookie[-5:]}"
                    if len(dsid_cookie) > 10
                    else dsid_cookie
                )
                logger.info(f"Set single WASID4D cookie using 4DSID value: {safe_id}")
                self.save_session_cookie()
                return True
            logger.warning("No session cookies received during login attempt")
            return False
        except Exception as e:
            logger.warning(f"Login failed: {e}")
            return False

    def ensure_session(self):
        """Ensure we have a valid session, attempting login if needed."""
        if not self.session_id:
            logger.info("No session ID loaded, attempting login")
            return self.login()

        # Clear all cookies and start fresh
        self.session.cookies.clear()

        # Set just our session ID cookie
        self.session.cookies.set("WASID4D", self.session_id)
        safe_id = (
            f"{self.session_id[:5]}...{self.session_id[-5:]}"
            if len(self.session_id) > 10
            else self.session_id
        )
        logger.info(f"Set single WASID4D cookie: {safe_id}")

        # Validate the session
        if self.validate_session():
            return True

        # If validation failed, try to log in
        logger.info("Session validation failed, attempting to get a new session")
        return self.login()

    def _parse_legacy_date(self, date_str: str) -> Optional[datetime]:
        """Parse a date string from the legacy system format (DD!MM!YYYY).
        
        Args:
            date_str: Date string in DD!MM!YYYY format
            
        Returns:
            Parsed datetime or None if parsing fails
        """
        if not date_str or date_str == "0!0!0":
            return None
        try:
            day, month, year = map(int, date_str.split("!"))
            return datetime(year, month, day)
        except (ValueError, AttributeError):
            logger.warning(f"Failed to parse legacy date: {date_str}")
            return None

    def _transform_dates_in_record(self, record: Dict[str, Any]) -> Dict[str, Any]:
        """Transform all date fields in a record from legacy format.
        
        Args:
            record: Record containing potential date fields
            
        Returns:
            Record with transformed date fields
        """
        # Common date field names in the legacy system
        date_fields = [
            'Release_date', 'Release_Date',  # Different cases observed
            'Auslaufdatum', 'modified_date',
            'CREATIONDATE', 'MODIFICATIONDATE'
        ]
        
        for field in date_fields:
            if field in record and record[field]:
                parsed_date = self._parse_legacy_date(record[field])
                if parsed_date:
                    record[field] = parsed_date.isoformat()
        
        return record

    def fetch_table(
        self,
        table_name: str,
        top: int,
        skip: int = 0,
        filter_query: Optional[str] = None,
        all_records: bool = False,
        new_data_only: bool = True,
        date_created_start: Optional[str] = None,
        fail_on_filter_error: bool = False,
    ) -> pd.DataFrame:
        """
        Fetch data from the specified table.

        Args:
            table_name: Name of the table to fetch
            top: Maximum number of records to fetch
            skip: Number of records to skip
            all_records: If True, fetch all records (may take a long time)
            filter_query: OData filter query
            new_data_only: If True, only fetch new records
            date_created_start: Start date for filtering by creation date
            fail_on_filter_error: If True, raise an error if filter doesn't work

        Returns:
            pandas.DataFrame: The fetched data
        """
        if not self.ensure_session():
            raise Exception("Failed to establish a valid session")

        # Log cookies before making the table request
        logger.info("------ FETCHING TABLE ------")
        self._log_cookies("Cookies for table request")

        # Ensure we have exactly one cookie with the correct session ID
        self.session.cookies.clear()
        if self.session_id:
            self.session.cookies.set("WASID4D", self.session_id)
            logger.info("Reset to a single session cookie for table request")
            self._log_cookies("Cookies after reset")
        else:
            logger.error("No session ID available for table request")
            raise Exception("No valid session ID available")

        # Prepare the request URL and parameters
        url = f"{self.base_url}/rest/{table_name}"

        # Handle pagination
        if all_records:
            logger.info(f"Fetching all records from {table_name}")
            return self._fetch_all_records(
                url,
                filter_query,
                new_data_only,
                date_created_start,
                fail_on_filter_error,
            )

        # Build query parameters
        params = {"$top": top, "$skip": skip}

        # Handle filter query with the correct syntax
        filter_requested = False
        if filter_query:
            filter_requested = True
            # If filter query is already in the correct format, use as is
            if filter_query.startswith("&$filter="):
                # Remove the leading & and $filter=
                filter_query = filter_query[1:]
                params["$filter"] = filter_query[7:]
            else:
                # Extract the field name and value from the filter query
                parts = filter_query.split(' ')
                if len(parts) >= 3:
                    field = parts[0]
                    operator = parts[1]
                    value = parts[2].strip("'")
                    # Construct the filter in the exact format required
                    params["$filter"] = (
                        f"'{field} {operator} '{value}'"
                    )
            logger.info(f"Using filter query: {filter_query}")

        # Handle date filtering
        if new_data_only and date_created_start:
            filter_requested = True
            date_filter = (
                f"CREATIONDATE > '{date_created_start}'"
            )
            if "$filter" in params:
                params["$filter"] = (
                    f"{params['$filter']} AND {date_filter}"
                )
            else:
                params["$filter"] = f"'{date_filter}'"
            logger.info(f"Using date filter: {date_filter}")

        logger.info(f"Full request URL: {url}")
        logger.info(f"Query parameters: {params}")

        # Build the full URL with parameters
        full_url = url
        param_strings = []
        for key, value in params.items():
            param_strings.append(f"{key}={value}")
        if param_strings:
            full_url = f"{url}?{'&'.join(param_strings)}"

        # Make the request
        try:
            response = self.session.get(full_url)
        except Exception as e:
            logger.error(f"Request failed: {e}")
            raise

        # Check for successful response
        if response.status_code != 200:
            msg = (
                f"API request failed with status code "
                f"{response.status_code}: {response.text}"
            )
            raise Exception(msg)

        # Parse the response
        data = response.json()

        # Transform dates in the response data
        if isinstance(data, dict):
            if "value" in data and isinstance(data["value"], list):
                data["value"] = [
                    self._transform_dates_in_record(record) 
                    for record in data["value"]
                ]
            elif "__ENTITIES" in data and isinstance(
                data["__ENTITIES"], list
            ):
                data["__ENTITIES"] = [
                    self._transform_dates_in_record(record) 
                    for record in data["__ENTITIES"]
                ]
        elif isinstance(data, list):
            data = [
                self._transform_dates_in_record(record) 
                for record in data
            ]

        # Convert to DataFrame
        df = None
        if "value" in data and isinstance(data["value"], list):
            df = pd.DataFrame(data["value"])
            logger.info(f"Retrieved {len(df)} records")
        elif "__ENTITIES" in data and isinstance(
            data["__ENTITIES"], list
        ):
            df = pd.DataFrame(data["__ENTITIES"])
            logger.info(
                f"Retrieved {len(df)} records from __ENTITIES"
            )
        elif isinstance(data, list):
            df = pd.DataFrame(data)
            logger.info(
                f"Retrieved {len(df)} records from direct list response"
            )
        elif isinstance(data, dict) and len(data) > 0:
            try:
                df = pd.DataFrame([data])
                logger.info(
                    "Retrieved 1 record from direct dict response"
                )
            except Exception as e:
                logger.warning(
                    f"Failed to convert response dict to DataFrame: {e}"
                )
                logger.warning(
                    f"Response keys: {list(data.keys())}"
                )
                df = pd.DataFrame()
        else:
            df = pd.DataFrame()

        # Check if filter was properly applied
        if filter_requested and fail_on_filter_error:
            # If we got a full page of results on the first request,
            # this might indicate the filter wasn't applied
            if len(df) >= top:
                msg = (
                    "Got maximum number of records when filter was "
                    "requested. Filter may not have been applied."
                )
                logger.warning(msg)
                if "$filter" in params:
                    msg = (
                        f"Filter may not have been applied correctly. "
                        f"Got {len(df)} records with filter: "
                        f"{params['$filter']}"
                    )
                    raise RuntimeError(msg)

            # If we got any records, verify they match our filter criteria
            if not df.empty and "$filter" in params:
                filter_parts = params["$filter"].strip("'").split(" ")
                if len(filter_parts) >= 3:
                    field = filter_parts[0]
                    operator = filter_parts[1]
                    value = " ".join(filter_parts[2:]).strip("'")
                    
                    if field in df.columns:
                        # Convert value to appropriate type if needed
                        if operator in ['>', '>=', '<', '<=']:
                            try:
                                value = pd.to_datetime(value)
                                df[field] = pd.to_datetime(
                                    df[field], errors='coerce'
                                )
                            except:
                                try:
                                    value = float(value)
                                    df[field] = pd.to_numeric(
                                        df[field], errors='coerce'
                                    )
                                except:
                                    pass
                        
                        # Check if any records don't match the filter
                        invalid_records = None
                        if operator == '>':
                            invalid_records = df[field] <= value
                        elif operator == '>=':
                            invalid_records = df[field] < value
                        elif operator == '<':
                            invalid_records = df[field] >= value
                        elif operator == '<=':
                            invalid_records = df[field] > value
                        elif operator == '=':
                            invalid_records = df[field] != value
                        
                        if invalid_records is not None and invalid_records.any():
                            msg = (
                                f"Filter not applied correctly. Found "
                                f"records that don't match filter: "
                                f"{params['$filter']}"
                            )
                            raise RuntimeError(msg)

        return df

    def _fetch_all_records(
        self,
        url: str,
        filter_query: Optional[str] = None,
        new_data_only: bool = True,
        date_created_start: Optional[str] = None,
        fail_on_filter_error: bool = False,
    ) -> pd.DataFrame:
        """Fetch all records from a table using pagination."""
        params = {"$top": 1000, "$skip": 0}
        filter_requested = False

        # Handle filter query with the correct syntax
        if filter_query:
            filter_requested = True
            # Log the raw filter query for debugging
            logger.info(f"Raw filter query: {filter_query}")
            
            # If filter query is already in the correct format (starts with &$filter=), use as is
            if filter_query.startswith("&$filter="):
                filter_query = filter_query[1:]  # Remove the leading &
                params["$filter"] = filter_query[7:]  # Remove "$filter="
                logger.info(f"Processed filter query (from &$filter format): {params['$filter']}")
            else:
                # Extract the field name and value from the filter query
                parts = filter_query.split(' ')
                logger.info(f"Filter query parts: {parts}")
                if len(parts) >= 3:
                    field = parts[0]
                    operator = parts[1]
                    value = parts[2].strip("'")
                    # Construct the filter in the exact format required
                    params["$filter"] = f"'{field} {operator} '{value}'"
                    logger.info(f"Constructed filter query: {params['$filter']}")

        # Handle date filtering
        if new_data_only and date_created_start:
            date_filter = f"CREATIONDATE > '{date_created_start}'"
            if "$filter" in params:
                params["$filter"] = f"{params['$filter']} AND {date_filter}"
            else:
                params["$filter"] = f"'{date_filter}'"
            logger.info(f"Added date filter: {date_filter}")

        # Fetch data using pagination
        all_data = []
        total_fetched = 0
        retry_count = 0
        max_retries = 3
        filter_error_detected = False
        
        # Log the base URL
        logger.info(f"Base URL for fetching all records: {url}")

        while True:
            self.session.cookies.clear()
            if not self.session_id:
                logger.error("No session ID available for paginated request")
                raise Exception("No valid session ID available")

            self.session.cookies.set("WASID4D", self.session_id)
            if retry_count > 0:
                logger.info(
                    f"Reset to single session cookie for retry attempt {retry_count}"
                )

            # Make the request with error handling for filter failures
            logger.info(f"Making paginated request: {url}")
            logger.info(f"With parameters: {params}")
            try:
                current_params = params.copy()
                if filter_error_detected and "$filter" in current_params:
                    logger.info(
                        "Filter error previously detected, removing filter for this request"
                    )
                    current_params.pop("$filter", None)

                # Build the full URL with parameters
                full_url = url
                param_strings = []
                for key, value in current_params.items():
                    param_strings.append(f"{key}={value}")
                if param_strings:
                    full_url = f"{url}?{'&'.join(param_strings)}"
                
                # Log the full URL for debugging
                logger.info(f"Full request URL with parameters: {full_url}")
                
                # Make the request - use the full_url directly instead of passing params separately
                try:
                    response = self.session.get(full_url)
                except Exception as e:
                    logger.error(f"Request failed: {e}")
                    raise
                
                # Check for filter-related errors
                if response.status_code != 200 and "$filter" in full_url:
                    logger.warning(
                        f"Request failed with status code {response.status_code}. "
                        f"This might be a filter error."
                    )
                    logger.warning(f"Response text: {response.text[:200]}...")
                    
                    # If we're supposed to fail on filter errors, raise an exception
                    if fail_on_filter_error:
                        raise Exception(
                            f"Filter error: Request failed with status code {response.status_code}. "
                            f"Response: {response.text[:200]}... "
                            f"The command was configured to fail on filter errors."
                        )
                    
                    # Only retry without filter if we're not configured to fail
                    logger.warning("Attempting to retry without filter...")
                    base_url = full_url.split("&$filter=")[0]
                    if not base_url.endswith("?"):
                        base_url = base_url.split("?")[0]
                    logger.info(
                        f"Retrying request without filter: {base_url}"
                    )
                    response = self.session.get(base_url)

                    # Mark that we've detected a filter error
                    filter_error_detected = True

                # Check for successful response
                if response.status_code != 200:
                    error_msg = (
                        f"API request failed with status code {response.status_code}"
                    )

                    # Check if this is a 'maximum sessions' error
                    if (
                        response.status_code == 402
                        and "Maximum number of sessions" in response.text
                    ):
                        if retry_count < max_retries:
                            logger.warning(
                                "Maximum sessions error detected. "
                                "Attempting to login with a new session..."
                            )
                            self.session.cookies.clear()
                            if self.login():
                                retry_count += 1
                                logger.info(
                                    f"Re-login successful. Retrying request "
                                    f"(attempt {retry_count}/{max_retries})"
                                )
                                continue
                        error_msg += (
                            ": Maximum number of sessions reached and retry failed"
                        )

                    error_msg += f": {response.text}"
                    raise Exception(error_msg)

                # Parse the response
                data = response.json()

                # If we're configured to fail on filter errors and we detect that
                # the filter was ignored (by getting a successful response without
                # the filter being applied), raise an exception
                if (fail_on_filter_error and "$filter" in full_url and
                    filter_error_detected):
                    raise Exception(
                        "Filter was ignored by the API. The command was "
                        "configured to fail on filter errors."
                    )

                # Extract the records based on the actual response structure
                if "value" in data and isinstance(data["value"], list):
                    records = data["value"]
                    all_data.extend(records)
                    total_fetched += len(records)
                    logger.info(
                        f"Fetched {len(records)} records (total: {total_fetched})"
                    )

                    # Check if we've received fewer records than requested
                    if len(records) < current_params.get("$top", 1000):
                        break

                    # Update skip for next page
                    params["$skip"] += params.get("$top", 1000)
                elif "__ENTITIES" in data and isinstance(data["__ENTITIES"], list):
                    records = data["__ENTITIES"]
                    all_data.extend(records)
                    total_fetched += len(records)
                    logger.info(
                        f"Fetched {len(records)} records from __ENTITIES "
                        f"(total: {total_fetched})"
                    )

                    # Check if there are more records
                    if "__COUNT" in data and total_fetched >= int(data["__COUNT"]):
                        logger.info(f"Reached total count of {data['__COUNT']} records")
                        break

                    # Update skip for next page
                    params["$skip"] += params.get("$top", 1000)
                elif isinstance(data, list):
                    all_data.extend(data)
                    total_fetched += len(data)
                    logger.info(
                        f"Fetched {len(data)} records from direct list response "
                        f"(total: {total_fetched})"
                    )
                    break
                else:
                    logger.warning("Response does not contain expected data format")
                    logger.warning(
                        f"Response keys: {list(data.keys()) if isinstance(data, dict) else 'not a dict'}"
                    )
                    break

                # Reset retry counter after successful request
                retry_count = 0

            except Exception as e:
                if "Maximum number of sessions" in str(e) and retry_count < max_retries:
                    continue
                raise

        # Convert all data to DataFrame
        df = pd.DataFrame(all_data)
        logger.info(f"Total records retrieved: {len(df)}")

        # Validate filter was properly applied
        if (filter_requested and fail_on_filter_error and 
            "$filter" in params):
            filter_parts = params["$filter"].strip("'").split(" ")
            if len(filter_parts) >= 3:
                field = filter_parts[0]
                operator = filter_parts[1]
                value = " ".join(filter_parts[2:]).strip("'")
                
                if field in df.columns:
                    # Convert value to appropriate type if needed
                    if operator in ['>', '>=', '<', '<=']:
                        try:
                            value = pd.to_datetime(value)
                            df[field] = pd.to_datetime(
                                df[field],
                                errors='coerce'
                            )
                        except:
                            try:
                                value = float(value)
                                df[field] = pd.to_numeric(
                                    df[field],
                                    errors='coerce'
                                )
                            except:
                                pass
                    
                    # Check if any records don't match the filter
                    invalid_records = None
                    if operator == '>':
                        invalid_records = df[field] <= value
                    elif operator == '>=':
                        invalid_records = df[field] < value
                    elif operator == '<':
                        invalid_records = df[field] >= value
                    elif operator == '<=':
                        invalid_records = df[field] > value
                    elif operator == '=':
                        invalid_records = df[field] != value
                    
                    if (invalid_records is not None and 
                        invalid_records.any()):
                        msg = (
                            "Filter not applied correctly. Found "
                            "records that don't match filter: "
                            f"{params['$filter']}"
                        )
                        raise RuntimeError(msg)

        return df 