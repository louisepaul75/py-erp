"""
Simple API client for the legacy ERP system.

This module provides a simplified version of the LegacyERPClient for use
in extraction tasks, maintaining compatibility with the previous
SimpleAPIClient.
"""

import logging
from typing import Optional

import pandas as pd

from pyerp.external_api.legacy_erp.base import BaseAPIClient
from pyerp.external_api.legacy_erp.exceptions import LegacyERPError

# Configure logging
logger = logging.getLogger(__name__)


class SimpleAPIClient(BaseAPIClient):
    """
    Simple client for the legacy ERP API with a subset of functionality.
    
    This class maintains compatibility with the
    direct_api.scripts.getTable.SimpleAPIClient interface to avoid breaking
    existing code that depends on it.
    """
    
    def __init__(self, environment: str = "live", timeout: int = None):
        """
        Initialize a new simple API client.
        
        Args:
            environment: The API environment to use ('live', 'test', etc.)
            timeout: Optional timeout for API requests in seconds
        """
        super().__init__(environment=environment, timeout=timeout)
        logger.debug(
            "Initialized SimpleAPIClient for environment: %s",
            environment,
        )
    
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
        fail_on_filter_error: bool = False,
    ) -> pd.DataFrame:
        """
        Fetch records from a table in the legacy ERP system.
        
        Args:
            table_name: Name of the table to fetch records from
            top: Maximum number of records to fetch (page size)
            skip: Number of records to skip (for pagination)
            filter_query: OData filter query string
            all_records: Whether to fetch all records (ignore pagination)
            fail_on_filter_error: If True, raise an error if filter doesn't work
            
        Returns:
            DataFrame containing the fetched records
        """
        try:
            return super().fetch_table(
                table_name=table_name,
                top=top,
                skip=skip,
                filter_query=filter_query,
                all_records=all_records,
                fail_on_filter_error=fail_on_filter_error,
            )
        except Exception as e:
            raise LegacyERPError(f"Failed to fetch table: {e}") 