"""Pytest configuration and fixtures for the core module tests."""

import pytest

# Mark all tests in this directory with the 'unit' marker
pytestmark = pytest.mark.unit


@pytest.fixture(scope="session", autouse=True)
def django_settings():
    """Ensure Django settings are properly configured for unit tests."""
    # Make sure we're using the test settings
    pytest.importorskip("django")
    from django.conf import settings

    if not settings.configured:
        if (
            hasattr(settings, "SETTINGS_MODULE")
            and "pyerp.config.settings.test" not in settings.SETTINGS_MODULE
            and "tests.settings" not in settings.SETTINGS_MODULE
        ):
            settings_module = "tests.settings"
            import django

            settings.configure()
            django.setup()

    return settings


@pytest.fixture
def test_user(django_user_model):
    """Create a test user."""
    return django_user_model.objects.create_user(
        username="testuser", email="test@example.com", password="password123"
    )


@pytest.fixture
def admin_user(django_user_model):
    """Create an admin user."""
    return django_user_model.objects.create_superuser(
        username="admin", email="admin@example.com", password="adminpassword"
    )
