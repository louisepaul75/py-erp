"""
Core app for the pyERP system.
"""

 # pyERP Core App - Common functionality shared across other apps

 # Import checks module to register system checks
from . import checks  # noqa: F401

default_app_config = 'pyerp.core.apps.CoreConfig'  # noqa: F841
