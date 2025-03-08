"""
Simple API client for the legacy ERP system.

This module provides a simplified version of the LegacyERPClient for use
in extraction tasks, maintaining compatibility with the previous SimpleAPIClient.
"""

import logging
import pandas as pd
from typing import Any, Dict, List, Optional, Union

from pyerp.external_api.legacy_erp.client import LegacyERPClient

logger = logging.getLogger(__name__)


class SimpleAPIClient:
    """
    Simple client for the legacy ERP API with a subset of functionality.
    
    This class maintains compatibility with the direct_api.scripts.getTable.SimpleAPIClient
    interface to avoid breaking existing code that depends on it.
    """
    
    def __init__(self, environment: str = "live", timeout: int = None):
        """
        Initialize a new simple API client.
        
        Args:
            environment: The API environment to use ('live', 'test', etc.)
            timeout: Optional timeout for API requests in seconds
        """
        self.client = LegacyERPClient(environment=environment, timeout=timeout)
        self.environment = environment
        logger.debug("Initialized SimpleAPIClient for environment: %s", environment)
    
    def fetch_table(
        self,
        table_name: str,
        top: int = 100,
        skip: int = 0,
        filter_query: Optional[str] = None,
        all_records: bool = False,
    ) -> pd.DataFrame:
        """
        Fetch records from a table in the legacy ERP system.
        
        Args:
            table_name: Name of the table to fetch records from
            top: Maximum number of records to fetch (page size)
            skip: Number of records to skip (for pagination)
            filter_query: OData filter query string
            all_records: Whether to fetch all records (ignore pagination)
            
        Returns:
            DataFrame containing the fetched records
        """
        # This is a wrapper that delegates to the full client implementation
        # We maintain the same interface for backward compatibility
        return self.client.fetch_table(
            table_name=table_name,
            top=top,
            skip=skip,
            filter_query=filter_query,
        ) 