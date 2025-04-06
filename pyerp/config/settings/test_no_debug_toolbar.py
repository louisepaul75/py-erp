"""
Test settings for pyERP project that completely disables debug toolbar.
"""

# Import base test settings
from .test import *  # noqa

# Make sure debug toolbar is removed from INSTALLED_APPS
INSTALLED_APPS = [app for app in INSTALLED_APPS if app != "debug_toolbar"]

# Make sure debug toolbar middleware is removed
MIDDLEWARE = [mw for mw in MIDDLEWARE if "debug_toolbar" not in mw]

# Set DEBUG_TOOLBAR_CONFIG to avoid the debug_toolbar.E001 check
DEBUG_TOOLBAR_CONFIG = {
    "SHOW_TOOLBAR_CALLBACK": lambda request: False,
    "IS_RUNNING_TESTS": False,
}

# Set DEBUG to False to fully avoid debug toolbar issues
DEBUG = False

# Make sure debug toolbar is not in sys.modules
import sys
if 'debug_toolbar' in sys.modules:
    del sys.modules['debug_toolbar']

# Configure logging level for tests
import logging
logging.getLogger('django').setLevel(logging.ERROR) 