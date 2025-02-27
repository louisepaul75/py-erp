# pyERP - Custom Django ERP System
# This file marks the directory as a Python package

# Configure Celery
from .celery import app as celery_app

__all__ = ['celery_app'] 