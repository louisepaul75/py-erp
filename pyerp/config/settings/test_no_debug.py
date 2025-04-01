"""
Test settings for pyERP project without debug toolbar.

These settings are specifically for running tests without debug toolbar,
to bypass the debug_toolbar.E001 error.
"""

from .test import *  # noqa

# Remove debug toolbar from installed apps
INSTALLED_APPS = [app for app in INSTALLED_APPS if app != "debug_toolbar"]

# Remove debug toolbar middleware
MIDDLEWARE = [mw for mw in MIDDLEWARE if "debug_toolbar" not in mw]

# Configure debug toolbar for tests
DEBUG_TOOLBAR_CONFIG = {
    "SHOW_TOOLBAR_CALLBACK": lambda request: False,
    "IS_RUNNING_TESTS": True,
}

# Disable debug mode for tests
DEBUG = False 