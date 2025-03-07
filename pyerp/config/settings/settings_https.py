"""
HTTPS settings for pyERP project.

Import this file in your development or local settings to enable proper HTTPS support.  # noqa: E501
"""

# This tells Django to trust the X-Forwarded-Proto header from the proxy server  # noqa: E501
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

# Disable Django's own SSL redirect as Nginx is handling this
SECURE_SSL_REDIRECT = False

# Set cookies as secure since we're using HTTPS
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

# Other security settings
SECURE_HSTS_SECONDS = 0
SECURE_HSTS_INCLUDE_SUBDOMAINS = False
SECURE_HSTS_PRELOAD = False

# Ensure DEBUG is false when testing HTTPS to catch any issues
DEBUG = True
