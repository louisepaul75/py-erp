"""
Minimal test command.
"""
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Test command to check command discovery"

    def handle(self, *args, **options):
        self.stdout.write("Test command successfully executed!") 