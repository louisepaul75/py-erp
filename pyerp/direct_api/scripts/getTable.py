"""
getTable.py - Simplified script to fetch tables from the legacy ERP system

This script provides a command-line interface to fetch data from any table
in the legacy ERP system using the direct_api module with simplified session management.  # noqa: E501

Usage:
    python getTable.py [table_name] [options]

Options:
    --env ENV             Environment to use (default: live)
    --top N               Number of records to fetch (default: 100)
    --skip N              Number of records to skip (default: 0)
    --all                 Fetch all records (overrides --top and --skip)
    --filter FILTER       Filter query string
    --output FILE         Output file (CSV format, default: stdout)
    --format FORMAT       Output format (csv, json, excel, default: csv)
    --verbose             Enable verbose output
"""

import argparse
import json
import logging
import os
import sys
from datetime import datetime
from pathlib import Path

import django
import pandas as pd
import requests

# Add the parent directory to the path so we can import the direct_api module
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent.parent))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger(__name__)

# Global constants
DIRECT_API_ROOT = Path(__file__).resolve().parent.parent
COOKIE_FILE_PATH = os.path.join(str(DIRECT_API_ROOT), ".global_session_cookie")

# Set up Django environment only when run as a script, not when imported
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "pyerp.settings")

# Import after Django setup (no need to setup Django when imported
# since it will already be set up)
try:
    from pyerp.direct_api.settings import API_ENVIRONMENTS

    logger.info(f"Available environments: {list(API_ENVIRONMENTS.keys())}")
except ImportError as e:
    logger.error(f"Failed to import API_ENVIRONMENTS: {e}")
    logger.error("Make sure the settings module is available and correctly configured")
    sys.exit(1)


class SimpleAPIClient:
    """Simple API client with built-in session management."""

    def __init__(self, environment="live"):
        """Initialize the client with the specified environment."""
        if environment not in API_ENVIRONMENTS:
            available_envs = list(API_ENVIRONMENTS.keys())
            logger.error(
                f"Invalid environment: '{environment}'. Available environments: {available_envs}",
            )
            raise ValueError(
                f"Invalid environment: '{environment}'. Available: {available_envs}",
            )

        self.environment = environment

        # Check if URL is properly configured in settings
        if "base_url" not in API_ENVIRONMENTS[environment]:
            logger.error(f"Missing URL configuration for environment '{environment}'")
            logger.error(
                f"API_ENVIRONMENTS['{environment}']: {API_ENVIRONMENTS[environment]}",
            )
            raise KeyError(f"Missing 'base_url' in API_ENVIRONMENTS['{environment}']")

        self.base_url = API_ENVIRONMENTS[environment]["base_url"]
        logger.info(f"Using API URL: {self.base_url}")

        self.session = requests.Session()
        self.session_id = None  # Store just the session ID value
        self.load_session_cookie()

    def __del__(self):
        """Destructor to ensure sessions are cleaned up."""

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

                    # Provide safe version of cookie for logging
                    safe_id = (
                        f"{self.session_id[:5]}...{self.session_id[-5:]}"
                        if len(self.session_id) > 10
                        else self.session_id
                    )
                    logger.info(f"Loaded session ID from {COOKIE_FILE_PATH}")
                    logger.info(f"Set cookie: WASID4D={safe_id}")
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
        for name, value in cookies.items():
            safe_value = f"{value[:5]}...{value[-5:]}" if len(value) > 10 else value
            logger.info(f"  - {name}={safe_value}")

    def _log_response_cookies(self, response, prefix="Response cookies"):
        """Log cookies received in a response."""
        if not response.cookies:
            logger.info(f"{prefix}: No cookies")
            return

        cookies = response.cookies.get_dict()
        logger.info(f"{prefix}: {len(cookies)} cookie(s)")
        for name, value in cookies.items():
            safe_value = f"{value[:5]}...{value[-5:]}" if len(value) > 10 else value
            logger.info(f"  - {name}={safe_value}")

        # Also check Set-Cookie header which might contain additional metadata
        if "Set-Cookie" in response.headers:
            logger.info(
                f"Raw Set-Cookie header: {response.headers['Set-Cookie'][:100]}...",
            )

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
                        logger.info(
                            f"Found new session cookie in response: {cookie.name}",
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
                        "Set single new cookie WASID4D with value from response",
                    )

                    # Save the updated cookie
                    self.save_session_cookie()
                else:
                    logger.info("No new session cookie received, keeping existing one")
                    if self.session_id and not self.session.cookies.get("WASID4D"):
                        logger.info("Re-adding existing session cookie")
                        self.session.cookies.clear()
                        self.session.cookies.set("WASID4D", self.session_id)

                return True
            logger.warning(f"Session validation failed: {response.status_code}")
            if response.text:
                logger.warning(f"Response text: {response.text[:200]}...")
            return False
        except Exception as e:
            logger.warning(f"Session validation failed with exception: {e}")
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
        table_name,
        top=100,
        skip=0,
        all_records=False,
        filter_query=None,
        new_data_only=True,
        date_created_start=None,
    ):
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
        params = {"$top": top, "$skip": skip}

        # Handle filter query with the correct syntax (quoted filter expression)
        if filter_query:
            params["$filter"] = f'"{filter_query}"'
            logger.info(f"Using filter query: {filter_query}")

        # Handle date filtering
        if new_data_only and date_created_start:
            date_filter = f"CREATIONDATE ge '{date_created_start}'"
            if filter_query:
                params["$filter"] = f'"{filter_query} AND {date_filter}"'
            else:
                params["$filter"] = f'"{date_filter}"'
            logger.info(f"Using date filter: {date_filter}")

        logger.info(f"Fetching up to {top} records from {table_name} (skip: {skip})")
        logger.info(f"Full request URL: {url} with params: {params}")

        # Make the request with error handling for filter failures
        try:
            response = self.session.get(url, params=params)

            # Check for filter-related errors
            if response.status_code != 200 and "$filter" in params:
                logger.warning(
                    f"Request failed with status code {response.status_code}. This might be a filter error.",
                )
                logger.warning(f"Response text: {response.text[:200]}...")
                logger.warning("Attempting to retry without filter...")

                # Remove the filter and try again
                params_without_filter = params.copy()
                params_without_filter.pop("$filter", None)
                logger.info(
                    f"Retrying request without filter: {url} with params: {params_without_filter}",
                )
                response = self.session.get(url, params=params_without_filter)
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
        url,
        filter_query=None,
        new_data_only=True,
        date_created_start=None,
    ):
        """Fetch all records from a table using pagination."""
        params = {"$top": 1000, "$skip": 0}

        # Handle filter query with the correct syntax (quoted filter expression)
        if filter_query:
            params["$filter"] = f'"{filter_query}"'
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


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Fetch data from a table in the legacy ERP system",
    )

    parser.add_argument(
        "table_name",
        nargs="?",
        default=None,
        help="Name of the table to fetch data from",
    )

    parser.add_argument(
        "--env",
        default="live",
        help="Environment to use (default: live)",
    )

    parser.add_argument(
        "--top",
        type=int,
        default=100,
        help="Number of records to fetch (default: 100)",
    )

    parser.add_argument(
        "--skip",
        type=int,
        default=0,
        help="Number of records to skip (default: 0)",
    )

    parser.add_argument(
        "--all",
        action="store_true",
        help="Fetch all records (overrides --top and --skip)",
    )

    parser.add_argument("--filter", dest="filter_query", help="Filter query string")

    parser.add_argument("--output", help="Output file (default: stdout)")

    parser.add_argument(
        "--format",
        choices=["csv", "json", "excel"],
        default="csv",
        help="Output format (csv, json, excel, default: csv)",
    )

    parser.add_argument("--verbose", action="store_true", help="Enable verbose output")

    return parser.parse_args()


