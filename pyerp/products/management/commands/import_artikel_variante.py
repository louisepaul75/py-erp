"""
Management command to import product variants from the legacy Artikel_Variante table.  # noqa: E501
"""

import logging
import sys
from decimal import Decimal

import pandas as pd
from django.core.management.base import BaseCommand
from django.db import transaction

from pyerp.products.models import (
    ParentProduct,
    ProductCategory,
    VariantProduct,
)

# Configure logging
logger = logging.getLogger(__name__)

# Add the WSZ_api path to the Python path
WSZ_API_PATH = r"C:\Users\Joan-Admin\PycharmProjects\WSZ_api"
if WSZ_API_PATH not in sys.path:
    sys.path.append(WSZ_API_PATH)

try:
    from wsz_api.getTable import fetch_data_from_api
except ImportError as e:
    logger.error(f"Failed to import WSZ_api modules: {e}")
    raise


class Command(BaseCommand):
    help = "Import product variants from the legacy Artikel_Variante table"

    def add_arguments(self, parser):
        parser.add_argument(
            "--limit",
            type=int,
            default=None,
            help="Limit the number of variants to import",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Perform a dry run without saving to the database",
        )
        parser.add_argument(
            "--skip-existing",
            action="store_true",
            help="Skip variants that already exist in the database",
        )

    def handle(self, *args, **options):
        limit = options["limit"]
        dry_run = options["dry_run"]
        skip_existing = options["skip_existing"]

        self.stdout.write(self.style.NOTICE("Starting product variant import..."))

        # Create uncategorized category if it doesn't exist
        uncategorized, _ = ProductCategory.objects.get_or_create(
            code="UNCATEGORIZED",
            defaults={"name": "Uncategorized"},
        )

        try:
            self.stdout.write("Fetching data from Artikel_Variante table...")
            df = fetch_data_from_api(
                table_name="Artikel_Variante",
                top=limit,
                new_data_only=False,
            )

            self.stdout.write(self.style.SUCCESS(f"Fetched {len(df)} records"))

            # Track statistics
            stats = {
                "total": len(df),
                "created": 0,
                "skipped": 0,
                "errors": 0,
                "parent_not_found": 0,
            }

            # Process each variant
            for index, row in df.iterrows():
                try:
                    legacy_id = row["UID"]
                    alte_nummer = row["alteNummer"]
                    nummer = (
                        row["Nummer"]
                        if "Nummer" in row and pd.notna(row["Nummer"])
                        else None
                    )
                    bezeichnung = row["Bezeichnung"]
                    ref_old = row.get("refOld", None)

                    # Skip if the variant already exists and skip_existing is True
                    if (
                        skip_existing
                        and VariantProduct.objects.filter(legacy_id=legacy_id).exists()
                    ):
                        self.stdout.write(f"Skipping existing variant: {alte_nummer}")
                        stats["skipped"] += 1
                        continue

                    # Determine the primary SKU - use Nummer if available, otherwise fallback to alteNummer
                    primary_sku = str(nummer) if nummer is not None else alte_nummer

                    # Parse SKU and variant code - split by the last hyphen
                    if "-" in alte_nummer:
                        last_hyphen_index = alte_nummer.rfind("-")
                        base_sku = alte_nummer[
                            :last_hyphen_index
                        ]  # Everything before the last hyphen
                        variant_code = alte_nummer[
                            last_hyphen_index + 1 :
                        ]  # Everything after the last hyphen
                    else:
                        base_sku = alte_nummer
                        variant_code = ""

                    # Find parent product by base_sku
                    parent = None
                    if base_sku:
                        parent_candidates = ParentProduct.objects.filter(
                            base_sku=base_sku,
                        )
                        if parent_candidates.exists():
                            parent = parent_candidates.first()

                    if not parent and ref_old:
                        parent_candidates = ParentProduct.objects.filter(
                            legacy_id=str(ref_old),
                        )
                        if parent_candidates.exists():
                            parent = parent_candidates.first()

                    if not parent:
                        self.stdout.write(
                            self.style.WARNING(
                                f"Parent product not found for variant: {alte_nummer}",
                            ),
                        )
                        stats["parent_not_found"] += 1
                        continue  # Skip this variant since we need a parent

                    # Extract pricing information
                    list_price = Decimal("0.00")
                    cost_price = Decimal("0.00")

                    if "Preise" in row and row["Preise"] is not None:
                        prices = row["Preise"]
                        if isinstance(prices, dict) and "Coll" in prices:
                            for price_item in prices["Coll"]:
                                if isinstance(price_item, dict):
                                    if price_item.get("Art") == "Laden":
                                        list_price = Decimal(
                                            str(price_item.get("Preis", 0)),
                                        )
                                    elif price_item.get("Art") == "Einkauf":
                                        cost_price = Decimal(
                                            str(price_item.get("Preis", 0)),
                                        )

                    # Create variant data
                    variant_data = {
                        "sku": primary_sku,  # Use Nummer as primary SKU
                        "base_sku": base_sku,
                        "variant_code": variant_code,
                        "name": bezeichnung,
                        "legacy_id": legacy_id,
                        "legacy_sku": alte_nummer,  # Store alteNummer as legacy_sku
                        "parent": parent,
                        "list_price": list_price,
                        "cost_price": cost_price,
                        "category": parent.category,
                    }

                    # Print variant data in dry run mode
                    if dry_run:
                        self.stdout.write(f"Would create variant: {variant_data}")
                        stats["created"] += 1
                        continue

                    # Create or update the variant
                    with transaction.atomic():
                        variant, created = VariantProduct.objects.update_or_create(
                            legacy_id=legacy_id,
                            defaults=variant_data,
                        )

                        if created:
                            self.stdout.write(f"Created variant: {variant.sku}")
                        else:
                            self.stdout.write(f"Updated variant: {variant.sku}")

                        stats["created"] += 1

                except Exception as e:
                    self.stdout.write(
                        self.style.ERROR(f"Error processing variant {index}: {e!s}"),
                    )
                    stats["errors"] += 1

            # Print summary
            self.stdout.write(
                self.style.SUCCESS(
                    "\nImport summary:\n"
                    f"Total records: {stats['total']}\n"
                    f"Created/Updated: {stats['created']}\n"
                    f"Skipped: {stats['skipped']}\n"
                    f"Errors: {stats['errors']}\n"
                    f"Parent not found: {stats['parent_not_found']}",
                ),
            )

            if dry_run:
                self.stdout.write(
                    self.style.NOTICE(
                        "This was a dry run. No changes were made to the database.",
                    ),
                )

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"Error importing variants: {e!s}"),
            )
            raise
