import pytest
from django.conf import settings
from pyerp.config.settings.testing import DisableMigrations


@pytest.mark.django_db
def test_testing_settings_applied():
    """
    Verify that settings from testing.py are loaded and applied.
    Importing 'settings' implicitly loads the configured settings module.
    """
    # Check settings explicitly set or modified in testing.py
    assert settings.DEBUG is True
    assert (
        settings.EMAIL_BACKEND == "django.core.mail.backends.console.EmailBackend"
    )
    # Break the list for line length
    assert settings.PASSWORD_HASHERS == \
        ["django.contrib.auth.hashers.MD5PasswordHasher"]
    assert settings.AUTH_PASSWORD_VALIDATORS == []
    assert settings.CELERY_TASK_ALWAYS_EAGER is True
    assert isinstance(settings.MIGRATION_MODULES, DisableMigrations)

    # Check that debug_toolbar and ddtrace were removed (assuming they were in base)
    assert "debug_toolbar" not in settings.INSTALLED_APPS
    assert not any("debug_toolbar" in m for m in settings.MIDDLEWARE)
    assert "ddtrace.contrib.django" not in settings.INSTALLED_APPS
    # Break the any() call for line length
    assert not any(
        "ddtrace" in m for m in settings.MIDDLEWARE
    )

    # Check database engine (will depend on environment)
    assert settings.DATABASES['default']['ENGINE'] in [
        "django.db.backends.postgresql",
        "django.db.backends.sqlite3",
    ]

    # Check a setting added in testing.py
    assert "pyerp.utils.email_system" in settings.INSTALLED_APPS
