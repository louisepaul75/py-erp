"""
Management command to import product variants from the legacy Artikel_Variante table.  # noqa: E501
"""

import logging
from decimal import Decimal

import pandas as pd
from django.core.management.base import BaseCommand
from django.db import transaction

from pyerp.direct_api.scripts.getTable import SimpleAPIClient
from pyerp.products.models import (
    ParentProduct,
    ProductCategory,
    VariantProduct,
)

# Configure logging
logger = logging.getLogger(__name__)


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
        parser.add_argument(
            "--debug-prices",
            action="store_true",
            help="Show detailed price information for debugging",
        )

    def handle(self, *args, **options):
        limit = options["limit"]
        dry_run = options["dry_run"]
        skip_existing = options["skip_existing"]
        debug_prices = options["debug_prices"]

        self.stdout.write(self.style.NOTICE("Starting product variant import..."))

        # Create uncategorized category if it doesn't exist
        uncategorized, _ = ProductCategory.objects.get_or_create(
            code="UNCATEGORIZED",
            defaults={"name": "Uncategorized"},
        )

        try:
            self.stdout.write("Fetching data from Artikel_Variante table...")

            # Create an instance of the SimpleAPIClient
            client = SimpleAPIClient(environment="live")

            # Fetch data using the client
            if limit:
                # Use direct API call with limit if specified
                limit_param = f"$top={limit}"
                response = client.session.get(
                    f"{client.base_url}/rest/Artikel_Variante?{limit_param}"
                )

                # Convert response to DataFrame
                if response.status_code != 200:
                    self.stdout.write(
                        self.style.ERROR(
                            f"Error: {response.status_code} - {response.text}"
                        )
                    )
                    return

                data = response.json()
                if "__ENTITIES" not in data:
                    self.stdout.write(
                        self.style.ERROR("No __ENTITIES found in response")
                    )
                    self.stdout.write(f"Response: {data}")
                    return

                df = pd.DataFrame(data["__ENTITIES"])
            else:
                # Use fetch_table with all_records=True to get all records with pagination
                self.stdout.write("Fetching all records with pagination...")
                df = client.fetch_table("Artikel_Variante", all_records=True)
                if df.empty:
                    self.stdout.write(self.style.ERROR("Failed to fetch data"))
                    return

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

                    # Skip if variant already exists and skip_existing is True
                    if (
                        skip_existing
                        and VariantProduct.objects.filter(legacy_id=legacy_id).exists()
                    ):
                        self.stdout.write(f"Skipping existing variant: {alte_nummer}")
                        stats["skipped"] += 1
                        continue

                    # Determine the primary SKU
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

                    # Extract pricing information
                    list_price = Decimal("0.00")
                    cost_price = Decimal("0.00")
                    retail_price = Decimal("0.00")
                    wholesale_price = Decimal("0.00")
                    retail_unit = 1
                    wholesale_unit = 1
                    gross_price = Decimal("0.00")

                    if "Preise" in row and row["Preise"] is not None:
                        prices = row["Preise"]
                        if isinstance(prices, dict) and "Coll" in prices:
                            for price_item in prices["Coll"]:
                                if isinstance(price_item, dict):
                                    price_type = price_item.get("Art")
                                    price_value = Decimal(
                                        str(price_item.get("Preis", 0))
                                    )
                                    ve_value = int(price_item.get("VE", 1))

                                    if price_type == "Laden":
                                        list_price = price_value
                                        retail_price = price_value
                                        retail_unit = ve_value
                                    elif price_type == "Handel":
                                        wholesale_price = price_value
                                        wholesale_unit = ve_value
                                    elif price_type == "Einkauf":
                                        cost_price = price_value
                                    elif price_type == "Empf.":
                                        gross_price = price_value

                    # Debug price information if requested
                    if debug_prices:
                        self._debug_prices(
                            row,
                            alte_nummer,
                            list_price,
                            retail_price,
                            wholesale_price,
                            cost_price,
                            gross_price,
                            retail_unit,
                            wholesale_unit,
                        )

                    # Find parent product - first try by Familie_ field
                    parent = None
                    familie_ = row.get("Familie_", None)

                    if familie_ and pd.notna(familie_):
                        parent_candidates = ParentProduct.objects.filter(
                            legacy_id=str(familie_),
                        )
                        if parent_candidates.exists():
                            parent = parent_candidates.first()

                    # If parent not found by Familie_, try by ref_old
                    if not parent and ref_old:
                        parent_candidates = ParentProduct.objects.filter(
                            legacy_id=str(ref_old),
                        )
                        if parent_candidates.exists():
                            parent = parent_candidates.first()

                    # As a last resort, try by base_sku
                    if not parent and base_sku:
                        parent_candidates = ParentProduct.objects.filter(
                            base_sku=base_sku,
                        )
                        if parent_candidates.exists():
                            parent = parent_candidates.first()

                    if not parent:
                        self.stdout.write(
                            self.style.WARNING(
                                f"Parent not found for variant: {alte_nummer} "
                                f"(Familie_: {familie_})"
                            ),
                        )
                        stats["parent_not_found"] += 1
                        continue  # Skip this variant since we need a parent

                    # Create variant data
                    variant_data = {
                        "sku": primary_sku,  # Use Nummer as primary SKU
                        "base_sku": base_sku,
                        "variant_code": variant_code,
                        "name": bezeichnung,
                        "legacy_id": legacy_id,
                        "legacy_sku": alte_nummer,  # Store alteNummer as legacy
                        "legacy_familie": familie_,  # Store the Familie_ reference
                        "parent": parent,
                        "list_price": list_price,
                        "cost_price": cost_price,
                        "wholesale_price": wholesale_price,
                        "retail_price": retail_price,
                        "retail_unit": retail_unit,
                        "wholesale_unit": wholesale_unit,
                        "gross_price": gross_price,
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
                        "This was a dry run. No changes were made to the database."
                    ),
                )

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"Error importing variants: {e!s}"),
            )
            raise

    def _debug_prices(
        self,
        row,
        alte_nummer,
        list_price=None,
        retail_price=None,
        wholesale_price=None,
        cost_price=None,
        gross_price=None,
        retail_unit=None,
        wholesale_unit=None,
    ):
        """Debug helper to print price information for a variant."""
        self.stdout.write(self.style.NOTICE(f"\n=== Price Debug for {alte_nummer} ==="))

        # Show raw price data
        if "Preise" in row and row["Preise"] is not None:
            self.stdout.write("Raw Preise data:")
            prices = row["Preise"]
            if isinstance(prices, dict) and "Coll" in prices:
                for i, price_item in enumerate(prices["Coll"]):
                    self.stdout.write(f"  Price {i + 1}: {price_item}")
            else:
                self.stdout.write(f"  {prices}")
        else:
            self.stdout.write("  No Preise data found")

        # Show mapped prices if provided
        if list_price is not None:
            self.stdout.write("\nMapped prices:")
            self.stdout.write(f"  list_price: {list_price}")
            self.stdout.write(f"  retail_price: {retail_price}")
            self.stdout.write(f"  wholesale_price: {wholesale_price}")
            self.stdout.write(f"  cost_price: {cost_price}")
            self.stdout.write(f"  gross_price: {gross_price}")
            self.stdout.write(f"  retail_unit: {retail_unit}")
            self.stdout.write(f"  wholesale_unit: {wholesale_unit}")

        self.stdout.write("=" * 50)