def main():
    """Main function to execute when script is run."""
    args = parse_args()

    # Check if table_name is provided
    if not args.table_name:
        logger.error("Table name is required")
        sys.exit(1)

    # Set logging level based on verbose flag
    if args.verbose:
        logger.setLevel(logging.DEBUG)

    try:
        client = SimpleAPIClient(environment=args.env)

        # Fetch the data
        df = client.fetch_table(
            table_name=args.table_name,
            top=args.top,
            skip=args.skip,
            all_records=args.all,
            filter_query=args.filter_query,
        )

        # Save the output
        if args.output:
            output_path = Path(args.output)

            # Create directory if it doesn't exist
            output_path.parent.mkdir(parents=True, exist_ok=True)

            # Save to file in the specified format
            if args.format == "csv":
                df.to_csv(output_path, index=False)
            elif args.format == "json":
                df.to_json(output_path, orient="records", indent=2)
            elif args.format == "excel":
                df.to_excel(output_path, index=False)

            logger.info(f"Data saved to {output_path}")
        else:
            # Print number of records and a sample of the DataFrame
            print(f"\nFetched {len(df)} records from '{args.table_name}'")
            print("\nDataFrame Preview:")
            print(df.tail())

        return df
    except Exception as e:
        logger.error(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    # Django setup should only happen when the script is run directly
    import django

    django.setup()

    table = "Artikel_Variante"

    # First run validation script if no arguments provided
    if len(sys.argv) == 1:
        print("\n=== Running Session Validation ===")
        try:
            client = SimpleAPIClient()

            # Check current cookie file
            print("\nChecking session cookie file...")
            if os.path.exists(COOKIE_FILE_PATH):
                with open(COOKIE_FILE_PATH) as f:
                    cookie_data = json.load(f)
                    print(f"Found cookie file at: {COOKIE_FILE_PATH}")
                    print(f"Cookie name: {cookie_data.get('name', 'Not specified')}")
                    value = cookie_data.get("value", "")
                    safe_value = (
                        f"{value[:5]}...{value[-5:]}" if len(value) > 10 else value
                    )
                    print(f"Cookie value: {safe_value}")
                    print(
                        f"Created at: {cookie_data.get('created_at', 'Not specified')}"
                    )
            else:
                print("No existing cookie file found")

            # Validate session
            print("\nValidating session...")
            if client.validate_session():
                print("✓ Session validation successful")
                print("\nCurrent session cookies:")
                client._log_cookies()
            else:
                print("✗ Session validation failed, attempting login...")
                if client.login():
                    print("✓ Login successful")
                    print("\nNew session cookies:")
                    client._log_cookies()
                else:
                    print("✗ Login failed")
                    sys.exit(1)

            # Try to fetch a small sample from a known table
            print("\nTesting table fetch...")
            try:
                df = client.fetch_table(table, top=1)
                print(f"✓ Successfully fetched sample from Kunden ({len(df)} records)")
                if not df.empty:
                    print("\nSample data:")
                    print(df.head())
            except Exception as e:
                print(f"✗ Failed to fetch sample table: {e}")

        except Exception as e:
            print(f"✗ Validation failed: {e}")
            sys.exit(1)
    else:
        # Run normal table fetch with provided arguments
        main()
