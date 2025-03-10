"""
Main API client for interacting with the legacy 4D-based ERP system.

This module provides the LegacyERPClient class which handles all interactions
with the legacy API, including data retrieval and updates.
"""

import logging
from typing import Optional

import pandas as pd

from pyerp.external_api.legacy_erp.base import BaseAPIClient
from pyerp.external_api.legacy_erp.exceptions import LegacyERPError
from pyerp.external_api import connection_manager

# Configure logging
logger = logging.getLogger(__name__)


class LegacyERPClient(BaseAPIClient):
    """
    Client for directly interacting with the legacy 4D-based ERP system.

    This class provides methods for fetching data from and pushing data to
    the legacy system, handling authentication and error handling.
    """

    def __init__(self, environment: str = "live", timeout: int = None):
        """
        Initialize a new client instance.

        Args:
            environment: Which API environment to use ('live', 'test', etc.)
            timeout: Optional custom timeout for API requests (in seconds)
        """
        super().__init__(environment=environment, timeout=timeout)

    def check_connection(self) -> bool:
        """
        Check if the connection to the legacy ERP API is working.
        
        This method is used by the health check system to verify 
        that the API is accessible and responding correctly.
        
        Returns:
            bool: True if connection is successful, False otherwise
            
        Raises:
            LegacyERPError: If an unexpected error occurs during validation
        """
        try:
            logger.info("Checking connection to legacy ERP API")
            
            # First check if the connection is enabled
            if not connection_manager.is_connection_enabled("legacy_erp"):
                logger.info("Legacy ERP API connection is disabled")
                return False
                
            return self.validate_session()
        except Exception as e:
            logger.error(f"Connection check failed: {e}")
            raise LegacyERPError(f"Failed to check connection: {e}")

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
        Fetch records from a table in the legacy ERP system.
        
        Args:
            table_name: Name of the table to fetch records from
            top: Maximum number of records to fetch (page size)
            skip: Number of records to skip (for pagination)
            filter_query: OData filter query string
            all_records: Whether to fetch all records (may take a long time)
            new_data_only: If True, only fetch new records
            date_created_start: Start date for filtering by creation date
            
        Returns:
            DataFrame containing the fetched records
            
        Raises:
            ConnectionError: If connection to the API fails
            ResponseError: If API returns an error response
            DataError: If data cannot be parsed
        """
        try:
            return super().fetch_table(
                table_name=table_name,
                top=top,
                skip=skip,
                filter_query=filter_query,
                all_records=all_records,
                new_data_only=new_data_only,
                date_created_start=date_created_start,
            )
        except Exception as e:
            raise LegacyERPError(f"Failed to fetch table: {e}") 