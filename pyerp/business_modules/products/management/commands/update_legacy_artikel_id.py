"""
Management command to populate the legacy_artikel_id field for existing VariantProduct records.

This command queries the legacy system to get the ID_Artikel_Stamm values for each product
and updates the corresponding VariantProduct records in our system.
"""

import logging
from datetime import datetime

from django.core.management.base import BaseCommand
from django.db import transaction

from pyerp.business_modules.products.models import VariantProduct
from pyerp.external_api.legacy_erp.client import LegacyERPClient
import pandas as pd

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    """Command to update legacy_artikel_id field for VariantProduct records."""

    help = "Populate legacy_artikel_id field for existing VariantProduct records"

    def add_arguments(self, parser):
        """Add command line arguments."""
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Perform a dry run without making any changes",
        )

    def handle(self, *args, **options):
        """Execute the command."""
        dry_run = options.get("dry_run", False)
        if dry_run:
            self.stdout.write(
                self.style.WARNING("Performing dry run - no changes will be made")
            )

        start_time = datetime.now()
        self.stdout.write(f"Starting update at {start_time}")

        # Fetch legacy products
        legacy_products_df = self.fetch_legacy_products()

        # Update legacy_artikel_id for existing products
        self.update_legacy_artikel_ids(legacy_products_df, dry_run)

        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        self.stdout.write(
            self.style.SUCCESS(f"Update completed in {duration:.2f} seconds")
        )

    def fetch_legacy_products(self):
        """
        Fetch products from the legacy system.

        Returns:
            DataFrame containing product data with ID and ArtNr columns
        """
        client = LegacyERPClient(environment="live")
        self.stdout.write("Fetching products from legacy system...")

        # Fetch products from Artikel_Stamm table
        artikel_stamm_df = client.fetch_table(
            table_name="Artikel_Stamm", all_records=True
        )

        if artikel_stamm_df is None or artikel_stamm_df.empty:
            self.stdout.write(self.style.ERROR("No data found in Artikel_Stamm table"))
            return None

        # Print all columns for debugging
        self.stdout.write(
            f"Artikel_Stamm columns: {', '.join(artikel_stamm_df.columns)}"
        )

        # Check if we have the required columns
        required_stamm_cols = ["ID", "ArtNr"]

        missing_stamm_cols = [
            col for col in required_stamm_cols if col not in artikel_stamm_df.columns
        ]
        if missing_stamm_cols:
            self.stdout.write(
                self.style.ERROR(
                    f"Missing required columns in Artikel_Stamm: {', '.join(missing_stamm_cols)}"
                )
            )
            return None

        # Create a copy of the Artikel_Stamm dataframe with only the columns we need
        result_df = artikel_stamm_df[["ID", "ArtNr"]].copy()

        # Filter out rows where ArtNr is null or empty
        result_df = result_df[result_df["ArtNr"].notna()]

        self.stdout.write(f"Found {len(result_df)} products with valid ArtNr")
        return result_df

    def update_legacy_artikel_ids(self, legacy_products_df, dry_run=False):
        """
        Update the legacy_artikel_id field for existing VariantProduct records.

        Args:
            legacy_products_df: DataFrame containing legacy product data
            dry_run: If True, don't make any changes
        """
        if legacy_products_df is None or legacy_products_df.empty:
            self.stdout.write(self.style.ERROR("No legacy product data available"))
            return

        # Create a mapping from ArtNr to ID
        artnr_to_id_map = {}

        for _, row in legacy_products_df.iterrows():
            if pd.notna(row["ArtNr"]) and pd.notna(row["ID"]):
                artnr_to_id_map[row["ArtNr"]] = row["ID"]

        self.stdout.write(f"Created mapping for {len(artnr_to_id_map)} ArtNr values")

        # Get all products that need updating (either null or incorrect legacy_artikel_id)
        products = VariantProduct.objects.all()
        self.stdout.write(
            f"Found {products.count()} products to check for legacy_artikel_id"
        )

        updated_count = 0
        not_found_count = 0

        if not dry_run:
            with transaction.atomic():
                for product in products:
                    artikel_id = None

                    # Try to match by legacy_sku (which should match ArtNr)
                    if product.legacy_sku and product.legacy_sku in artnr_to_id_map:
                        artikel_id = artnr_to_id_map[product.legacy_sku]
                    # Then try to match by sku
                    elif product.sku in artnr_to_id_map:
                        artikel_id = artnr_to_id_map[product.sku]

                    if artikel_id:
                        if product.legacy_artikel_id != artikel_id:
                            product.legacy_artikel_id = artikel_id
                            product.save(update_fields=["legacy_artikel_id"])
                            updated_count += 1
                            if updated_count % 100 == 0:
                                self.stdout.write(
                                    f"Updated {updated_count} products so far"
                                )
                    else:
                        not_found_count += 1
                        self.stdout.write(
                            self.style.WARNING(
                                f"Could not find legacy ID for product {product.sku} "
                                f"(legacy_sku: {product.legacy_sku})"
                            )
                        )
        else:
            # Dry run - just count how many would be updated
            for product in products:
                artikel_id = None

                # Try to match by legacy_sku (which should match ArtNr)
                if product.legacy_sku and product.legacy_sku in artnr_to_id_map:
                    artikel_id = artnr_to_id_map[product.legacy_sku]
                # Then try to match by sku
                elif product.sku in artnr_to_id_map:
                    artikel_id = artnr_to_id_map[product.sku]

                if artikel_id:
                    if product.legacy_artikel_id != artikel_id:
                        updated_count += 1
                        if updated_count % 100 == 0:
                            self.stdout.write(
                                f"Would update {updated_count} products so far"
                            )
                else:
                    not_found_count += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"{'Would update' if dry_run else 'Updated'} "
                f"{updated_count} products with legacy_artikel_id"
            )
        )
        self.stdout.write(
            self.style.WARNING(
                f"Could not find legacy ID for {not_found_count} products"
            )
        )
