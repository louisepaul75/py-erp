"""
Staging settings for pyERP project.

These settings extend the production settings but with some modifications
to allow easier debugging in a production-like environment.
"""

from .production import *  # noqa

# Allow limited debugging in staging
DEBUG = os.environ.get("DEBUG", "False").lower() == "true"

# More permissive ALLOWED_HOSTS for staging
ALLOWED_HOSTS = os.environ.get("ALLOWED_HOSTS", "*").split(",")

# Optional: Enable Django Debug Toolbar in staging if needed
if DEBUG and os.environ.get("ENABLE_DEBUG_TOOLBAR", "False").lower() == "true":
    INSTALLED_APPS += ["debug_toolbar"]  # noqa
    MIDDLEWARE += ["debug_toolbar.middleware.DebugToolbarMiddleware"]  # noqa
    INTERNAL_IPS = ["127.0.0.1"]
    DEBUG_TOOLBAR_CONFIG = {
        "SHOW_TOOLBAR_CALLBACK": lambda request: True,
    }

# Less strict security for staging environment
SECURE_SSL_REDIRECT = os.environ.get("SECURE_SSL_REDIRECT", "False").lower() == "true"
SECURE_HSTS_SECONDS = 0
SECURE_CONTENT_TYPE_NOSNIFF = True
SESSION_COOKIE_SECURE = SECURE_SSL_REDIRECT
CSRF_COOKIE_SECURE = SECURE_SSL_REDIRECT

# More detailed error emails in staging
ADMINS = [
    ("Developer", email)
    for email in os.environ.get("ADMIN_EMAILS", "").split(",")
    if email
]
SERVER_EMAIL = os.environ.get("SERVER_EMAIL", "staging@example.com")

# Adjust logging for more verbosity in staging
if DEBUG:
    LOGGING["loggers"]["django"]["level"] = "DEBUG"  # noqa
    LOGGING["loggers"]["pyerp"]["level"] = "DEBUG"  # noqa

# Celery settings - make tasks execute immediately if needed for debugging
CELERY_TASK_ALWAYS_EAGER = (
    os.environ.get("CELERY_TASK_ALWAYS_EAGER", "False").lower() == "true"
)
