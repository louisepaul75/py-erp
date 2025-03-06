# pyERP - Custom Django ERP System
# This file marks the directory as a Python package

# Configure Celery
from .celery import app as celery_app  # noqa: F401

__all__ = ['celery_app']  # noqa: F841
  # noqa: F841
