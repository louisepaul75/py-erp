from contextlib import suppress
from typing import Any

from django.core.management.base import BaseCommand
from django.db import transaction

from pyerp.products.models import ParentProduct, ProductCategory


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

        # Get data from API
        df = fetch_data_from_api("Artikel_Familie", limit=limit)
        if df is None or df.empty:
            self.stderr.write("No data received from API")
            return

        record_count = len(df)
        self.stdout.write(f"Retrieved {record_count} records")

        # Process records
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
                    try:
                        if isinstance(row["Beschreibung"], str):
                            description = row["Beschreibung"]
                        else:
                            description = str(row["Beschreibung"])
                    except (KeyError, TypeError, ValueError):
                        description = str(row.get("Beschreibung", ""))

                    category_code = row.get("Gruppe", "").strip()

                    # Find category if provided
                    category = None
                    if category_code:
                        with suppress(ProductCategory.DoesNotExist):
                            category = ProductCategory.objects.get(
                                code=category_code,
                            )

                    # Create or update parent product
                    if not dry_run:
                        defaults = {
                            "name": name,
                            "description": description,
                            "category": category,
                        }
                        result = ParentProduct.objects.update_or_create(
                            sku=nummer,
                            defaults=defaults,
                        )
                        parent, is_created = result
                        if is_created:
                            created += 1
                        else:
                            skipped += 1
                    else:
                        self.stdout.write(f"Would create parent: {nummer} - {name}")

                except Exception as e:
                    err_msg = f"Error processing row {row.name}: {e}"
                    self.stderr.write(err_msg)
                    errors += 1

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
