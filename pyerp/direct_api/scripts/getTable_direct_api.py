"""
getTable_direct_api.py - Script to fetch tables from the legacy ERP system using direct_api module  # noqa: E501

This script provides a command-line interface to fetch data from any table
in the legacy ERP system using the official direct_api module.

Usage:
    python getTable_direct_api.py [table_name] [options]

Options:
    --env ENV             Environment to use (default: live)
    --top N               Number of records to fetch (default: 100)
    --skip N              Number of records to skip (default: 0)
    --all                 Fetch all records (overrides --top and --skip)
    --filter FILTER       Filter query string
    --output FILE         Output file (CSV format, default: stdout)
    --format FORMAT       Output format (csv, json, excel, default: csv)
    --verbose             Enable verbose output
    --debug               Run in debug mode to test session management
"""

import os
import sys
import argparse
import logging
import json
import pandas as pd  # noqa: F401
from datetime import datetime
from pathlib import Path
import requests
from urllib.parse import urljoin  # noqa: F401
import time

 # Add the parent directory to the path so we can import the direct_api module
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent.parent))

 # Configure logging
logging.basicConfig(
    level=logging.INFO,  # noqa: E128
    format='%(asctime)s - %(levelname)s - %(message)s',  # noqa: F841
    handlers=[logging.StreamHandler(sys.stdout)]  # noqa: F841
)
logger = logging.getLogger(__name__)

 # Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pyerp.settings')
import django
django.setup()

 # Import the direct_api module
try:
    from pyerp.direct_api.client import DirectAPIClient
    from pyerp.direct_api.exceptions import DirectAPIError
    from pyerp.direct_api.settings import API_ENVIRONMENTS
    from pyerp.direct_api.auth import (
        get_session,  # noqa: E128
        invalidate_session,
        set_session_limit_reached,
        is_session_limit_reached
    )
    logger.info(f"Available environments: {list(API_ENVIRONMENTS.keys())}")
except ImportError as e:
    logger.error(f"Failed to import direct_api module: {e}")
    logger.error("Make sure the direct_api module is available and correctly configured")  # noqa: E501
    sys.exit(1)


