"""
Signal handlers for the legacy_sync app.
"""

# Import Django signals
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

# This file will contain signal handlers for synchronizing data with the legacy system
# For example, when a product is created or updated in the new system, we might want to
# push that data back to the legacy system. 