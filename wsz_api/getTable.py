"""
Type stub for the wsz_api.getTable module.

This module provides functions to retrieve data from legacy system tables.
"""

from datetime import datetime
from typing import Any

import pandas as pd


def getTable(
    table_name: str,
    fields: list[str] | None = None,
    where: dict[str, Any] | None = None,
    order_by: str | None = None,
    limit: int | None = None,
    offset: int | None = None,
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
    fields: list[str] | None = None,
    where: dict[str, Any] | None = None,
    order_by: str | None = None,
    limit: int | None = None,
    offset: int | None = None,
    session_cookie: str | None = None,
    top: int | None = None,
    skip: int | None = None,
    new_data_only: bool = False,
    date_created_start: datetime | None = None,
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
