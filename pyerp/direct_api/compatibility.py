"""
Compatibility layer for the legacy WSZ_api module.

This module provides drop-in replacements for common WSZ_api functions
to make migration easier for existing code.
"""

import warnings
import pandas as pd
from typing import Dict, List, Optional, Any, Union

from pyerp.direct_api.client import DirectAPIClient

# Create a client instance for compatibility functions
_client = DirectAPIClient()


def fetch_data_from_api(
    table_name: str,
    top: int = 100,
    skip: int = 0,
    new_data_only: bool = True,
    date_created_start: Optional[str] = None
) -> pd.DataFrame:
    """
    Compatibility function for wsz_api.getTable.fetch_data_from_api
    
    Args:
        table_name: The name of the table to fetch data from
        top: The number of records to fetch (max per page)
        skip: The number of records to skip (for pagination)
        new_data_only: If True, fetch only records with modified_date > threshold
        date_created_start: Optional start date for filtering by creation date
        
    Returns:
        pd.DataFrame: A pandas DataFrame containing the fetched data
    """
    warnings.warn(
        "Using deprecated WSZ_api compatibility layer. "
        "Consider migrating to DirectAPIClient directly.",
        DeprecationWarning, stacklevel=2
    )
    return _client.fetch_table(
        table_name=table_name,
        top=top,
        skip=skip,
        new_data_only=new_data_only,
        date_created_start=date_created_start
    )


def push_data(
    table: str,
    column: str,
    key: Union[int, str],
    value: Any
) -> bool:
    """
    Compatibility function for wsz_api.pushField.push_data
    
    Args:
        table: The name of the table to update
        column: The name of the field to update
        key: The ID of the record to update
        value: The new value for the field
        
    Returns:
        bool: True if the update was successful
    """
    warnings.warn(
        "Using deprecated WSZ_api compatibility layer. "
        "Consider migrating to DirectAPIClient directly.",
        DeprecationWarning, stacklevel=2
    )
    return _client.push_field(
        table_name=table,
        record_id=key,
        field_name=column,
        field_value=value
    )


def get_session_cookie(mode: str = 'live') -> str:
    """
    Compatibility function for wsz_api.auth.get_session_cookie
    
    Args:
        mode: The environment to use ('live', 'test', etc.)
        
    Returns:
        str: The session cookie for API requests
    """
    warnings.warn(
        "Using deprecated WSZ_api compatibility layer. "
        "Consider migrating to DirectAPIClient directly.",
        DeprecationWarning, stacklevel=2
    )
    from pyerp.direct_api.auth import get_session_cookie as direct_get_session_cookie
    return direct_get_session_cookie(environment=mode)


# Add compatibility for other WSZ_api functions as needed 