"""
Management command to import products from a CSV file.
"""

from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Import products from a CSV file"

    def add_arguments(self, parser):
        parser.add_argument("file_path", type=str, help="Path to the CSV file")

    def handle(self, *args, **options):
        file_path = options["file_path"]
        self.stdout.write(f"Importing products from {file_path}")
        # Actual import logic would go here
        self.stdout.write(self.style.SUCCESS("Successfully imported products"))
