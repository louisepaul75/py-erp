"""
Type stub for the wsz_api.api module.

This module provides general API functionality for interacting with the legacy system.
"""

from typing import Any

import pandas as pd


class WSZ_API:
    """
    Main API class for interacting with the legacy system.

    This class provides a high-level interface for all API operations,
    including authentication, data retrieval, and data updates.
    """

    def __init__(
        self,
        username: str | None = None,
        password: str | None = None,
        host: str = "localhost",
        port: int = 8080,
    ) -> None:
        """
        Initialize the WSZ_API object.

        Args:
            username: Username for authentication (optional if using environment variables)
            password: Password for authentication (optional if using environment variables)
            host: Host address of the legacy system
            port: Port number of the legacy system
        """
        self.username = username
        self.password = password
        self.host = host
        self.port = port
        self.session_cookie: str | None = None

    def authenticate(self) -> bool:
        """
        Authenticate with the legacy system.

        Returns:
            True if authentication was successful, False otherwise
        """
        raise NotImplementedError("This is a stub for type checking only")

    def get_table(
        self,
        table_name: str,
        fields: list[str] | None = None,
        where: dict[str, Any] | None = None,
        order_by: str | None = None,
        limit: int | None = None,
        offset: int | None = None,
    ) -> pd.DataFrame:
        """
        Get data from a table in the legacy system.

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

    def get_record(
        self,
        table_name: str,
        record_id: int | str,
        fields: list[str] | None = None,
    ) -> dict[str, Any]:
        """
        Get a single record from a table in the legacy system.

        Args:
            table_name: Name of the table to retrieve the record from
            record_id: ID of the record to retrieve
            fields: List of fields to retrieve (None for all fields)

        Returns:
            Dictionary containing the requested record data
        """
        raise NotImplementedError("This is a stub for type checking only")

    def push_field(
        self,
        table_name: str,
        record_id: int | str,
        field_name: str,
        field_value: Any,
    ) -> bool:
        """
        Update a field in a record in the legacy system.

        Args:
            table_name: Name of the table to update
            record_id: ID of the record to update
            field_name: Name of the field to update
            field_value: New value for the field

        Returns:
            True if the update was successful, False otherwise
        """
        raise NotImplementedError("This is a stub for type checking only")


def call_api(
    endpoint: str,
    method: str = "GET",
    params: dict[str, Any] | None = None,
    data: dict[str, Any] | None = None,
    headers: dict[str, str] | None = None,
    session_cookie: str | None = None,
    **kwargs: Any,
) -> dict[str, Any]:
    """
    Make a direct call to the legacy API.

    Args:
        endpoint: API endpoint to call
        method: HTTP method to use (GET, POST, PUT, DELETE)
        params: Query parameters for the request
        data: Request body data
        headers: HTTP headers for the request
        session_cookie: Authentication cookie for the API
        **kwargs: Additional arguments

    Returns:
        Dictionary containing the API response
    """
    raise NotImplementedError("This is a stub for type checking only")


def get_table_schema(
    table_name: str,
    session_cookie: str | None = None,
) -> dict[str, dict[str, Any]]:
    """
    Get the schema for a table in the legacy system.

    Args:
        table_name: Name of the table to get the schema for
        session_cookie: Authentication cookie for the API

    Returns:
        Dictionary containing the table schema
    """
    raise NotImplementedError("This is a stub for type checking only")


def list_tables(
    session_cookie: str | None = None,
) -> list[str]:
    """
    Get a list of available tables in the legacy system.

    Args:
        session_cookie: Authentication cookie for the API

    Returns:
        List of table names
    """
    raise NotImplementedError("This is a stub for type checking only")
