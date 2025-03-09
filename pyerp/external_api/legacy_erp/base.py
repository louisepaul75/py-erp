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

from pyerp.external_api.legacy_erp.settings import (
    API_ENVIRONMENTS,
    API_REQUEST_TIMEOUT,
    API_REST_ENDPOINT,
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

            # Make the request
            response = self.session.get(url)

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

    def fetch_table(
        self,
        table_name: str,
        top: int = 100,
        skip: int = 0,
        filter_query: Optional[str] = None,
        all_records: bool = False,
        new_data_only: bool = True,
        date_created_start: Optional[str] = None,
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
            )

        # Build base URL with pagination
        url = f"{url}?$top={top}&$skip={skip}"

        # Handle filter query with the correct syntax
        if filter_query:
            # If filter query is already in the correct format (starts with &$filter=), use as is
            if not filter_query.startswith("&$filter="):
                # Extract the field name and value from the filter query
                parts = filter_query.split(' ')
                if len(parts) >= 3:
                    field = parts[0]
                    operator = parts[1]
                    value = parts[2]
                    # Construct the filter in the exact format required
                    filter_query = f"&$filter='{field} {operator} '{value}''"
            url = f"{url}{filter_query}"
            logger.info(f"Using filter query: {filter_query}")

        # Handle date filtering
        if new_data_only and date_created_start:
            date_filter = f"CREATIONDATE ge '{date_created_start}'"
            if filter_query:
                url = f"{url} AND {date_filter}"
            else:
                url = f"{url}&$filter='{date_filter}'"
            logger.info(f"Using date filter: {date_filter}")

        logger.info(f"Full request URL: {url}")

        # Make the request with error handling for filter failures
        try:
            response = self.session.get(url)

            # Check for filter-related errors
            if response.status_code != 200 and "$filter" in url:
                logger.warning(
                    f"Request failed with status code {response.status_code}. This might be a filter error.",
                )
                logger.warning(f"Response text: {response.text[:200]}...")
                logger.warning("Attempting to retry without filter...")

                # Remove the filter and try again
                base_url = url.split("&$filter=")[0]
                logger.info(
                    f"Retrying request without filter: {base_url}",
                )
                response = self.session.get(base_url)
        except Exception as e:
            logger.error(f"API request failed: {e!s}")
            raise

        # Check for successful response
        if response.status_code != 200:
            raise Exception(
                f"API request failed with status code {response.status_code}: {response.text}",
            )

        # Parse the response
        data = response.json()

        # Debug response structure
        logger.info(
            f"Response structure: {list(data.keys()) if isinstance(data, dict) else type(data)}",
        )
        logger.info(f"Response data: {str(data)[:500]}...")

        # Convert to DataFrame
        if "value" in data and isinstance(data["value"], list):
            df = pd.DataFrame(data["value"])
            logger.info(f"Retrieved {len(df)} records")
            return df
        logger.warning("Response does not contain expected 'value' list")
        if "__ENTITIES" in data and isinstance(data["__ENTITIES"], list):
            df = pd.DataFrame(data["__ENTITIES"])
            logger.info(f"Retrieved {len(df)} records from __ENTITIES")
            return df
        if isinstance(data, list):
            df = pd.DataFrame(data)
            logger.info(f"Retrieved {len(df)} records from direct list response")
            return df
        if isinstance(data, dict) and len(data) > 0:
            try:
                df = pd.DataFrame([data])
                logger.info("Retrieved 1 record from direct dict response")
                return df
            except Exception as e:
                logger.warning(f"Failed to convert response dict to DataFrame: {e}")
                logger.warning(f"Response keys: {list(data.keys())}")

        return pd.DataFrame()

    def _fetch_all_records(
        self,
        url: str,
        filter_query: Optional[str] = None,
        new_data_only: bool = True,
        date_created_start: Optional[str] = None,
    ) -> pd.DataFrame:
        """Fetch all records from a table using pagination."""
        params = {"$top": 1000, "$skip": 0}

        # Handle filter query with the correct syntax
        if filter_query:
            # If filter query is already in the correct format (starts with &$filter=), use as is
            if not filter_query.startswith("&$filter="):
                # Extract the field name and value from the filter query
                parts = filter_query.split(' ')
                if len(parts) >= 3:
                    field = parts[0]
                    operator = parts[1]
                    value = parts[2]
                    # Construct the filter in the exact format required
                    filter_query = f"&$filter='{field} {operator} '{value}''"
            url = f"{url}{filter_query}"
            logger.info(f"Using filter query: {filter_query}")

        # Handle date filtering
        if new_data_only and date_created_start:
            date_filter = f"CREATIONDATE ge '{date_created_start}'"
            if filter_query:
                params["$filter"] = f'"{filter_query} AND {date_filter}"'
            else:
                params["$filter"] = f'"{date_filter}"'
            logger.info(f"Using date filter: {date_filter}")

        # Fetch data using pagination
        all_data = []
        total_fetched = 0
        retry_count = 0
        max_retries = 3
        filter_error_detected = False

        while True:
            self.session.cookies.clear()
            if not self.session_id:
                logger.error("No session ID available for paginated request")
                raise Exception("No valid session ID available")

            self.session.cookies.set("WASID4D", self.session_id)
            if retry_count > 0:
                logger.info(
                    f"Reset to single session cookie for retry attempt {retry_count}",
                )

            # Make the request with error handling for filter failures
            logger.info(f"Making paginated request: {url} with params: {params}")
            try:
                current_params = params.copy()
                if filter_error_detected and "$filter" in current_params:
                    logger.info(
                        "Filter error previously detected, removing filter for this request",
                    )
                    current_params.pop("$filter", None)

                response = self.session.get(url, params=current_params)

                # Check for filter-related errors
                if (
                    response.status_code != 200
                    and "$filter" in current_params
                    and not filter_error_detected
                ):
                    logger.warning(
                        f"Request failed with status code {response.status_code}. This might be a filter error.",
                    )
                    logger.warning(f"Response text: {response.text[:200]}...")
                    logger.warning("Attempting to retry without filter...")

                    # Remove the filter and try again
                    current_params.pop("$filter", None)
                    logger.info(
                        f"Retrying request without filter: {url} with params: {current_params}",
                    )
                    response = self.session.get(url, params=current_params)

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
                                "Maximum sessions error detected. Attempting to login with a new session...",
                            )
                            self.session.cookies.clear()
                            if self.login():
                                retry_count += 1
                                logger.info(
                                    f"Re-login successful. Retrying request (attempt {retry_count}/{max_retries})",
                                )
                                continue
                        error_msg += (
                            ": Maximum number of sessions reached and retry failed"
                        )

                    error_msg += f": {response.text}"
                    raise Exception(error_msg)

                # Check for new session cookie in response and update if found
                for cookie in response.cookies:
                    if cookie.name == "WASID4D" and cookie.value != self.session_id:
                        logger.info(
                            "Received new session cookie in paginated response, updating...",
                        )
                        self.session_id = cookie.value
                        self.save_session_cookie()
                        self.session.cookies.clear()
                        self.session.cookies.set("WASID4D", self.session_id)
                        break

                # Parse the response
                data = response.json()

                # Debug first request response
                if total_fetched == 0:
                    logger.info(
                        f"First response structure: {list(data.keys()) if isinstance(data, dict) else type(data)}",
                    )
                    logger.info(f"First response sample: {str(data)[:500]}...")

                # Extract the records based on the actual response structure
                if "value" in data and isinstance(data["value"], list):
                    records = data["value"]
                    all_data.extend(records)
                    total_fetched += len(records)
                    logger.info(
                        f"Fetched {len(records)} records (total: {total_fetched})",
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
                        f"Fetched {len(records)} records from __ENTITIES (total: {total_fetched})",
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
                        f"Fetched {len(data)} records from direct list response (total: {total_fetched})",
                    )
                    break
                else:
                    logger.warning("Response does not contain expected data format")
                    logger.warning(
                        f"Response keys: {list(data.keys()) if isinstance(data, dict) else 'not a dict'}",
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
        return df 