class DirectAPIClientWASID(DirectAPIClient):
    """Extended client that always uses WASID4D cookie."""

    def __init__(self, environment: str = 'live', timeout: int = None):

        """Initialize with additional session cookie handling."""
        super().__init__(environment, timeout)
        self.cookie_file = os.path.join(os.path.dirname(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'auth.py'))),  # noqa: E501
            '.global_session_cookie')
        self.session_id = None
        self.session_created_at = None
        self.load_session_cookie()

    def load_session_cookie(self):
        """Load session cookie value directly from file."""
        if not os.path.exists(self.cookie_file):
            logger.info("No session cookie file found")
            return False

        try:
            with open(self.cookie_file, 'r') as f:
                cookie_data = json.load(f)

                if 'value' in cookie_data:
                    self.session_id = cookie_data['value']

 # Store created_at time if available
                    if 'created_at' in cookie_data:
                        try:
                            self.session_created_at = datetime.fromisoformat(cookie_data['created_at'])  # noqa: E501
                        except (ValueError, TypeError):
                            self.session_created_at = datetime.now()
                    else:
                        self.session_created_at = datetime.now()

                    logger.info(f"Loaded session ID from {self.cookie_file}")
                    logger.debug(f"Session created at: {self.session_created_at}")  # noqa: E501
                    return True
                else:
                    logger.warning("Cookie file has invalid format (missing 'value' field)")  # noqa: E501
                    return False

        except Exception as e:
            logger.warning(f"Failed to load session cookie: {e}")
            return False

    def invalidate_and_reload_cookie(self):
        """Invalidate the current session and load a new cookie."""
        if is_session_limit_reached():
            logger.warning("Not invalidating session because the global session limit has been reached")  # noqa: E501
            return False

        old_session_id = self.session_id

 # Call the invalidate_session function to clear the session
        invalidate_session(self.environment)

 # Wait a moment for the server to register the session invalidation
        time.sleep(2)

 # Clear our cached session ID
        self.session_id = None
        self.session_created_at = None

 # Load a new cookie
        success = self.load_session_cookie()

 # Check if the session ID actually changed
        if success and old_session_id == self.session_id:
            logger.warning("Session ID did not change after invalidation - server may be limiting sessions")  # noqa: E501
            return False

        return success

    def _make_request(

        self,  # noqa: E128
        method,
        endpoint,
        params=None,
        data=None,
        headers=None
    ):
        """
        Override the _make_request method to always use WASID4D cookie,
        reading directly from the cookie file.
        """
        if is_session_limit_reached():
            error_msg = "Cannot make API request because the global session limit has been reached (402 error)"  # noqa: E501
            logger.error(error_msg)
            raise DirectAPIError(error_msg)

        url = self._build_url(endpoint)

 # Try to ensure we have a valid session ID
        if not self.session_id:
            if not self.load_session_cookie():
                if not is_session_limit_reached():
                    try:
                        session = get_session(self.environment)
                        session.ensure_valid()  # Make sure the session is valid  # noqa: E501
                        self.session_id = session.get_cookie()  # Store for future use  # noqa: E501
                        self.session_created_at = datetime.now()
                        logger.info("Created new session via session manager")
                    except DirectAPIError as e:
                        if "session limit" in str(e).lower() or "402" in str(e):  # noqa: E501
                            set_session_limit_reached(True)
                            error_msg = f"Cannot create a new session: {str(e)}"  # noqa: E501
                        else:
                            error_msg = f"Error creating session: {str(e)}"
                        logger.error(error_msg)
                        raise DirectAPIError(error_msg)
                else:
                    error_msg = "Cannot create a new session because the global session limit has been reached (402 error)"  # noqa: E501
                    logger.error(error_msg)
                    raise DirectAPIError(error_msg)

 # Always use WASID4D as the cookie name
        cookie_name = 'WASID4D'
        cookie_value = self.session_id

 # If we don't have a valid cookie value, fail the request
        if not cookie_value:
            if is_session_limit_reached():
                error_msg = "No valid session cookie available and cannot create a new session due to session limit (402 error)"  # noqa: E501
            else:
                error_msg = "No valid session cookie available"
            logger.error(error_msg)
            raise DirectAPIError(error_msg)

 # Format the cookie for the request
        cookie_header = f"{cookie_name}={cookie_value}"

 # Prepare headers
        request_headers = {
            'Cookie': cookie_header,  # noqa: E128
            'Accept': 'application/json'
        }
        if headers:
            request_headers.update(headers)

 # Log the cookie being used (truncated for security)
        logger.debug(f"Using cookie: {cookie_name}={cookie_value[:10]}...")

 # Make the request (simplified version without retry logic)
        logger.debug(f"{method} request to {url}")

        try:
            response = requests.request(
                method=method,  # noqa: E128
                url=url,
                params=params,
                json=data,
                headers=request_headers,
                timeout=self.timeout
            )

 # Check for successful response
            if 200 <= response.status_code < 300:
                return response
            else:
                error_msg = f"API request failed with status {response.status_code}"  # noqa: E501

 # If we get a 402 error, mark that we've hit the session limit globally  # noqa: E501
                if response.status_code == 402:
                    set_session_limit_reached(True)
                    error_msg = f"Too many sessions error (402): {error_msg}"

                logger.error(error_msg)
                raise DirectAPIError(error_msg)

        except requests.exceptions.RequestException as e:
            error_msg = f"Connection error: {str(e)}"
            logger.error(error_msg)
            raise DirectAPIError(error_msg)


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='Fetch data from a table in the legacy ERP system')  # noqa: E501

    parser.add_argument('table_name', nargs='?', default=None,
                        help='Name of the table to fetch data from')  # noqa: F841

    parser.add_argument('--env', default='live',
                        help='Environment to use (default: live)')  # noqa: F841

    parser.add_argument('--top', type=int, default=100,
                        help='Number of records to fetch (default: 100)')  # noqa: F841

    parser.add_argument('--skip', type=int, default=0,
                        help='Number of records to skip (default: 0)')  # noqa: F841

    parser.add_argument('--all', action='store_true',
                        help='Fetch all records (overrides --top and --skip)')  # noqa: F841

    parser.add_argument('--filter', dest='filter_query',
                        help='Filter query string')  # noqa: F841

    parser.add_argument('--output',
                        help='Output file (default: stdout)')  # noqa: F841

    parser.add_argument('--format', choices=['csv', 'json', 'excel'], default='csv',  # noqa: E501
                        help='Output format (csv, json, excel, default: csv)')  # noqa: F841

    parser.add_argument('--verbose', action='store_true',
                        help='Enable verbose output')  # noqa: F841

    parser.add_argument('--debug', action='store_true',
                        help='Run in debug mode to test session management')  # noqa: F841

    return parser.parse_args()


