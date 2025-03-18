from django.core.management.base import BaseCommand
from pyerp.business_modules.inventory.models import StorageLocation


class Command(BaseCommand):
    help = "Check the StorageLocation table in the database"

    def handle(self, *args, **options):
        # Count total records
        total_count = StorageLocation.objects.count()
        self.stdout.write(f"Total StorageLocation records: {total_count}")

        # Display a sample of records
        if total_count > 0:
            self.stdout.write("\nSample records:")
            for loc in StorageLocation.objects.all()[:10]:
                self.stdout.write(
                    f"ID: {loc.id}, Legacy ID: {loc.legacy_id}, "
                    f"Location: {loc.country}-{loc.city_building}-"
                    f"{loc.unit}-{loc.compartment}-{loc.shelf}, "
                    f"Name: {loc.name}"
                )
        else:
            self.stdout.write("\nNo records found in the StorageLocation table.")

        # Check for records with specific legacy IDs
        sample_legacy_ids = ["201", "199", "170", "1511", "1641"]
        self.stdout.write("\nChecking for specific legacy IDs:")
        for legacy_id in sample_legacy_ids:
            locations = StorageLocation.objects.filter(legacy_id=legacy_id)
            count = locations.count()
            if count > 0:
                for loc in locations:
                    self.stdout.write(
                        f"Legacy ID {legacy_id}: "
                        f"Country: {loc.country}, "
                        f"City/Building: {loc.city_building}, "
                        f"Unit: {loc.unit}, "
                        f"Compartment: {loc.compartment}, "
                        f"Shelf: {loc.shelf}, "
                        f"Location Code: {loc.location_code}"
                    )
            else:
                self.stdout.write(f"Legacy ID {legacy_id}: No records found")

        # Check for potential duplicates (same unique constraint fields)
        self.stdout.write("\nChecking for potential duplicate constraints:")
        # Get counts by unique constraint combination
        from django.db.models import Count

        duplicates = (
            StorageLocation.objects.values(
                "country", "city_building", "unit", "compartment", "shelf"
            )
            .annotate(count=Count("id"))
            .filter(count__gt=1)
        )

        if duplicates.exists():
            self.stdout.write(
                f"Found {duplicates.count()} potentially problematic "
                f"unique constraint combinations:"
            )
            for dup in duplicates:
                self.stdout.write(
                    f"Combination: {dup['country']}-{dup['city_building']}-"
                    f"{dup['unit']}-{dup['compartment']}-{dup['shelf']} "
                    f"has {dup['count']} records"
                )
                # Show the specific records
                matches = StorageLocation.objects.filter(
                    country=dup["country"],
                    city_building=dup["city_building"],
                    unit=dup["unit"],
                    compartment=dup["compartment"],
                    shelf=dup["shelf"],
                )
                for match in matches:
                    self.stdout.write(
                        f"  - ID: {match.id}, Legacy ID: {match.legacy_id}, "
                        f"Name: {match.name}"
                    )
        else:
            self.stdout.write("No duplicate combinations found - all good!")
