"""
API client for interacting with the legacy 4D-based ERP system.

This module provides a wrapper for interacting with the legacy system,
originally using the WSZ_api package but now using our direct_api implementation.
"""

import os
import sys
import logging
import datetime
from typing import Dict, List, Optional, Any, Union
import pandas as pd

# Configure logging
logger = logging.getLogger(__name__)

# Import from our new direct_api module
try:
    from pyerp.direct_api.client import DirectAPIClient
    from pyerp.direct_api.auth import get_session_cookie
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

    def __init__(self):
        """
        Initialize the API client.
        """
        self.session_cookie = None
        self.direct_client = None
        
        try:
            # Try to use DirectAPIClient
            self.direct_client = DirectAPIClient()
            logger.info("Using DirectAPIClient for legacy API interactions")
        except Exception as e:
            logger.warning(f"Failed to initialize DirectAPIClient: {e}")
            logger.info("Using WSZ_api for legacy API interactions")
        
        self.refresh_session()

    def refresh_session(self) -> None:
        """
        Refresh the session cookie for API authentication.
        """
        try:
            if self.direct_client:
                # Use DirectAPIClient session management
                self.session_cookie = self.direct_client._get_session().get_cookie()
            else:
                # Fall back to WSZ_api
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
            if self.direct_client:
                # Use DirectAPIClient
                df = self.direct_client.fetch_table(
                    table_name=table_name,
                    top=top,
                    skip=skip,
                    new_data_only=new_data_only,
                    date_created_start=date_created_start
                )
            else:
                # Fall back to WSZ_api
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
            if self.direct_client:
                # Use DirectAPIClient
                result = self.direct_client.push_field(
                    table_name=table_name,
                    record_id=record_id,
                    field_name=field_name,
                    field_value=field_value
                )
            else:
                # Fall back to WSZ_api
                result = push_data(
                    table=table_name,
                    column=field_name,
                    key=record_id,
                    value=field_value
                )
                
            logger.info(f"Successfully pushed {field_name}={field_value} to {table_name}/{record_id}")
            return result
        except Exception as e:
            logger.error(f"Failed to push {field_name}={field_value} to {table_name}/{record_id}: {e}")
            raise

    def fetch_record(
        self,
        table_name: str,
        record_id: Union[int, str]
    ) -> Dict[str, Any]:
        """
        Fetch a single record by ID.

        Args:
            table_name: The name of the table
            record_id: The ID of the record to fetch

        Returns:
            Dict[str, Any]: The record data as a dictionary
        """
        try:
            if self.direct_client:
                # Use DirectAPIClient
                return self.direct_client.fetch_record(
                    table_name=table_name,
                    record_id=record_id
                )
            else:
                # No direct equivalent in WSZ_api, so we'll fetch the table and filter
                logger.warning("fetch_record not directly supported in WSZ_api, using workaround")
                df = self.fetch_table(
                    table_name=table_name,
                    top=1,
                    skip=0,
                    new_data_only=False,
                    date_created_start=None
                )
                # Find the record by ID (this assumes that the ID field is '__KEY')
                record = df[df['__KEY'] == record_id]
                if len(record) == 0:
                    raise ValueError(f"Record with ID {record_id} not found in {table_name}")
                return record.iloc[0].to_dict()
                
        except Exception as e:
            logger.error(f"Failed to fetch record {record_id} from {table_name}: {e}")
            raise


# Create a singleton instance of the API client
api_client = LegacyAPIClient() 