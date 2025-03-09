"""
Management command to update parent products from the legacy ERP system.

This command fetches data from the Artikel_Familie table and updates the
corresponding ParentProduct records, ensuring that the Haengend and Einseitig
fields are correctly mapped to is_hanging and is_one_sided.
"""

import logging

import pandas as pd
from django.core.management.base import BaseCommand
from django.db import transaction
from django.db.models import Q

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
            default="dev",
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
                            name = row.get("Bezeichnung", "")
                            name_en = row.get("Bezeichnung_ENG", "")
                            description = row.get("Beschreibung", "")
                            if description is None:
                                description = {'DE': ''}
                            description_en = row.get("Beschreibung_ENG", "")
                            short_description = row.get("Bez_kurz", "")
                            art_gr = row.get("ArtGr", "")

                            # Physical attributes
                            weight = (
                                float(row["Gewicht"])
                                if pd.notna(row.get("Gewicht"))
                                else 0
                            )
                            width = (
                                float(row["Masse_Breite"])
                                if pd.notna(row.get("Masse_Breite"))
                                else None
                            )
                            height = (
                                float(row["Masse_Hoehe"])
                                if pd.notna(row.get("Masse_Hoehe"))
                                else None
                            )
                            depth = (
                                float(row["Masse_Tiefe"])
                                if pd.notna(row.get("Masse_Tiefe"))
                                else None
                            )

                            # Boolean flags
                            is_active = True  # Default to active

                            # Map Haengend to is_hanging
                            is_hanging = bool(row.get("Haengend", False))
                            if debug:
                                self.stdout.write(
                                    f"Haengend field value: "
                                    f"{row.get('Haengend', 'Not found')}"
                                )

                            # Map Einseitig to is_one_sided
                            is_one_sided = bool(row.get("Einseitig", False))
                            if debug:
                                self.stdout.write(
                                    f"Einseitig field value: "
                                    f"{row.get('Einseitig', 'Not found')}"
                                )

                            # Add debug logging for these fields
                            if debug:
                                self.stdout.write(
                                    f"Product {nummer} - "
                                    f"is_hanging: {is_hanging}, "
                                    f"is_one_sided: {is_one_sided}"
                                )
                                self.stdout.write(
                                    "Available fields: "
                                    f"{list(row.keys())}"
                                )

                            # Try to find category from ArtGr
                            category = default_category
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

                            # Check if parent product exists
                            existing_parent = ParentProduct.objects.filter(
                                Q(sku=nummer) | Q(legacy_id=familie_id)
                            ).first()

                            # Create parent product data dictionary
                            parent_data = {
                                "sku": nummer,
                                "base_sku": nummer,
                                "legacy_id": familie_id,
                                "name": name,
                                "name_en": name_en,
                                "short_description": short_description,
                                "description": description,
                                "description_en": description_en,
                                "weight": weight,
                                "is_active": is_active,
                                "is_one_sided": is_one_sided,
                                "is_hanging": is_hanging,
                                "category": category,
                            }

                            # Add dimensions if available
                            if all(x is not None for x in [width, height, depth]):
                                parent_data["dimensions"] = (
                                    f"{width}x{height}x{depth}"
                                )

                            # Create or update parent product
                            if existing_parent:
                                for key, value in parent_data.items():
                                    setattr(existing_parent, key, value)
                                existing_parent.save()
                                stats["updated"] += 1
                                if debug:
                                    self.stdout.write(
                                        f"Updated parent product: {nummer}"
                                    )
                            else:
                                parent = ParentProduct(**parent_data)
                                parent.save()
                                stats["created"] += 1
                                if debug:
                                    self.stdout.write(
                                        f"Created parent product: {nummer}"
                                    )

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
