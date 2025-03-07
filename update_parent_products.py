#!/usr/bin/env python
"""
Update Parent Products Script

This script updates all parent products from the legacy ERP system using SimpleAPIClient.
It fetches data from the Artikel_Familie table and updates the corresponding ParentProduct records.
"""

import os
import sys
import logging
import argparse
import django
import pandas as pd
from pathlib import Path

# Set up Django environment
# Add the parent directory to the path so we can import the pyerp module
sys.path.insert(0, str(Path(__file__).resolve().parent))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "pyerp.settings")

# Initialize Django
django.setup()

# Ensure the products app is in INSTALLED_APPS
from django.conf import settings
if 'pyerp.products' not in settings.INSTALLED_APPS:
    settings.INSTALLED_APPS += ('pyerp.products',)

# Import Django models after setting up the environment
from django.db import transaction  # noqa: E402
from django.db.models import Q  # noqa: E402
from pyerp.products.models import (  # noqa: E402
    ParentProduct, VariantProduct, ProductCategory
)
from pyerp.direct_api.scripts.getTable import SimpleAPIClient  # noqa: E402

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger(__name__)

def update_parent_products(
    environment="live",
    limit=None,
    update_existing=True,
    dry_run=False,
    debug=False,
):
    """
    Update parent products from the legacy ERP system.
    
    Args:
        environment: API environment to use (default: live)
        limit: Maximum number of records to process (default: None, process all)
        update_existing: Whether to update existing parent products (default: True)
        dry_run: If True, don't save changes to the database (default: False)
        debug: If True, print additional debug information (default: False)
    
    Returns:
        dict: Statistics about the update process
    """
    stats = {
        "total": 0,
        "created": 0,
        "updated": 0,
        "skipped": 0,
        "errors": 0,
    }
    
    logger.info("Starting parent product update process")
    logger.info(f"Environment: {environment}")
    logger.info(f"Update existing: {update_existing}")
    logger.info(f"Dry run: {dry_run}")
    
    # Initialize the API client
    try:
        client = SimpleAPIClient(environment=environment)
        logger.info("API client initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize API client: {e}")
        return stats
    
    # Fetch parent products from the legacy system
    try:
        logger.info("Fetching parent products from Artikel_Familie table")
        df = client.fetch_table(
            table_name="Artikel_Familie",
            top=limit,
            all_records=limit is None,
        )
        
        stats["total"] = len(df)
        logger.info(f"Fetched {stats['total']} parent products")
        
        # Get default category for products without a category
        try:
            default_category = ProductCategory.objects.get(code="DEFAULT")
            logger.info(f"Found default category with ID: {default_category.id}")
        except ProductCategory.DoesNotExist:
            try:
                # Try to get any existing category as a fallback
                default_category = ProductCategory.objects.first()
                if default_category:
                    logger.info(f"Using existing category as default: {default_category.code} (ID: {default_category.id})")
                else:
                    # If no categories exist at all, we need to handle this case
                    logger.error("No categories found in the database. Cannot proceed.")
                    return stats
            except Exception as e:
                logger.error(f"Error getting default category: {e}")
                return stats
        
        # Process each parent product
        for _, row in df.iterrows():
            try:
                # Extract data from the row
                familie_id = str(row["__KEY"]) if "__KEY" in row else None
                nummer = str(row["Nummer"]) if "Nummer" in row else None
                
                if not familie_id or not nummer:
                    logger.warning(f"Skipping row - Missing ID or SKU: {row}")
                    stats["skipped"] += 1
                    continue
                
                # Extract additional fields
                name = row.get("Bezeichnung", "")
                name_en = row.get("Bezeichnung_ENG", "")
                description = row.get("Beschreibung", "")
                description_en = row.get("Beschreibung_ENG", "")
                short_description = row.get("Bez_kurz", "")
                art_gr = row.get("ArtGr", "")
                
                # Physical attributes
                weight = float(row["Gewicht"]) if pd.notna(row.get("Gewicht")) else 0
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
                
                # Map Haengend/hangend to is_hanging
                is_hanging = False
                for field_name in ["Haengend", "hangend", "haengen", "haengend"]:
                    if field_name in row and pd.notna(row.get(field_name)):
                        is_hanging = bool(row.get(field_name))
                        break
                
                # Map Einseitig/einseitig to is_one_sided
                is_one_sided = False
                for field_name in ["Einseitig", "einseitig", "eineSeite", "eineSeit"]:
                    if field_name in row and pd.notna(row.get(field_name)):
                        is_one_sided = bool(row.get(field_name))
                        break
                
                # Add debug logging for these fields
                if debug:
                    logger.info(f"Product {nummer} - is_hanging: {is_hanging}, is_one_sided: {is_one_sided}")
                    logger.info(f"Available fields: {list(row.keys())}")
                
                # Try to find category from ArtGr
                category = default_category
                if art_gr:
                    try:
                        category = ProductCategory.objects.get(code=art_gr)
                        logger.info(f"Found category {art_gr} with ID: {category.id}")
                    except ProductCategory.DoesNotExist:
                        # Don't try to create a new category, use the default instead
                        logger.info(f"Category {art_gr} not found, using default category")
                
                # Check if parent product exists
                existing_parent = ParentProduct.objects.filter(
                    Q(sku=nummer) | Q(legacy_id=familie_id)
                ).first()
                
                # Prepare parent product data
                parent_data = {
                    "sku": nummer,
                    "base_sku": nummer,  # For a parent, sku and base_sku are the same
                    "legacy_id": familie_id,
                    "name": name,
                    "name_en": name_en,
                    "description": description,
                    "description_en": description_en,
                    "short_description": short_description,
                    "weight": weight,
                    "width": width,
                    "height": height,
                    "depth": depth,
                    "is_active": is_active,
                    "is_hanging": is_hanging,
                    "is_one_sided": is_one_sided,
                    "category": category,  # Make sure category is properly set
                    "is_placeholder": 0,  # Use integer 0 instead of boolean False
                }
                
                if debug:
                    logger.info(f"Parent data: {parent_data}")
                    logger.info(f"Category: {category.code} (ID: {category.id})")
                
                # Add dimensions if available
                if width is not None:
                    parent_data["width"] = width
                if height is not None:
                    parent_data["height"] = height
                if depth is not None:
                    parent_data["depth"] = depth
                
                # Create or update parent product
                if existing_parent:
                    if not update_existing:
                        if debug:
                            logger.info(
                                f"Skipping existing parent {nummer} (update not enabled)"
                            )
                        stats["skipped"] += 1
                        continue
                    
                    # Update existing parent product
                    if not dry_run:
                        for key, value in parent_data.items():
                            setattr(existing_parent, key, value)
                        existing_parent.save()
                    
                    logger.info(f"Updated parent product: {nummer}")
                    stats["updated"] += 1
                    
                    # Associate variants with this parent
                    if not dry_run:
                        associate_variants(existing_parent, familie_id, debug)
                else:
                    # Create new parent product
                    if not dry_run:
                        with transaction.atomic():
                            parent_product = ParentProduct.objects.create(**parent_data)
                            associate_variants(parent_product, familie_id, debug)
                    
                    logger.info(f"Created parent product: {nummer}")
                    stats["created"] += 1
            
            except Exception as e:
                logger.error(f"Error processing parent product: {e}")
                stats["errors"] += 1
    
    except Exception as e:
        logger.error(f"Failed to fetch parent products: {e}")
        return stats
    
    logger.info("Parent product update process completed")
    logger.info(f"Total: {stats['total']}")
    logger.info(f"Created: {stats['created']}")
    logger.info(f"Updated: {stats['updated']}")
    logger.info(f"Skipped: {stats['skipped']}")
    logger.info(f"Errors: {stats['errors']}")
    
    return stats

