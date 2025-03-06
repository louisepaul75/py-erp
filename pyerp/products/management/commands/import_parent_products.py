"""Management command to import parent products from the Art_Kalkulation table."""

import logging
from typing import Any

import pandas as pd
from django.core.management.base import BaseCommand, CommandError
from django.db.models import Q

from pyerp.products.models import Product, ProductCategory
from wsz_api.getTable import fetch_data_from_api

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = (
        "Import parent products from the Art_Kalkulation table in the legacy 4D system"
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--limit",
            type=int,
            default=0,
            help="Limit the number of parent products to import",
        )
        parser.add_argument(
            "--update",
            action="store_true",
            help="Update existing parent products",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Perform a dry run without saving to the database",
        )
        parser.add_argument(
            "--debug",
            action="store_true",
            help="Print debug information",
        )
        parser.add_argument(
            "--force",
            action="store_true",
            help="Create parent products even if they have no variants",
        )

    def handle(self, *args: Any, **options: dict[str, Any]) -> None:
        """Handle command execution."""
        self.stdout.write(
            "Starting parent product import from Art_Kalkulation table...",
        )

        # Command options
        self.limit = options["limit"]
        self.update = options["update"]
        self.dry_run = options["dry_run"]
        self.debug = options["debug"]
        self.force = options["force"]

        # Get or create default category
        self.default_category, _ = ProductCategory.objects.get_or_create(
            code="UNCATEGORIZED",
            defaults={
                "name": "Uncategorized",
                "description": "Default category for products without a specific category",
            },
        )

        # Fetch data from Art_Kalkulation
        self.stdout.write("Fetching data from Art_Kalkulation table...")
        try:
            df = fetch_data_from_api(
                table_name="Art_Kalkulation",
                new_data_only=False,
            )

            if df is None or len(df) == 0:
                error_message = "No data returned from Art_Kalkulation table"
                raise CommandError(error_message)

            self.stdout.write(f"Retrieved {len(df)} parent product records")

            # Limit the number of records to process if specified
            if self.limit > 0:
                df = df.head(self.limit)
                self.stdout.write(f"Limited to {len(df)} records")

            # Process data
            self.process_parent_products(df)

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error: {e!s}"))
            import traceback

            self.stdout.write(traceback.format_exc())

    def get_value(self, row, column, default=None):
        """
        Safely get a value from a DataFrame row.
        """
        if column in row and pd.notna(row[column]):
            return row[column]
        return default

    def process_parent_products(self, df):
        """
        Process parent product records from the Art_Kalkulation table.
        """
        total = len(df)
        created = 0
        updated = 0
        skipped = 0
        orphaned = 0

        self.stdout.write(f"Processing {total} parent product records...")

        # Process each row
        for idx, row in df.iterrows():
            if self.debug and idx % 100 == 0:
                self.stdout.write(f"Processing record {idx + 1} of {total}...")

            try:
                result = self.process_parent_product(row)

                if result == "created":
                    created += 1
                elif result == "updated":
                    updated += 1
                elif result == "skipped":
                    skipped += 1
                elif result == "orphaned":
                    orphaned += 1

            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f"Error processing record {idx}: {e!s}"),
                )
                if self.debug:
                    import traceback

                    self.stdout.write(traceback.format_exc())
                skipped += 1

        # Print summary
        self.stdout.write(
            self.style.SUCCESS(f"Processed {total} parent product records:"),
        )
        self.stdout.write(f"  - Created: {created}")
        self.stdout.write(f"  - Updated: {updated}")
        self.stdout.write(f"  - Skipped: {skipped}")
        self.stdout.write(f"  - Orphaned (no variants): {orphaned}")

    def process_parent_product(self, row):
        """
        Process a single parent product record from Art_Kalkulation.

        Returns:
        - 'created': A new parent product was created
        - 'updated': An existing parent product was updated
        - 'skipped': The record was skipped
        - 'orphaned': Parent product has no variants
        """
        parent_sku = self.get_value(row, "ArtNr_Kalk", "")
        legacy_id = self.get_value(row, "ID", "")

        # Skip if no valid SKU
        if not parent_sku:
            if self.debug:
                self.stdout.write("  Skipping row - No valid SKU")
            return "skipped"

        # Check if we already have this product as a parent
        existing_parent = (
            Product.objects.filter(
                (
                    Q(sku=parent_sku) | Q(legacy_id=str(legacy_id))
                    if legacy_id
                    else Q(sku=parent_sku)
                ),
            )
            .filter(is_parent=True)
            .first()
        )

        # Check for variants that might be associated with this parent
        variants = Product.objects.filter(base_sku=parent_sku, is_parent=False)
        variant_count = variants.count()

        if variant_count == 0 and not self.update and not self.force:
            if self.debug:
                self.stdout.write(
                    f"  Skipping orphaned parent {parent_sku} - No variants exist",
                )
            return "orphaned"

        # Extract additional fields
        name = self.get_value(row, "Bezeichnung", "")
        short_name = self.get_value(row, "Bez_kurz", "")
        dimensions = self.get_value(row, "Masse", "")
        weight = self.get_value(row, "Gewicht", 0)
        is_hanging = bool(self.get_value(row, "haengen", False))
        is_one_sided = bool(self.get_value(row, "eineSeite", False))
        art_gr = self.get_value(row, "ArtGr", "")

        # Try to find category from ArtGr
        category = self.default_category
        if art_gr:
            try:
                category_obj = ProductCategory.objects.get(code=art_gr)
                category = category_obj
            except ProductCategory.DoesNotExist:
                category_name = art_gr  # Use code as name if no mapping exists
                category = ProductCategory.objects.create(
                    code=art_gr,
                    name=category_name,
                    description=f"Category imported from legacy system with code {art_gr}",
                )

        # Create parent product data dictionary
        parent_data = {
            "sku": parent_sku,
            "base_sku": parent_sku,  # For a parent, sku and base_sku are the same
            "variant_code": "",  # No variant code for parent
            "name": name,
            "short_description": short_name,
            "dimensions": dimensions,
            "weight": weight,
            "is_parent": True,
            "is_hanging": is_hanging,
            "is_one_sided": is_one_sided,
            "category": category,
            "legacy_id": str(legacy_id) if legacy_id else None,
        }

        # Create or update parent product
        if existing_parent:
            if not self.update:
                if self.debug:
                    self.stdout.write(
                        f"  Skipping existing parent {parent_sku} (update not enabled)",
                    )
                return "skipped"

            # Update existing parent product
            for key, value in parent_data.items():
                setattr(existing_parent, key, value)

            if not self.dry_run:
                existing_parent.save()

            if self.debug:
                self.stdout.write(f"  Updated parent product: {parent_sku}")

            # Associate variants with this parent
            self.associate_variants(existing_parent, variants)

            return "updated"
        parent_product = Product(**parent_data)

        if not self.dry_run:
            parent_product.save()

        if self.debug:
            self.stdout.write(f"  Created parent product: {parent_sku}")

        # Associate variants with this parent
        self.associate_variants(parent_product, variants)

        return "created"

    def associate_variants(self, parent, variants):
        """
        Associate variant products with their parent.
        """
        if self.dry_run:
            return

        count = 0
        for variant in variants:
            if variant.parent != parent:
                variant.parent = parent
                variant.save()
                count += 1

        if count > 0 and self.debug:
            self.stdout.write(f"  Associated {count} variants with parent {parent.sku}")
