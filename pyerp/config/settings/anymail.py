"""
Django Anymail settings for pyERP.

This module contains settings for configuring email delivery through various
email service providers using django-anymail.

For more information on django-anymail settings, see:
https://anymail.readthedocs.io/en/stable/installation/
"""

import os

# Anymail settings
ANYMAIL = {
    # Default ESP (Email Service Provider)
    # Change this to the ESP you want to use: "sendgrid", "mailgun", "mailjet", etc.
    "ESP_NAME": os.environ.get("ANYMAIL_ESP", "sendgrid"),
    
    # SendGrid settings
    "SENDGRID_API_KEY": os.environ.get("SENDGRID_API_KEY", ""),
    
    # Mailgun settings
    "MAILGUN_API_KEY": os.environ.get("MAILGUN_API_KEY", ""),
    "MAILGUN_SENDER_DOMAIN": os.environ.get("MAILGUN_DOMAIN", ""),
    "MAILGUN_API_URL": os.environ.get("MAILGUN_API_URL", "https://api.mailgun.net/v3"),
    
    # Mailjet settings
    "MAILJET_API_KEY": os.environ.get("MAILJET_API_KEY", ""),
    "MAILJET_SECRET_KEY": os.environ.get("MAILJET_SECRET_KEY", ""),
    
    # Amazon SES settings
    "AMAZON_SES_CLIENT_PARAMS": {
        "aws_access_key_id": os.environ.get("AWS_ACCESS_KEY_ID", ""),
        "aws_secret_access_key": os.environ.get("AWS_SECRET_ACCESS_KEY", ""),
        "region_name": os.environ.get("AWS_SES_REGION_NAME", "us-east-1"),
    },
    
    # Postmark settings
    "POSTMARK_SERVER_TOKEN": os.environ.get("POSTMARK_SERVER_TOKEN", ""),
    
    # SparkPost settings
    "SPARKPOST_API_KEY": os.environ.get("SPARKPOST_API_KEY", ""),
    
    # SMTP settings (for generic SMTP providers)
    "SMTP_HOST": os.environ.get("EMAIL_HOST", ""),
    "SMTP_PORT": int(os.environ.get("EMAIL_PORT", 587)),
    "SMTP_USERNAME": os.environ.get("EMAIL_HOST_USER", ""),
    "SMTP_PASSWORD": os.environ.get("EMAIL_HOST_PASSWORD", ""),
    "SMTP_USE_TLS": os.environ.get("EMAIL_USE_TLS", "True").lower() == "true",
    "SMTP_USE_SSL": os.environ.get("EMAIL_USE_SSL", "False").lower() == "true",
    
    # Common settings for all ESPs
    "DEBUG_API_REQUESTS": os.environ.get("ANYMAIL_DEBUG", "").lower() == "true",
}

# Set the default from email address
DEFAULT_FROM_EMAIL = os.environ.get("DEFAULT_FROM_EMAIL", "noreply@example.com")
SERVER_EMAIL = os.environ.get("SERVER_EMAIL", DEFAULT_FROM_EMAIL)

# Email tracking settings
ANYMAIL_TRACK_OPENS = os.environ.get("ANYMAIL_TRACK_OPENS", "").lower() == "true"
ANYMAIL_TRACK_CLICKS = os.environ.get("ANYMAIL_TRACK_CLICKS", "").lower() == "true"

# Email template settings
ANYMAIL_TEMPLATE_CONTEXT = {}

# Standard Django email settings (used for SMTP and as fallback)
EMAIL_HOST = os.environ.get("EMAIL_HOST", "")
EMAIL_PORT = int(os.environ.get("EMAIL_PORT", 587))
EMAIL_HOST_USER = os.environ.get("EMAIL_HOST_USER", "")
EMAIL_HOST_PASSWORD = os.environ.get("EMAIL_HOST_PASSWORD", "")
EMAIL_USE_TLS = os.environ.get("EMAIL_USE_TLS", "True").lower() == "true"
EMAIL_USE_SSL = os.environ.get("EMAIL_USE_SSL", "False").lower() == "true" 