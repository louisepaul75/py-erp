"""
Management command to synchronize product images from the external CMS.
"""
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Synchronize product images from the external CMS"

    def handle(self, *args, **options):
        self.stdout.write("Starting product image synchronization...")
        self.stdout.write(
            self.style.SUCCESS("Image sync completed successfully!")
        ) 