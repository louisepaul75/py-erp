"""
Legacy ERP API integrations.

This package provides functionality for interacting with the legacy ERP
system API.
"""

from .scripts.simple_client import SimpleAPIClient
from .client import LegacyERPClient

__all__ = ['SimpleAPIClient', 'LegacyERPClient'] 