"""
API client for interacting with the legacy 4D-based ERP system.

This module provides a wrapper for interacting with the legacy system,
originally using the WSZ_api package but now using our direct_api implementation.  # noqa: E501
"""

import os  # noqa: F401
import sys
import logging
import datetime
from typing import Dict, List, Optional, Any, Union  # noqa: F401
import pandas as pd  # noqa: F401

# Configure logging
logger = logging.getLogger(__name__)

# Import from our new direct_api module
try:
    from pyerp.direct_api.client import DirectAPIClient
    from pyerp.direct_api.auth import get_session  # noqa: F401
    from pyerp.direct_api.exceptions import DirectAPIError, ServerUnavailableError, ResponseError  # noqa: E501
    logger.info("Successfully imported direct_api modules")
except ImportError as e:
    logger.error(f"Failed to import direct_api modules: {e}")

    # Fall back to WSZ_api if direct_api is not available
    logger.warning("Falling back to WSZ_api package")

    # Add the WSZ_api package to the Python path
    WSZ_API_PATH = r'C:\Users\Joan-Admin\PycharmProjects\WSZ_api'
    if WSZ_API_PATH not in sys.path:
        sys.path.append(WSZ_API_PATH)

    try:
        # Import the WSZ_api modules
        from wsz_api.getTable import fetch_data_from_api
        from wsz_api.pushField import push_data
        from wsz_api.auth import get_session_cookie
        logger.info("Successfully imported WSZ_api modules as fallback")
    except ImportError as e:
        logger.error(f"Failed to import WSZ_api modules: {e}")
        raise


