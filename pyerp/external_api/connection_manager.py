"""
Connection manager for external API services.

This module provides functionality to enable or disable external API
connections on a per-instance basis. Settings are stored in a local
JSON file that is excluded from version control.
"""

import json
from pathlib import Path
from typing import Dict

from pyerp.utils.logging import get_logger

# Set up logging using the centralized logging system
logger = get_logger(__name__)

# Define the path to the connection settings file
# Place it in a location that is .gitignore'd
BASE_DIR = Path(__file__).resolve().parent.parent
CONNECTIONS_FILE = BASE_DIR / "config" / "external_connections.json"

# Default connection settings - all connections disabled by default
DEFAULT_CONNECTIONS = {
    "legacy_erp": False,
    "images_cms": False,
}


def get_connections() -> Dict[str, bool]:
    """
    Get current connection settings.

    Returns:
        Dict[str, bool]: A dictionary mapping connection names to their
        enabled status.
    """
    if not CONNECTIONS_FILE.exists():
        # Create the directory if it doesn't exist
        CONNECTIONS_FILE.parent.mkdir(exist_ok=True)
        # Initialize with default settings
        save_connections(DEFAULT_CONNECTIONS)
        return DEFAULT_CONNECTIONS

    try:
        with open(CONNECTIONS_FILE, "r") as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError) as e:
        logger.error(f"Error reading connections file: {e}")
        # Return defaults if there's an error
        return DEFAULT_CONNECTIONS


def save_connections(connections: Dict[str, bool]) -> bool:
    """
    Save connection settings to file.

    Args:
        connections (Dict[str, bool]): Connection settings to save

    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Create the directory if it doesn't exist
        CONNECTIONS_FILE.parent.mkdir(exist_ok=True)

        with open(CONNECTIONS_FILE, "w") as f:
            json.dump(connections, f, indent=2)
        return True
    except IOError as e:
        logger.error(f"Error saving connections file: {e}")
        return False


def is_connection_enabled(connection_name: str) -> bool:
    """
    Check if a specific connection is enabled.

    Args:
        connection_name (str): Name of the connection to check

    Returns:
        bool: True if the connection is enabled, False otherwise
    """
    connections = get_connections()
    return connections.get(connection_name, False)


def set_connection_status(connection_name: str, enabled: bool) -> bool:
    """
    Enable or disable a specific connection.

    Args:
        connection_name (str): Name of the connection to modify
        enabled (bool): Whether to enable or disable the connection

    Returns:
        bool: True if successful, False otherwise
    """
    connections = get_connections()
    if (
        connection_name not in connections
        and connection_name not in DEFAULT_CONNECTIONS
    ):
        logger.error(
            f"Attempted to set status for unknown connection: " f"{connection_name}"
        )
        return False

    connections[connection_name] = enabled
    return save_connections(connections)


def add_connection(connection_name: str, enabled: bool = False) -> bool:
    """
    Add a new connection to the configuration.

    Args:
        connection_name (str): Name of the new connection
        enabled (bool): Whether the connection should be enabled initially

    Returns:
        bool: True if successful, False otherwise
    """
    connections = get_connections()
    if connection_name in connections:
        logger.warning(f"Connection {connection_name} already exists")
        return False

    connections[connection_name] = enabled
    return save_connections(connections)
