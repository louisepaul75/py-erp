import os
import django
import sys

# Set up Django environment
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "pyerp.settings")
django.setup()

from django.core.management import call_command

# Call the management command
call_command('sync_product_images', limit=3, page_size=20) 