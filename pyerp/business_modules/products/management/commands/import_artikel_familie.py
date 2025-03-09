from contextlib import suppress
from typing import Any

from django.core.management.base import BaseCommand
from django.db import transaction

from pyerp.business_modules.products.models import ParentProduct, ProductCategory


class Command(BaseCommand):
    """Command to import Artikel_Familie records as parent products."""

    help = "Import Artikel_Familie records as parent products"

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Show what would be done without making changes",
        )
        parser.add_argument(
            "--limit",
            type=int,
            help="Maximum number of records to process",
        )
        parser.add_argument(
            "--skip-existing",
            action="store_true",
            help="Skip records that already exist",
        )

    def handle(self, *args: Any, **options: Any) -> None:
        """Import Artikel_Familie records as parent products.

        Args:
            *args: Variable length argument list
            **options: Arbitrary keyword arguments:
                - dry_run: Run without making changes
                - limit: Max records to process
                - skip_existing: Skip existing records

        Returns:
            None
        """
        limit = options.get("limit")
        skip_existing = options.get("skip_existing", False)
        dry_run = options.get("dry_run", False)

        self.import_artikel_familie(
            limit=limit,
            skip_existing=skip_existing,
            dry_run=dry_run,
        )

    def import_artikel_familie(
        self,
        *,
        limit: int | None = None,
        skip_existing: bool = False,
        dry_run: bool = False,
    ) -> None:
        """Import Artikel_Familie records as parent products.

        Args:
            limit: Maximum number of records to process
            skip_existing: Skip records that already exist
            dry_run: Run without making changes

        Returns:
            None
        """
        try:
            from wsz_api.getTable import fetch_data_from_api
        except ImportError as e:
            self.stderr.write(f"Failed to import WSZ_api: {e}")
            return

        # Optimize queryset to reduce SQL queries
        df = fetch_data_from_api("Artikel_Familie", limit=limit)
        if df is None or df.empty:
            self.stderr.write("No data received from API")
            return

        # Use select_related and prefetch_related to optimize queries
        categories = ProductCategory.objects.all()
        category_map = {cat.code: cat for cat in categories}

        record_count = len(df)
        self.stdout.write(f"Retrieved {record_count} records")

        # Process records in batches
        batch_size = 100  # Define a suitable batch size
        records = []

        created = 0
        skipped = 0
        errors = 0

        with transaction.atomic():
            for _, row in df.iterrows():
                try:
                    # Get required fields
                    nummer = row.get("Nummer", "").strip()
                    if not nummer:
                        self.stderr.write(f"Skipping row {row.name}: No Nummer")
                        skipped += 1
                        continue

                    # Get optional fields with defaults
                    name = row.get("Name", "").strip()
                    description = str(row.get("Beschreibung", ""))
                    category_code = row.get("Gruppe", "").strip()

                    # Find category if provided
                    category = category_map.get(category_code)

                    # Prepare record for bulk operation
                    defaults = {
                        "name": name,
                        "description": description,
                        "category": category,
                    }
                    records.append(ParentProduct(sku=nummer, **defaults))

                    # Process batch if size is reached
                    if len(records) >= batch_size:
                        if not dry_run:
                            ParentProduct.objects.bulk_create(records, ignore_conflicts=True)
                            created += len(records)
                        records.clear()

                except Exception as e:
                    err_msg = f"Error processing row {row.name}: {e}"
                    self.stderr.write(err_msg)
                    errors += 1

            # Process any remaining records
            if records and not dry_run:
                ParentProduct.objects.bulk_create(records, ignore_conflicts=True)
                created += len(records)

        # Print summary
        summary = (
            f"\nProcessed {record_count} records: "
            f"Created {created}, "
            f"Skipped {skipped}, "
            f"Errors {errors}"
        )
        self.stdout.write(self.style.SUCCESS(summary))

        if dry_run:
            dry_run_msg = "This was a dry run - no changes made."
            self.stdout.write(self.style.WARNING(dry_run_msg))
