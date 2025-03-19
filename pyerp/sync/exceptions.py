"""Exceptions for the sync module."""


class SyncError(Exception):
    """Base exception for sync operations."""

    pass


class ExtractError(SyncError):
    """Exception raised during data extraction."""

    pass


class TransformError(SyncError):
    """Exception raised during data transformation."""

    pass


class LoadError(SyncError):
    """Exception raised during data loading."""

    pass


class ValidationError(SyncError):
    """Exception raised during data validation."""

    pass


class ConfigurationError(SyncError):
    """Exception raised for configuration issues."""

    pass
