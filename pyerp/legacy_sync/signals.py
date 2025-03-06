"""
Signal handlers for the legacy_sync app.
"""

 # Import Django signals
from django.db.models.signals import post_save, post_delete  # noqa: F401
from django.dispatch import receiver  # noqa: F401

 # This file will contain signal handlers for synchronizing data with the legacy system  # noqa: E501
 # For example, when a product is created or updated in the new system, we might want to  # noqa: E501
 # push that data back to the legacy system.
