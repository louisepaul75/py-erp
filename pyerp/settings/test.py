"""
Test settings for pyERP project.
"""

# Import base settings
from .base import *  # noqa

# Disable debug mode
DEBUG = False

# Remove debug toolbar from INSTALLED_APPS and MIDDLEWARE
INSTALLED_APPS = [app for app in INSTALLED_APPS if app != 'debug_toolbar']
MIDDLEWARE = [mw for mw in MIDDLEWARE if mw != 'debug_toolbar.middleware.DebugToolbarMiddleware']

# Disable debug toolbar completely
DEBUG_TOOLBAR_CONFIG = {
    'ENABLED': False,
    'SHOW_TOOLBAR_CALLBACK': lambda request: False,
    'IS_RUNNING_TESTS': False,
}

# Prevent debug toolbar from being loaded
import sys
if 'debug_toolbar' in sys.modules:
    del sys.modules['debug_toolbar']

# Prevent debug toolbar from being imported
import builtins
_import = builtins.__import__
def import_mock(name, *args, **kwargs):
    if name == 'debug_toolbar':
        return None
    return _import(name, *args, **kwargs)
builtins.__import__ = import_mock

# Prevent debug toolbar from being checked
from django.core.checks import Tags, register
@register(Tags.compatibility)
def check_debug_toolbar(app_configs, **kwargs):
    return []

# Test database settings
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}

# Use fast password hasher for tests
PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.MD5PasswordHasher',
]

# Disable migrations for tests
class DisableMigrations:
    def __contains__(self, item):
        return True

    def __getitem__(self, item):
        return None

MIGRATION_MODULES = DisableMigrations() 