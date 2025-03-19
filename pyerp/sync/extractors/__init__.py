"""
Data extractors for sync operations.

This package provides extractors for retrieving data from source systems
during synchronization.
"""

from .legacy_api import LegacyAPIExtractor

__all__ = ["LegacyAPIExtractor"]