def associate_variants(parent, familie_id, debug=False):
    """
    Associate variant products with their parent.
    
    Args:
        parent: ParentProduct instance
        familie_id: Legacy ID of the parent product
        debug: If True, print additional debug information
    """
    # Find variants that reference this parent in the legacy system
    variants = VariantProduct.objects.filter(legacy_parent_id=familie_id)
    
    count = 0
    for variant in variants:
        if variant.parent != parent:
            variant.parent = parent
            variant.save()
            count += 1
    
    if count > 0 and debug:
        logger.info(f"Associated {count} variants with parent {parent.sku}")

def main():
    """Main entry point for the script."""
    # Check if we're being run from Django shell
    if len(sys.argv) > 1 and 'shell' in sys.argv:
        print("Running in Django shell mode")
        # Use default arguments when run from shell
        return update_parent_products(
            environment="live",
            limit=None,
            update_existing=True,
            dry_run=False,
            debug=True,
        )
    
    parser = argparse.ArgumentParser(
        description="Update parent products from legacy ERP system"
    )
    parser.add_argument("--env", default="live", help="API environment to use")
    parser.add_argument(
        "--limit", 
        type=int, 
        help="Maximum number of records to process"
    )
    parser.add_argument(
        "--no-update", 
        action="store_false", 
        dest="update", 
        help="Don't update existing parent products"
    )
    parser.add_argument(
        "--dry-run", 
        action="store_true", 
        help="Don't save changes to database"
    )
    parser.add_argument(
        "--debug", 
        action="store_true", 
        help="Print additional debug information"
    )
    
    args = parser.parse_args()
    
    update_parent_products(
        environment=args.env,
        limit=args.limit,
        update_existing=args.update,
        dry_run=args.dry_run,
        debug=args.debug,
    )

if __name__ == "__main__":
    main()
else:
    # This allows the script to be executed when imported in Django shell
    print("Running update_parent_products script...")
    # Use default arguments when imported
    update_parent_products(
        environment="live",
        limit=None,
        update_existing=True,
        dry_run=False,
        debug=True,
    ) 