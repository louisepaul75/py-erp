"""
Core module for pyERP system.
Contains shared base models, utilities, and services used across the system.
"""

# pyERP Core App - Common functionality shared across other apps

# Import checks module to register system checks
from . import checks  # noqa: F401

default_app_config = "pyerp.core.apps.CoreConfig"
