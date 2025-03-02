"""
Type stub for the wsz_api.getTable module.

This module provides functions to retrieve data from legacy system tables.
"""

from typing import Any, Dict, List, Optional, Union
import pandas as pd
from datetime import datetime


def getTable(
    table_name: str,
    fields: Optional[List[str]] = None,
    where: Optional[Dict[str, Any]] = None,
    order_by: Optional[str] = None,
    limit: Optional[int] = None,
    offset: Optional[int] = None,
) -> pd.DataFrame:
    """
    Retrieve data from a legacy system table.
    
    Args:
        table_name: Name of the table to retrieve data from
        fields: List of fields to retrieve (None for all fields)
        where: Dictionary of field-value pairs for filtering
        order_by: Field to order results by
        limit: Maximum number of records to return
        offset: Number of records to skip
        
    Returns:
        DataFrame containing the requested data
    """
    raise NotImplementedError("This is a stub for type checking only")

def fetch_data_from_api(
    table_name: str,
    fields: Optional[List[str]] = None,
    where: Optional[Dict[str, Any]] = None,
    order_by: Optional[str] = None,
    limit: Optional[int] = None,
    offset: Optional[int] = None,
    session_cookie: Optional[str] = None,
    top: Optional[int] = None,
    skip: Optional[int] = None,
    new_data_only: bool = False,
    date_created_start: Optional[datetime] = None,
) -> pd.DataFrame:
    """
    Fetch data from the legacy API.
    
    This is an alternative interface to getTable that accepts a session cookie.
    
    Args:
        table_name: Name of the table to retrieve data from
        fields: List of fields to retrieve (None for all fields)
        where: Dictionary of field-value pairs for filtering
        order_by: Field to order results by
        limit: Maximum number of records to return
        offset: Number of records to skip
        session_cookie: Authentication cookie for the API
        top: Alternative to limit, maximum number of records to return
        skip: Alternative to offset, number of records to skip
        new_data_only: Whether to only fetch new data since the last sync
        date_created_start: Only fetch records created after this date
        
    Returns:
        DataFrame containing the requested data
    """
    raise NotImplementedError("This is a stub for type checking only") 