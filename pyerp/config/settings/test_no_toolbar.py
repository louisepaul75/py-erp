"""
Test settings for pyERP project without debug toolbar.

These settings extend the test settings but ensure the debug toolbar is completely disabled.
"""

from .test import *  # noqa

# Force remove debug toolbar
INSTALLED_APPS = [app for app in INSTALLED_APPS if app != "debug_toolbar"]
MIDDLEWARE = [mw for mw in MIDDLEWARE if "debug_toolbar" not in mw]

# Disable debug toolbar completely
DEBUG_TOOLBAR_CONFIG = {
    "SHOW_TOOLBAR_CALLBACK": lambda request: False,
    "IS_RUNNING_TESTS": False,
}

# Add explicit DEBUG=False setting
DEBUG = False

# Use PostgreSQL for tests
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": "pyerp_testing",
        "USER": "postgres",
        "PASSWORD": DB_PASSWORD,
        "HOST": "192.168.73.65",
        "PORT": "5432",
        "TEST": {
            "NAME": "test_pyerp",
        },
    }
} 