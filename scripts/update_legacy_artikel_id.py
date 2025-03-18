#!/usr/bin/env python
"""
Script to populate the legacy_artikel_id field for existing VariantProduct records.

This script queries the legacy system to get the ID_Artikel_Stamm values for each product
and updates the corresponding VariantProduct records in our system.
"""

import os
import sys
import logging
from datetime import datetime

# Set up Django environment
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.local")

# Initialize Django
import django

django.setup()

# Now import Django models
from django.db import transaction
from pyerp.business_modules.products.models import VariantProduct
from pyerp.external_api.legacy_erp.client import LegacyERPClient
import pandas as pd

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def fetch_legacy_products():
    """
    Fetch products from the legacy system.

    Returns:
        DataFrame containing product data with ID and Nummer columns
    """
    client = LegacyERPClient(environment="live")
    logger.info("Fetching products from legacy system...")

    # Fetch products from Artikel_Variante table
    df = client.fetch_table(table_name="Artikel_Variante", all_records=True)

    # Keep only the columns we need
    if "ID" in df.columns and "Nummer" in df.columns:
        return df[["ID", "Nummer", "alteNummer"]]
    else:
        missing_cols = []
        if "ID" not in df.columns:
            missing_cols.append("ID")
        if "Nummer" not in df.columns:
            missing_cols.append("Nummer")
        if "alteNummer" not in df.columns:
            missing_cols.append("alteNummer")

        logger.error(f"Missing required columns: {', '.join(missing_cols)}")
        logger.info(f"Available columns: {', '.join(df.columns)}")
        return None


def update_legacy_artikel_ids(legacy_products_df):
    """
    Update the legacy_artikel_id field for existing VariantProduct records.

    Args:
        legacy_products_df: DataFrame containing legacy product data
    """
    if legacy_products_df is None or legacy_products_df.empty:
        logger.error("No legacy product data available")
        return

    # Create a mapping from SKU to ID
    sku_to_id_map = {}
    legacy_sku_to_id_map = {}

    for _, row in legacy_products_df.iterrows():
        if pd.notna(row["Nummer"]):
            sku_to_id_map[row["Nummer"]] = row["ID"]
        if pd.notna(row["alteNummer"]):
            legacy_sku_to_id_map[row["alteNummer"]] = row["ID"]

    logger.info(
        f"Created mapping for {len(sku_to_id_map)} SKUs and {len(legacy_sku_to_id_map)} legacy SKUs"
    )

    # Get all products that need updating
    products = VariantProduct.objects.filter(legacy_artikel_id__isnull=True)
    logger.info(f"Found {products.count()} products without legacy_artikel_id")

    updated_count = 0
    not_found_count = 0

    with transaction.atomic():
        for product in products:
            artikel_id = None

            # Try to match by SKU first
            if product.sku in sku_to_id_map:
                artikel_id = sku_to_id_map[product.sku]
            # Then try to match by legacy_sku
            elif product.legacy_sku and product.legacy_sku in legacy_sku_to_id_map:
                artikel_id = legacy_sku_to_id_map[product.legacy_sku]

            if artikel_id:
                product.legacy_artikel_id = artikel_id
                product.save(update_fields=["legacy_artikel_id"])
                updated_count += 1
                if updated_count % 100 == 0:
                    logger.info(f"Updated {updated_count} products so far")
            else:
                not_found_count += 1
                logger.warning(
                    f"Could not find legacy ID for product {product.sku} (legacy_sku: {product.legacy_sku})"
                )

    logger.info(f"Updated {updated_count} products with legacy_artikel_id")
    logger.info(f"Could not find legacy ID for {not_found_count} products")


def main():
    """Main function to run the script."""
    start_time = datetime.now()
    logger.info(f"Starting update at {start_time}")

    # Fetch legacy products
    legacy_products_df = fetch_legacy_products()

    # Update legacy_artikel_id for existing products
    update_legacy_artikel_ids(legacy_products_df)

    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()
    logger.info(f"Update completed in {duration:.2f} seconds")


if __name__ == "__main__":
    main()
