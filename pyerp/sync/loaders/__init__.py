"""
Data loaders for sync operations.

This package provides loaders for loading transformed data into target
systems during synchronization.
"""

from .django_model import DjangoModelLoader

__all__ = ["DjangoModelLoader"]
