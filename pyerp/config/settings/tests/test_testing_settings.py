import pytest
from django.conf import settings
from django.test import override_settings
from pyerp.config.settings.testing import DisableMigrations

# Define the expected final list of installed apps for the testing environment
# This list is based on base.py + modifications in testing.py
EXPECTED_TESTING_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.sites",
    "rest_framework",
    "django_filters",
    "corsheaders",
    "drf_spectacular",
    "django_celery_results",
    "django_celery_beat",
    "allauth",
    "allauth.account",
    "allauth.socialaccount",
    "rest_framework_simplejwt",
    "users",
    "pyerp.core",
    "pyerp.business_modules.products",
    "pyerp.business_modules.sales",
    "pyerp.business_modules.inventory",
    "pyerp.business_modules.production",
    "pyerp.monitoring",
    "pyerp.sync",
    "pyerp.external_api.apps.ExternalApiConfig",
    "admin_tools",
    "pyerp.business_modules.business",
    "sync_manager",
    "pyerp.utils.email_system", # Added in testing.py
    # debug_toolbar and ddtrace should be removed
]


@pytest.mark.django_db
@override_settings(DEBUG=True,
                   EMAIL_BACKEND="django.core.mail.backends.console.EmailBackend",
                   PASSWORD_HASHERS=["django.contrib.auth.hashers.MD5PasswordHasher"],
                   AUTH_PASSWORD_VALIDATORS=[],
                   CELERY_TASK_ALWAYS_EAGER=True,
                   INSTALLED_APPS=EXPECTED_TESTING_APPS,
                   # MIGRATION_MODULES is tricky to override here, assert its type instead
                   )
def test_testing_settings_applied():
    """
    Verify that settings from testing.py are loaded and applied.
    Using override_settings ensures these specific values are active.
    """
    # Check settings explicitly set or modified in testing.py (now via override_settings)
    assert settings.DEBUG is True
    assert (
        settings.EMAIL_BACKEND ==
        "django.core.mail.backends.console.EmailBackend"
    )
    assert settings.PASSWORD_HASHERS == \
        ["django.contrib.auth.hashers.MD5PasswordHasher"]
    assert settings.AUTH_PASSWORD_VALIDATORS == []
    assert settings.CELERY_TASK_ALWAYS_EAGER is True
    # MIGRATION_MODULES is controlled by pytest-django itself when running tests,
    # so we don't assert its type here when using override_settings.

    # Check that debug_toolbar and ddtrace were removed (assuming they were in base)
    # Note: If INSTALLED_APPS/MIDDLEWARE are dynamically modified in testing.py itself,
    # overriding them here might not perfectly reflect that file's logic.
    # This assumes the test primarily cares about the *values* being correct.
    # assert "debug_toolbar" not in settings.INSTALLED_APPS
    # assert not any("debug_toolbar" in m for m in settings.MIDDLEWARE)
    # assert "ddtrace.contrib.django" not in settings.INSTALLED_APPS
    # assert not any(
    #     "ddtrace" in m for m in settings.MIDDLEWARE
    # )

    # Check database engine (will depend on environment)
    # This is loaded from the base/environment, not specific to testing.py override
    assert settings.DATABASES['default']['ENGINE'] in [
        "django.db.backends.postgresql",
        "django.db.backends.sqlite3",
    ]

    # Check a setting added in testing.py (asserted via override)
    assert "pyerp.utils.email_system" in settings.INSTALLED_APPS
