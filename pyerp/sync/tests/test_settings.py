"""
Test settings for pyERP sync module tests.
"""

from django.conf import settings

# Configure minimal Django settings for tests
if not settings.configured:
    settings.configure(
        DEBUG=True,
        USE_TZ=True,
        DATABASES={
            "default": {
                "ENGINE": "django.db.backends.sqlite3",
                "NAME": ":memory:",
            }
        },
        INSTALLED_APPS=[
            "django.contrib.auth",
            "django.contrib.contenttypes",
            "django.contrib.sites",
            "pyerp.sync",
        ],
        SITE_ID=1,
        MIDDLEWARE_CLASSES=(),
        SECRET_KEY="not-so-secret",
        MIGRATION_MODULES={},  # No migrations needed for tests
    )

    try:
        import django

        django.setup()
    except AttributeError:
        pass  # Django < 1.7
