from django.core.management.base import BaseCommand
from pyerp.business_modules.inventory.models import StorageLocation

class Command(BaseCommand):
    help = 'Check the StorageLocation table in the database'

    def handle(self, *args, **options):
        # Count total records
        total_count = StorageLocation.objects.count()
        self.stdout.write(f"Total StorageLocation records: {total_count}")
        
        # Display a sample of records
        if total_count > 0:
            self.stdout.write("\nSample records:")
            for loc in StorageLocation.objects.all()[:10]:
                self.stdout.write(f"ID: {loc.id}, Legacy ID: {loc.legacy_id}, Name: {loc.name}")
        else:
            self.stdout.write("\nNo records found in the StorageLocation table.")
        
        # Check for records with specific legacy IDs
        sample_legacy_ids = ['201', '199', '170', '1511', '1641']
        self.stdout.write("\nChecking for specific legacy IDs:")
        for legacy_id in sample_legacy_ids:
            count = StorageLocation.objects.filter(legacy_id=legacy_id).count()
            self.stdout.write(f"Legacy ID {legacy_id}: {count} records") 