def main():
    """Main function to execute when script is run."""
    args = parse_args()


    args.table_name = 'Kunden'

 # Check if table_name is provided
    if not args.table_name:
        logger.error("Table name is required")
        sys.exit(1)

 # Set logging level based on verbose flag
    if args.verbose:
        logger.setLevel(logging.DEBUG)
        logging.getLogger('pyerp.direct_api').setLevel(logging.DEBUG)

    try:
        client = DirectAPIClientWASID(environment=args.env)

 # Determine whether to fetch all records
        if args.all:
            logger.info(f"Fetching all records from '{args.table_name}'")
            df = fetch_all_records(client, args.table_name, args.filter_query)
        else:
            logger.info(f"Fetching up to {args.top} records from '{args.table_name}' (skip: {args.skip})")  # noqa: E501
            df = client.fetch_table(
                table_name=args.table_name,  # noqa: E128
                top=args.top,
                skip=args.skip,
                filter_query=args.filter_query
            )

 # Save the output
        if args.output:
            output_path = Path(args.output)

 # Create directory if it doesn't exist
            output_path.parent.mkdir(parents=True, exist_ok=True)

 # Save to file in the specified format
            if args.format == 'csv':
                df.to_csv(output_path, index=False)
            elif args.format == 'json':
                df.to_json(output_path, orient='records', indent=2)
            elif args.format == 'excel':
                df.to_excel(output_path, index=False)

            logger.info(f"Data saved to {output_path}")
        else:
            pd.set_option('display.max_rows', 20)  # Limit rows to avoid huge output  # noqa: E501
            pd.set_option('display.max_columns', None)  # Show all columns
            pd.set_option('display.width', None)  # Auto-detect width
            pd.set_option('display.expand_frame_repr', False)  # Don't wrap to multiple lines  # noqa: E501

 # Print number of records and a sample of the DataFrame
            print(f"\nFetched {len(df)} records from '{args.table_name}'")
            print("\nDataFrame Preview:")
            print(df.head())

        return df
    except DirectAPIError as e:
        logger.error(f"DirectAPI Error: {e}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Error: {e}")
        sys.exit(1)


def fetch_all_records(client, table_name, filter_query=None):
    """
    Fetch all records from a table using pagination.

    Args:
        client: DirectAPIClient instance
        table_name: Name of the table to fetch
        filter_query: Optional filter query string

    Returns:
        pandas.DataFrame: All records from the table
    """
    top = 1000  # Fetch in chunks of 1000 records
    skip = 0
    all_data = []

 # Session management - IMPORTANT CONSTANTS
    max_retries = 5  # Increased max retries
    retry_count = 0
    max_wait_time = 120  # Increased max wait time

 # Track when a 402 error occurs for a specific skip value
    problematic_skip_values = set()

 # Keep track of the current session ID to detect changes
    current_session_id = client.session_id  # noqa: F841

 # Store the last successful skip value for reporting
    last_successful_skip = 0

 # Log total records expected if available
    logger.info(f"Starting data fetch from table {table_name}")

    try:
        while True:
            if is_session_limit_reached():
                logger.warning("Stopping data fetch because the global session limit has been reached")  # noqa: E501
                break

            try:
                if skip in problematic_skip_values:
                    logger.warning(f"Skipping problematic offset {skip} that consistently returns 402 errors")  # noqa: E501
                    skip += top
                    continue

 # Fetch a chunk of data
                logger.info(f"Fetching records {skip} to {skip+top-1}")
                chunk = client.fetch_table(
                    table_name=table_name,  # noqa: E128
                    top=top,
                    skip=skip,
                    filter_query=filter_query
                )

 # Check if we got any data
                if chunk.empty:
                    logger.info("No more records available")
                    break

 # Add the chunk to our collection
                all_data.append(chunk)
                logger.info(f"Retrieved {len(chunk)} records")

 # Update last successful skip
                last_successful_skip = skip

 # Check if we received fewer records than requested (end of data)  # noqa: E501
                if len(chunk) < top:
                    logger.info("Reached end of data")
                    break

 # Update skip for next chunk
                skip += top

 # Reset retry counter after successful request
                retry_count = 0

            except DirectAPIError as e:
                error_str = str(e)

 # Check if this is a "too many sessions" error (status code 402)  # noqa: E501
                if "402" in error_str or "session limit" in error_str.lower():
                    logger.warning(f"Received 402 error (too many sessions) at offset {skip}")  # noqa: E501

 # Set the global session limit flag
                    set_session_limit_reached(True)
                    logger.warning("Hit session limit - will not create any new sessions (global flag set)")  # noqa: E501

 # If we've already fetched a significant number of records, stop and return what we have  # noqa: E501
                    if len(all_data) > 0:
                        logger.warning(f"We've already collected {sum(len(df) for df in all_data)} records. "  # noqa: E501
                                      "Stopping to avoid creating more sessions.")  # noqa: E501
                        break

                    if retry_count < max_retries:
                        retry_count += 1

 # Use exponential backoff with a cap, but start with a higher base wait time  # noqa: E501
                        wait_time = min(30 * (2 ** retry_count), max_wait_time)
                        logger.warning(f"Too many sessions error detected. Waiting {wait_time} seconds before retry {retry_count}/{max_retries}")  # noqa: E501
                        time.sleep(wait_time)

 # Don't update skip - retry the same range
                        continue
                    else:
                        logger.error(f"Failed to fetch data after {max_retries} retries at offset {skip} - too many sessions")  # noqa: E501
                        problematic_skip_values.add(skip)

 # Consider stopping entirely if we can't make progress
                        if not all_data:
                            logger.error("Unable to fetch any data due to session limits. Exiting.")  # noqa: E501
                            break

 # Move to the next chunk
                        skip += top
                        retry_count = 0
                        continue
                else:
                    if retry_count < max_retries:
                        retry_count += 1
                        wait_time = 5 * (2 ** retry_count)  # Increased base wait time: 10, 20, 40 seconds...  # noqa: E501
                        logger.warning(f"Error: {error_str}. Retrying in {wait_time} seconds (attempt {retry_count}/{max_retries})")  # noqa: E501
                        time.sleep(wait_time)
                        continue
                    else:
                        raise
    except Exception as e:
        logger.error(f"Error during data fetch: {e}")
        if len(all_data) > 0:
            logger.warning(f"Returning {sum(len(df) for df in all_data)} records that were successfully fetched before the error")  # noqa: E501
        else:
            raise

 # Combine all chunks into a single DataFrame
    if all_data:
        result = pd.concat(all_data, ignore_index=True)
        logger.info(f"Total records retrieved: {len(result)}")

 # Log how far we got in terms of records
        if last_successful_skip > 0:
            logger.info(f"Successfully fetched records up to offset {last_successful_skip+top-1}")  # noqa: E501

        return result
    else:
        logger.warning("No data retrieved")
        return pd.DataFrame()


