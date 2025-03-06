"""
Type stub for the wsz_api.getRecord module.

This module provides functions to retrieve individual records from legacy system tables.
"""

from typing import Any


def getRecord(
    table_name: str,
    record_id: int | str,
    fields: list[str] | None = None,
    **kwargs: Any,
) -> dict[str, Any]:
    """
    Retrieve a single record from a legacy system table.

    Args:
        table_name: Name of the table to retrieve the record from
        record_id: ID of the record to retrieve
        fields: List of fields to retrieve (None for all fields)
        **kwargs: Additional arguments

    Returns:
        Dictionary containing the requested record data
    """
    raise NotImplementedError("This is a stub for type checking only")


# Alias for getRecord to maintain backward compatibility
get_record = getRecord


def fetch_record_from_api(
    table_name: str,
    record_id: int | str,
    fields: list[str] | None = None,
    session_cookie: str | None = None,
    **kwargs: Any,
) -> dict[str, Any]:
    """
    Fetch a single record from the legacy API.

    This is an alternative interface to getRecord that accepts a session cookie.

    Args:
        table_name: Name of the table to retrieve the record from
        record_id: ID of the record to retrieve
        fields: List of fields to retrieve (None for all fields)
        session_cookie: Authentication cookie for the API
        **kwargs: Additional arguments

    Returns:
        Dictionary containing the requested record data
    """
    raise NotImplementedError("This is a stub for type checking only")
