#!/usr/bin/env python
import os
import sys
import django

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pyerp.settings')
django.setup()

# Import the model after Django is set up
from pyerp.business_modules.inventory.models import StorageLocation

def main():
    # Count total records
    total_count = StorageLocation.objects.count()
    print(f"Total StorageLocation records: {total_count}")
    
    # Display a sample of records
    if total_count > 0:
        print("\nSample records:")
        for loc in StorageLocation.objects.all()[:10]:
            print(f"ID: {loc.id}, Legacy ID: {loc.legacy_id}, Name: {loc.name}")
    else:
        print("\nNo records found in the StorageLocation table.")
    
    # Check for records with specific legacy IDs
    sample_legacy_ids = ['201', '199', '170', '1511', '1641']
    print("\nChecking for specific legacy IDs:")
    for legacy_id in sample_legacy_ids:
        count = StorageLocation.objects.filter(legacy_id=legacy_id).count()
        print(f"Legacy ID {legacy_id}: {count} records")

if __name__ == "__main__":
    main() 