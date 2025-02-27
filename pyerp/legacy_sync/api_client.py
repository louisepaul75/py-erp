"""
API client for interacting with the legacy 4D-based ERP system.

This module provides a wrapper around the WSZ_api package to fetch data from
and push data to the legacy system.
"""

import os
import sys
import logging
import datetime
from typing import Dict, List, Optional, Any, Union
import pandas as pd

# Configure logging
logger = logging.getLogger(__name__)

# Add the WSZ_api package to the Python path
WSZ_API_PATH = r'C:\Users\Joan-Admin\PycharmProjects\WSZ_api'
if WSZ_API_PATH not in sys.path:
    sys.path.append(WSZ_API_PATH)

try:
    # Import the WSZ_api modules
    from wsz_api.getTable import fetch_data_from_api
    from wsz_api.pushField import push_field_to_api
    from wsz_api.auth import get_session_cookie
    logger.info("Successfully imported WSZ_api modules")
except ImportError as e:
    logger.error(f"Failed to import WSZ_api modules: {e}")
    raise


class LegacyAPIClient:
    """
    Client for interacting with the legacy 4D-based ERP system.
    """

    def __init__(self):
        """
        Initialize the API client.
        """
        self.session_cookie = None
        self.refresh_session()

    def refresh_session(self) -> None:
        """
        Refresh the session cookie for API authentication.
        """
        try:
            self.session_cookie = get_session_cookie(mode='live')
            logger.info("Successfully refreshed session cookie")
        except Exception as e:
            logger.error(f"Failed to refresh session cookie: {e}")
            raise

    def fetch_table(
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
            new_data_only: If True, fetch only records with modified_date > threshold.
            date_created_start: Optional start date for filtering by creation date.

        Returns:
            A pandas DataFrame containing the fetched data.
        """
        try:
            df = fetch_data_from_api(
                table_name=table_name,
                top=top,
                skip=skip,
                new_data_only=new_data_only,
                date_created_start=date_created_start
            )
            logger.info(f"Successfully fetched {len(df)} records from {table_name}")
            return df
        except Exception as e:
            logger.error(f"Failed to fetch data from {table_name}: {e}")
            raise

    def push_field(
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
        """
        try:
            result = push_field_to_api(
                table_name=table_name,
                record_id=record_id,
                field_name=field_name,
                field_value=field_value
            )
            logger.info(f"Successfully pushed {field_name}={field_value} to {table_name}/{record_id}")
            return result
        except Exception as e:
            logger.error(f"Failed to push {field_name}={field_value} to {table_name}/{record_id}: {e}")
            raise


# Create a singleton instance of the API client
api_client = LegacyAPIClient() 