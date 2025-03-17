"""
Management command to update parent products from the legacy ERP system.

This command fetches data from the Artikel_Familie table and updates the
corresponding ParentProduct records, ensuring that the Haengend and Einseitig
fields are correctly mapped to is_hanging and is_one_sided.
"""

import logging
import datetime

import pandas as pd
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from pyerp.business_modules.products.models import (
    ParentProduct,
    ProductCategory,
)
from pyerp.external_api.legacy_erp.client import LegacyERPClient

# Configure logging
logger = logging.getLogger(__name__)

# Disable SQL logging
db_logger = logging.getLogger('django.db.backends')
db_logger.setLevel(logging.ERROR)


class Command(BaseCommand):
    help = "Update parent products from the legacy ERP system"

    def add_arguments(self, parser):
        parser.add_argument(
            "--env",
            type=str,
            default="live",
            choices=["dev", "live"],
            help="Environment to use (dev or live)",
        )
        parser.add_argument(
            "--limit",
            type=int,
            help="Limit the number of records to process",
        )
        parser.add_argument(
            "--debug",
            action="store_true",
            help="Enable debug output",
        )

    def handle(self, *args, **options):
        """Execute the command."""
        # Store original logging level
        original_log_level = db_logger.level
        
        try:
            env = options.get("env", "dev")
            limit = options.get("limit")
            debug = options.get("debug", False)

            # Only enable SQL logging if debug is True
            if debug:
                db_logger.setLevel(original_log_level)
            else:
                db_logger.setLevel(logging.ERROR)

            self.stdout.write("Starting parent product update process")
            self.stdout.write(f"Environment: {env}")
            self.stdout.write(f"Limit: {limit}")
            self.stdout.write(f"Debug: {debug}")

            # Initialize statistics
            stats = {
                "total": 0,
                "created": 0,
                "updated": 0,
                "skipped": 0,
                "errors": 0,
            }

            # Initialize the API client
            try:
                client = LegacyERPClient(environment=env)
                self.stdout.write("API client initialized successfully")
            except Exception as e:
                self.stderr.write(f"Failed to initialize API client: {e}")
                return

            # Get or create default category outside the main transaction
            try:
                default_category = ProductCategory.objects.get(code="DEFAULT")
                self.stdout.write("Using existing default category")
            except ProductCategory.DoesNotExist:
                try:
                    default_category = ProductCategory.objects.create(
                        code="DEFAULT",
                        name="Default Category",
                        description="Default category for imported products",
                    )
                    self.stdout.write("Created default category")
                except Exception as e:
                    self.stderr.write(
                        f"Failed to create default category: {e}"
                    )
                    return

            # Fetch parent products from the legacy system
            try:
                self.stdout.write("Fetching parent products from Artikel_Familie table")
                df = client.fetch_table(
                    table_name="Artikel_Familie",
                    top=limit,
                    all_records=limit is None,
                )

                stats["total"] = len(df)
                self.stdout.write(f"Fetched {stats['total']} parent products")

                # Print the field names from the first record
                if len(df) > 0:
                    self.stdout.write("\nField names in the first record:")
                    for field_name in sorted(df.iloc[0].keys()):
                        self.stdout.write(f"  - {field_name}")

                    # Print the first record for debugging
                    if debug:
                        self.stdout.write("\nFirst record data:")
                        for field_name, value in df.iloc[0].items():
                            self.stdout.write(f"  {field_name}: {value}")

                # Process each parent product
                for _, row in df.iterrows():
                    # Process each parent product within its own transaction
                    try:
                        with transaction.atomic():
                            # Extract data from the row
                            familie_id = (
                                str(row["__KEY"]) if "__KEY" in row else None
                            )
                            nummer = (
                                str(row["Nummer"]) if "Nummer" in row else None
                            )

                            if not familie_id or not nummer:
                                self.stdout.write(
                                    "Skipping row - Missing ID or SKU: "
                                    f"{row}"
                                )
                                stats["skipped"] += 1
                                continue

                            # Extract additional fields
                            bezeichnung = row.get("Bezeichnung", "")
                            bezeichnung_fs = row.get("Bezeichnung_ENG", {})
                            beschreibung = row.get("Beschreibung", {})
                            gewicht = (
                                float(row["Gewicht"])
                                if pd.notna(row.get("Gewicht"))
                                else 0
                            )
                            masse_breite = (
                                float(row["Masse_Breite"])
                                if pd.notna(row.get("Masse_Breite"))
                                else None
                            )
                            masse_hoehe = (
                                float(row["Masse_Hoehe"])
                                if pd.notna(row.get("Masse_Hoehe"))
                                else None
                            )
                            masse_tiefe = (
                                float(row["Masse_Tiefe"])
                                if pd.notna(row.get("Masse_Tiefe"))
                                else None
                            )
                            release_date = row.get("Release_date")
                            neu = row.get("neu", False)
                            aktiv = True  # Default to active

                            # Map Haengend to is_hanging
                            haengend = bool(row.get("Haengend", False))
                            if debug:
                                self.stdout.write(
                                    f"Haengend field value: "
                                    f"{row.get('Haengend', 'Not found')}"
                                )

                            # Map Einseitig to is_one_sided
                            einseitig = bool(row.get("Einseitig", False))
                            if debug:
                                self.stdout.write(
                                    f"Einseitig field value: "
                                    f"{row.get('Einseitig', 'Not found')}"
                                )

                            # Add debug logging for these fields
                            if debug:
                                self.stdout.write(
                                    f"Product {nummer} - "
                                    f"is_hanging: {haengend}, "
                                    f"is_one_sided: {einseitig}"
                                )
                                self.stdout.write(
                                    "Available fields: "
                                    f"{list(row.keys())}"
                                )

                            # Try to find category from ArtGr
                            category = default_category
                            art_gr = row.get("ArtGr")
                            if art_gr:
                                try:
                                    category = ProductCategory.objects.get(code=art_gr)
                                except ProductCategory.DoesNotExist:
                                    try:
                                        category = ProductCategory.objects.create(
                                            code=art_gr,
                                            name=art_gr,
                                            description=(
                                                "Category imported from legacy "
                                                f"system with code {art_gr}"
                                            ),
                                        )
                                        self.stdout.write(
                                            f"Created new category: {art_gr}"
                                        )
                                    except Exception as e:
                                        self.stderr.write(
                                            f"Failed to create category {art_gr}: {e}"
                                        )
                                        category = default_category

                            # Prepare data for parent product
                            parent_data = {
                                'name': bezeichnung,
                                'description': (
                                    beschreibung.get('DE', '')
                                    if isinstance(beschreibung, dict)
                                    else beschreibung
                                ),
                                'description_en': bezeichnung_fs.get('EN', ''),
                                'weight': gewicht,
                                'dimensions': (
                                    f"{masse_tiefe}x{masse_breite}x{masse_hoehe}"
                                    if all([masse_tiefe, masse_breite, masse_hoehe])
                                    else ''
                                ),
                                'is_active': aktiv,
                                'is_hanging': haengend,
                                'is_one_sided': einseitig,
                                'category': category,
                                'release_date': release_date,
                                'is_new': neu,
                            }

                            # Try to get existing parent product by legacy_id and sku
                            try:
                                parent_product, created = ParentProduct.objects.get_or_create(
                                    legacy_id=familie_id,
                                    sku=nummer,
                                    defaults=parent_data
                                )

                                if not created:
                                    # Update existing product with new data
                                    for key, value in parent_data.items():
                                        setattr(parent_product, key, value)
                                    parent_product.save()
                                    stats['updated'] += 1
                                else:
                                    stats['created'] += 1

                            except Exception as e:
                                error_msg = f"Error processing parent product: {str(e)}"
                                logger.error(error_msg)
                                logger.error(f"Row data: {row}")
                                stats['errors'] += 1
                                continue

                    except Exception as e:
                        stats["errors"] += 1
                        self.stderr.write(
                            f"Error processing parent product: {e}"
                        )
                        if debug:
                            self.stderr.write(f"Row data: {row}")
                        continue

            except Exception as e:
                self.stderr.write(f"Error fetching parent products: {e}")
                return

            # Print summary
            self.stdout.write("\nSummary:")
            self.stdout.write(f"Total records: {stats['total']}")
            self.stdout.write(f"Created: {stats['created']}")
            self.stdout.write(f"Updated: {stats['updated']}")
            self.stdout.write(f"Skipped: {stats['skipped']}")
            self.stdout.write(f"Errors: {stats['errors']}")
        finally:
            # Restore original logging level
            db_logger.setLevel(original_log_level)