def test_session_management():
    """
    Test function for session management and 402 error handling.
    This function deliberately tests the behavior when dealing with session limits.  # noqa: E501
    """
    logger.info("Running session management test...")

 # Set up logging for detailed debug information
    logger.setLevel(logging.DEBUG)
    logging.getLogger('pyerp.direct_api').setLevel(logging.DEBUG)

 # Create client for testing
    client = DirectAPIClientWASID(environment='live')
    logger.info(f"Created test client with session ID: {client.session_id[:10] if client.session_id else 'None'}")  # noqa: E501

 # Test 1: Basic fetch
    logger.info("TEST 1: Basic fetch of 10 records")
    table_name = 'Kunden'  # Using Kunden table as test
    try:
        data = client.fetch_table(table_name=table_name, top=10)
        logger.info(f"Successfully fetched {len(data)} records")
    except Exception as e:
        logger.error(f"Error during basic fetch: {e}")

 # Test 2: Check global session limit behavior
    logger.info("\nTEST 2: Testing global session limit behavior")
    logger.info("Setting global session limit flag to True...")
    set_session_limit_reached(True)

    logger.info("Attempting to fetch data with session limit flag set...")
    try:
        data = client.fetch_table(table_name=table_name, top=5)
        logger.info(f"Request succeeded despite session limit flag! Retrieved {len(data)} records")  # noqa: E501
    except Exception as e:
        logger.info(f"Received expected error when session limit is set: {e}")

 # Reset flag and confirm it works again
    logger.info("Resetting session limit flag to False...")
    set_session_limit_reached(False)

    logger.info("Attempting fetch after resetting flag...")
    try:
        data = client.fetch_table(table_name=table_name, top=5)
        logger.info(f"Successfully fetched {len(data)} records after resetting flag")  # noqa: E501
    except Exception as e:
        logger.error(f"Unexpected error after resetting flag: {e}")

 # Test 3: Test fetch_all_records with session limit handling
    logger.info("\nTEST 3: Testing fetch_all_records with forced session limit")  # noqa: E501
    logger.info("First fetching some records normally...")
    try:
        data = fetch_all_records(client, table_name, filter_query=None)
        logger.info(f"Successfully fetched {len(data)} records")
    except Exception as e:
        logger.error(f"Error during fetch_all_records: {e}")

 # Now set session limit and try again
    logger.info("Setting session limit flag and trying fetch_all_records again...")  # noqa: E501
    set_session_limit_reached(True)
    try:
        data = fetch_all_records(client, table_name, filter_query=None)
        logger.info(f"fetch_all_records with session limit returned {len(data)} records")  # noqa: E501
    except Exception as e:
        logger.info(f"Received expected error in fetch_all_records: {e}")

 # Reset flag for cleanup
    set_session_limit_reached(False)
    logger.info("Session management tests completed")


if __name__ == '__main__':
    args = parse_args()

 # Configure logging based on verbose flag
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
        logging.getLogger('pyerp.direct_api').setLevel(logging.DEBUG)

 # Run in debug mode if flag is set
    if args.debug:
        test_session_management()
    else:
        main()


