"""
Direct API client for the legacy 4D-based ERP system.

This module provides a direct implementation of the API client to replace
the external WSZ_api package dependency.
"""

__version__ = "0.1.0"

# Import the client for easy access
from pyerp.direct_api.client import DirectAPIClient

# Create a singleton instance for backwards compatibility
client = DirectAPIClient()