class LegacyAPIClient:
    """
    Client for interacting with the legacy 4D-based ERP system.
    """

    def __init__(self) -> None:
        """
        Initialize the API client.
        """
        self.session_cookie = None
        self.direct_client = None
        self.server_available = True
        self.last_availability_check = datetime.datetime.now()
        self.availability_check_interval = datetime.timedelta(minutes=5)  # Check every 5 minutes  # noqa: E501

        try:
            # Try to use DirectAPIClient
            self.direct_client = DirectAPIClient()
            logger.info("Using DirectAPIClient for legacy API interactions")
        except Exception as e:
            logger.warning(f"Failed to initialize DirectAPIClient: {e}")
            logger.info("Using WSZ_api for legacy API interactions")

        try:
            self.refresh_session()
        except (ServerUnavailableError, ResponseError) as e:
            # Handle initialization errors gracefully
            logger.error(f"Could not establish initial connection to legacy ERP: {e}")  # noqa: E501
            self.server_available = False
            self.last_availability_check = datetime.datetime.now()

    def refresh_session(self) -> None:
        """
        Refresh the session cookie for API authentication.
        """
        if not self.server_available:
            # Check if we should try again based on the time interval
            time_since_last_check = datetime.datetime.now() - self.last_availability_check  # noqa: E501
            if time_since_last_check < self.availability_check_interval:
                logger.warning("Server was previously unavailable, skipping refresh_session")  # noqa: E501
                return

        try:
            if self.direct_client:
                # Use DirectAPIClient session management
                self.session_cookie = self.direct_client._get_session().get_cookie()  # noqa: E501
            else:
                # Fall back to WSZ_api
                self.session_cookie = get_session_cookie(mode='live')
  # noqa: F841

            logger.info("Successfully refreshed session cookie")
            self.server_available = True
        except (ServerUnavailableError, ResponseError) as e:
            logger.error(f"Server is unavailable during session refresh: {e}")
            self.server_available = False
            self.last_availability_check = datetime.datetime.now()
            # Don't raise the exception, just mark the server as unavailable
        except Exception as e:
            logger.error(f"Failed to refresh session cookie: {e}")
            raise

    def fetch_table(
  # noqa: E128

        self,
        table_name: str,
        top: int = 100,
        skip: int = 0,
        new_data_only: bool = True,
        date_created_start: Optional[str] = None
    ) -> pd.DataFrame:
        """
        Fetch data from a table in the legacy system.

        Args:
            table_name: The name of the table to fetch data from.
            top: The number of records to fetch per API call (pagination).
            skip: The number of records to skip (for pagination).
            new_data_only: If True, fetch only records with modified_date > threshold.  # noqa: E501
            date_created_start: Optional start date for filtering by creation date.  # noqa: E501

        Returns:
            A pandas DataFrame containing the fetched data.

        Raises:
            ServerUnavailableError: If the server is unavailable and cannot be reached  # noqa: E501
            Exception: For other errors during data fetching
        """
        if not self.server_available:
            # Check if we should try again based on the time interval
            time_since_last_check = datetime.datetime.now() - self.last_availability_check  # noqa: E501
            if time_since_last_check < self.availability_check_interval:
                logger.warning(f"Server is currently unavailable, skipping fetch_table for {table_name}")  # noqa: E501
                return pd.DataFrame()  # Return empty DataFrame instead of raising an exception  # noqa: E501

        try:
            if self.direct_client:
                # Use DirectAPIClient
                df = self.direct_client.fetch_table(
                    table_name=table_name,  # noqa: E128
                    top=top,
                    skip=skip,
                    new_data_only=new_data_only,
                    date_created_start=date_created_start
                )
            else:
                # Fall back to WSZ_api
                # Convert date_created_start to datetime if it's a string
                date_created_param = date_created_start
                if isinstance(date_created_start, str):
                    date_created_param = datetime.datetime.fromisoformat(date_created_start)  # noqa: E501

                df = fetch_data_from_api(
                    table_name=table_name,  # noqa: E128
                    top=top,
  # noqa: F841
                    skip=skip,
                    new_data_only=new_data_only,
  # noqa: F841
                    date_created_start=date_created_param
  # noqa: F841
                )

            logger.info(f"Successfully fetched {len(df)} records from {table_name}")  # noqa: E501
            self.server_available = True
            return df
        except ServerUnavailableError as e:
            logger.error(f"Server is unavailable during fetch_table for {table_name}: {e}")  # noqa: E501
            self.server_available = False
            self.last_availability_check = datetime.datetime.now()
            return pd.DataFrame()  # Return empty DataFrame instead of raising an exception  # noqa: E501
        except Exception as e:
            logger.error(f"Failed to fetch data from {table_name}: {e}")
            raise

    def push_field(
  # noqa: E128

        self,
        table_name: str,
        record_id: Union[int, str],
        field_name: str,
        field_value: Any
    ) -> bool:
        """
        Push a field value to the legacy system.

        Args:
            table_name: The name of the table to update.
            record_id: The ID of the record to update.
            field_name: The name of the field to update.
            field_value: The new value for the field.

        Returns:
            True if the update was successful, False otherwise.

        Raises:
            ServerUnavailableError: If the server is unavailable and cannot be reached  # noqa: E501
            Exception: For other errors during data pushing
        """
        if not self.server_available:
            # Check if we should try again based on the time interval
            time_since_last_check = datetime.datetime.now() - self.last_availability_check  # noqa: E501
            if time_since_last_check < self.availability_check_interval:
                logger.warning(f"Server is currently unavailable, skipping push_field to {table_name}")  # noqa: E501
                return False  # Return False instead of raising an exception

        try:
            if self.direct_client:
                # Use DirectAPIClient
                result = self.direct_client.push_field(
                    table_name=table_name,  # noqa: E128
                    record_id=record_id,
                    field_name=field_name,
                    field_value=field_value
                )
            else:
                # Fall back to WSZ_api
                result = push_data(
                    table=table_name,  # noqa: E128
                    column=field_name,  # noqa: F841
  # noqa: F841
                    key=record_id,  # noqa: F841
  # noqa: F841
                    value=field_value  # noqa: F841
                )

            logger.info(f"Successfully pushed {field_name}={field_value} to {table_name}/{record_id}")  # noqa: E501
            self.server_available = True
            return result
        except ServerUnavailableError as e:
            logger.error(f"Server is unavailable during push_field to {table_name}: {e}")  # noqa: E501
            self.server_available = False
            self.last_availability_check = datetime.datetime.now()
            return False  # Return False instead of raising an exception
        except Exception as e:
            logger.error(f"Failed to push {field_name}={field_value} to {table_name}/{record_id}: {e}")  # noqa: E501
            raise

    def fetch_record(
  # noqa: E128

        self,
        table_name: str,
        record_id: Union[int, str]
    ) -> Dict[str, Any]:
        """
        Fetch a single record from the legacy system.

        Args:
            table_name: The name of the table to fetch from.
            record_id: The ID of the record to fetch.

        Returns:
            A dictionary containing the record data.

        Raises:
            ServerUnavailableError: If the server is unavailable and cannot be reached  # noqa: E501
            Exception: For other errors during data fetching
        """
        if not self.server_available:
            # Check if we should try again based on the time interval
            time_since_last_check = datetime.datetime.now() - self.last_availability_check  # noqa: E501
            if time_since_last_check < self.availability_check_interval:
                logger.warning(f"Server is currently unavailable, skipping fetch_record for {table_name}/{record_id}")  # noqa: E501
                return {}  # Return empty dict instead of raising an exception

        try:
            if self.direct_client:
                # Use DirectAPIClient
                record = self.direct_client.fetch_record(
                    table_name=table_name,  # noqa: E128
                    record_id=record_id
                )
            else:
                # Fall back to a workaround using WSZ_api
                from wsz_api.getRecord import get_record
                record = get_record(table_name, record_id)

            logger.info(f"Successfully fetched record {table_name}/{record_id}")  # noqa: E501
            self.server_available = True
            return record
        except ServerUnavailableError as e:
            logger.error(f"Server is unavailable during fetch_record for {table_name}/{record_id}: {e}")  # noqa: E501
            self.server_available = False
  # noqa: F841
            self.last_availability_check = datetime.datetime.now()
  # noqa: F841
            return {}  # Return empty dict instead of raising an exception
        except Exception as e:
            logger.error(f"Failed to fetch record {table_name}/{record_id}: {e}")  # noqa: E501
            raise


# Create a singleton instance of the API client
api_client = LegacyAPIClient()  # noqa: F841
  # noqa: F841
