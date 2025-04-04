"""
Management command to synchronize product images from the external CMS.
This is a proxy to the actual implementation in pyerp.sync.management.commands.
"""
from pyerp.sync.management.commands.sync_product_images import Command

# This effectively makes this file a proxy for the main command implementation 