"""
Management command to update variant products from the legacy ERP system.

This command fetches data from the Artikel_Variante table and updates the
corresponding VariantProduct records, ensuring that all fields are correctly
mapped from the legacy system.
"""

import logging
from datetime import datetime

import pandas as pd
from django.core.management.base import BaseCommand
from django.db import transaction
from django.db.models import Q

from pyerp.business_modules.products.models import (
    ParentProduct,
    VariantProduct,
)
from pyerp.external_api.legacy_erp.client import LegacyERPClient

# Configure logging
logger = logging.getLogger(__name__)

# Disable SQL logging
db_logger = logging.getLogger('django.db.backends')
db_logger.setLevel(logging.ERROR)


def parse_legacy_date(date_str):
    """Parse a date string from the legacy system format (DD!MM!YYYY)."""
    if not date_str or date_str == "0!0!0":
        return None
    try:
        day, month, year = map(int, date_str.split("!"))
        return datetime(year, month, day)
    except (ValueError, AttributeError):
        return None


def bool_to_int(value):
    """Convert a boolean value to an integer (1 or 0)."""
    if isinstance(value, bool):
        return 1 if value else 0
    return value


class Command(BaseCommand):
    help = "Update variant products from the legacy ERP system"

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

            self.stdout.write("Starting variant product update process")
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
                "parent_not_found": 0,
            }

            # Initialize the API client
            try:
                client = LegacyERPClient(environment=env)
                self.stdout.write("API client initialized successfully")
            except Exception as e:
                self.stderr.write(f"Failed to initialize API client: {e}")
                return

            # Fetch variant products from the legacy system
            try:
                self.stdout.write(
                    "Fetching variant products from Artikel_Variante table"
                )
                df = client.fetch_table(
                    table_name="Artikel_Variante",
                    top=limit,
                    all_records=limit is None,
                )

                stats["total"] = len(df)
                self.stdout.write(
                    f"Fetched {stats['total']} variant products"
                )

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

                # Process each variant product
                for _, row in df.iterrows():
                    # Process each variant product within its own transaction
                    try:
                        with transaction.atomic():
                            # Extract data from the row
                            variant_id = (
                                str(row["__KEY"]) if "__KEY" in row else None
                            )
                            nummer = (
                                str(row["Nummer"]) if "Nummer" in row else None
                            )
                            familie_id = (
                                str(row["Familie_"]) if "Familie_" in row else None
                            )

                            if not variant_id or not nummer:
                                self.stdout.write(
                                    "Skipping row - Missing ID or SKU: "
                                    f"{row}"
                                )
                                stats["skipped"] += 1
                                continue

                            # Find parent product
                            parent = None
                            if familie_id:
                                try:
                                    parent = ParentProduct.objects.get(
                                        legacy_id=familie_id
                                    )
                                except ParentProduct.DoesNotExist:
                                    self.stdout.write(
                                        f"Parent product not found for "
                                        f"familie_id: {familie_id}"
                                    )
                                    stats["parent_not_found"] += 1

                            # Extract additional fields
                            name = row.get("Bezeichnung", "")
                            name_en = row.get("Bezeichnung_ENG", "")
                            description = row.get("Beschreibung", "")
                            if description is None:
                                description = {'DE': ''}
                            description_en = row.get("Beschreibung_ENG", "")
                            short_description = row.get("Bez_kurz", "")
                            base_sku = row.get("fk_ArtNr", nummer)
                            legacy_sku = row.get("alteNummer")
                            variant_code = row.get("ArtikelArt", "")

                            # Physical attributes
                            weight = (
                                float(row["Gewicht"])
                                if pd.notna(row.get("Gewicht"))
                                else None
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

                            # Pricing
                            retail_price = None
                            wholesale_price = None
                            retail_unit = None
                            wholesale_unit = None

                            # Extract pricing information from Preise.Coll array
                            prices = row.get("Preise.Coll", [])
                            if isinstance(prices, dict) and "Coll" in prices:
                                prices = prices["Coll"]
                            if isinstance(prices, list):
                                for price in prices:
                                    if isinstance(price, dict):
                                        price_type = price.get("Art")
                                        if price_type == "Laden":
                                            retail_price = (
                                                float(price["Preis"])
                                                if pd.notna(price.get("Preis"))
                                                else None
                                            )
                                            retail_unit = (
                                                int(price["VE"])
                                                if pd.notna(price.get("VE"))
                                                else None
                                            )
                                        elif price_type == "Handel":
                                            wholesale_price = (
                                                float(price["Preis"])
                                                if pd.notna(price.get("Preis"))
                                                else None
                                            )
                                            wholesale_unit = (
                                                int(price["VE"])
                                                if pd.notna(price.get("VE"))
                                                else None
                                            )

                            # Status fields
                            is_active = bool_to_int(row.get("Aktiv", True))
                            is_verkaufsartikel = bool_to_int(
                                row.get("Verkaufsartikel", False)
                            )
                            release_date = parse_legacy_date(
                                row.get("Release_Date")
                            )
                            auslaufdatum = parse_legacy_date(
                                row.get("Auslaufdatum")
                            )

                            # Check if variant product exists
                            existing_variant = VariantProduct.objects.filter(
                                Q(sku=nummer) | Q(legacy_id=variant_id)
                            ).first()

                            # Create variant product data dictionary
                            variant_data = {
                                "sku": nummer,
                                "base_sku": base_sku,
                                "legacy_id": variant_id,
                                "legacy_sku": legacy_sku,
                                "legacy_familie": familie_id,
                                "parent": parent,
                                "variant_code": variant_code,
                                "name": name,
                                "name_en": name_en,
                                "description": description,
                                "description_en": description_en,
                                "short_description": short_description,
                                "is_active": is_active,
                                "is_verkaufsartikel": is_verkaufsartikel,
                                "release_date": release_date,
                                "auslaufdatum": auslaufdatum,
                                "retail_price": retail_price,
                                "wholesale_price": wholesale_price,
                                "retail_unit": retail_unit,
                                "wholesale_unit": wholesale_unit,
                                # Convert kg to grams
                                "weight_grams": weight * 1000 if weight else None,
                                "length_mm": depth,  # Map Tiefe to length
                                "width_mm": width,
                                "height_mm": height,
                            }

                            # Create or update variant product
                            if existing_variant:
                                for key, value in variant_data.items():
                                    setattr(existing_variant, key, value)
                                existing_variant.save()
                                stats["updated"] += 1
                                if debug:
                                    self.stdout.write(
                                        f"Updated variant product: {nummer}"
                                    )
                            else:
                                variant = VariantProduct(**variant_data)
                                variant.save()
                                stats["created"] += 1
                                if debug:
                                    self.stdout.write(
                                        f"Created variant product: {nummer}"
                                    )

                    except Exception as e:
                        stats["errors"] += 1
                        self.stderr.write(
                            f"Error processing variant product: {e}"
                        )
                        if debug:
                            self.stderr.write(f"Row data: {row}")
                        continue

            except Exception as e:
                self.stderr.write(f"Error fetching variant products: {e}")
                return

            # Print summary
            self.stdout.write("\nSummary:")
            self.stdout.write(f"Total records: {stats['total']}")
            self.stdout.write(f"Created: {stats['created']}")
            self.stdout.write(f"Updated: {stats['updated']}")
            self.stdout.write(f"Skipped: {stats['skipped']}")
            self.stdout.write(f"Parent not found: {stats['parent_not_found']}")
            self.stdout.write(f"Errors: {stats['errors']}")
        finally:
            # Restore original logging level
            db_logger.setLevel(original_log_level) 