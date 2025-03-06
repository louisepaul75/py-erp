"""
HTTPS settings for pyERP project.

Import this file in your development or local settings to enable proper HTTPS support.  # noqa: E501
"""

# This tells Django to trust the X-Forwarded-Proto header from the proxy server
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
  # noqa: F841

# Disable Django's own SSL redirect as Nginx is handling this
SECURE_SSL_REDIRECT = False
  # noqa: F841

# Set cookies as secure since we're using HTTPS
SESSION_COOKIE_SECURE = True
  # noqa: F841
CSRF_COOKIE_SECURE = True
  # noqa: F841

# Other security settings
SECURE_HSTS_SECONDS = 0
  # noqa: F841
SECURE_HSTS_INCLUDE_SUBDOMAINS = False
  # noqa: F841
SECURE_HSTS_PRELOAD = False
  # noqa: F841

# Ensure DEBUG is false when testing HTTPS to catch any issues
DEBUG = True
  # noqa: F841
