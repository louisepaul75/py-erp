"""
Main API client for interacting with the legacy 4D-based ERP system.

This module provides the LegacyERPClient class which handles all interactions
with the legacy API, including data retrieval and updates.
"""

from typing import Optional

import pandas as pd

from pyerp.external_api.legacy_erp.base import BaseAPIClient
from pyerp.external_api.legacy_erp.exceptions import LegacyERPError
from pyerp.external_api import connection_manager
from pyerp.utils.logging import get_logger

# Configure logging using the centralized logging system
logger = get_logger(__name__)


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
        top: Optional[int] = None,
        skip: int = 0,
        filter_query: Optional[str] = None,
        all_records: bool = False,
        new_data_only: bool = True,
        date_created_start: Optional[str] = None,
        fail_on_filter_error: bool = False,
    ) -> pd.DataFrame:
        """
        Fetch records from a table in the legacy ERP system.
        
        Args:
            table_name: Name of the table to fetch records from
            top: Number of records to fetch per request (None for no limit, 
                though the API server may still apply a default limit, 
                typically 100 records)
            skip: Number of records to skip (for pagination)
            filter_query: [['field', 'operator', 'value']]
            all_records: Whether to fetch all records (may take a long time)
            new_data_only: If True, only fetch new records
            date_created_start: Start date for filtering by creation date
            fail_on_filter_error: Whether to fail if filter query is invalid
            
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
                fail_on_filter_error=fail_on_filter_error,
            )
        except Exception as e:
            raise LegacyERPError(f"Failed to fetch table: {e}") 


if __name__ == "__main__":
    pd.set_option('display.max_columns', None)
    # pd.set_option('display.max_rows', 10)
    # pd.set_option('display.width', 1000)

    client = LegacyERPClient(environment="live")


    filter_query = [['created_date', '>=', '2025-03-01']]

    belege = client.fetch_table(
        table_name="Belege",
        # skip = 10000,
        top=100,
        filter_query=filter_query
    )
    print(belege.tail())
    absnr = str(list(belege['AbsNr'].unique().astype(str)))
    print(absnr)
    belege_pos = client.fetch_table(
        table_name="Belege_Pos",
        filter_query=[['AbsNr', 'in', absnr]]
    )

    print(belege.tail())
    print(belege_pos.tail())
    # breakpoint()

