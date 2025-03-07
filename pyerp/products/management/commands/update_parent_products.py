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

from pyerp.direct_api.scripts.getTable import SimpleAPIClient
from pyerp.products.models import ParentProduct, ProductCategory, VariantProduct

# Configure logging
logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Update parent products from the legacy ERP system"

    def add_arguments(self, parser):
        parser.add_argument(
            "--env",
            default="live",
            help="API environment to use",
        )
        parser.add_argument(
            "--limit",
            type=int,
            help="Maximum number of records to process",
        )
        parser.add_argument(
            "--no-update",
            action="store_false",
            dest="update",
            help="Don't update existing parent products",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Don't save changes to database",
        )
        parser.add_argument(
            "--debug",
            action="store_true",
            help="Print additional debug information",
        )

    def handle(self, *args, **options):
        """Execute the command."""
        environment = options["env"]
        limit = options["limit"]
        update_existing = options["update"]
        dry_run = options["dry_run"]
        debug = options["debug"]

        self.stdout.write("Starting parent product update process")
        self.stdout.write(f"Environment: {environment}")
        self.stdout.write(f"Update existing: {update_existing}")
        self.stdout.write(f"Dry run: {dry_run}")

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
            client = SimpleAPIClient(environment=environment)
            self.stdout.write("API client initialized successfully")
        except Exception as e:
            self.stderr.write(f"Failed to initialize API client: {e}")
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

            # Print the field names from the first record to help identify the correct field names
            if len(df) > 0:
                self.stdout.write("\nField names in the first record:")
                for field_name in sorted(df.iloc[0].keys()):
                    self.stdout.write(f"  - {field_name}")

                # Print the first record for debugging
                if debug:
                    self.stdout.write("\nFirst record data:")
                    for field_name, value in df.iloc[0].items():
                        self.stdout.write(f"  {field_name}: {value}")

            # Get default category for products without a category
            try:
                default_category = ProductCategory.objects.get(code="DEFAULT")
            except ProductCategory.DoesNotExist:
                default_category = ProductCategory.objects.create(
                    code="DEFAULT",
                    name="Default Category",
                    description="Default category for imported products",
                )
                self.stdout.write("Created default category")

            # Process each parent product
            for _, row in df.iterrows():
                try:
                    # Extract data from the row
                    familie_id = str(row["__KEY"]) if "__KEY" in row else None
                    nummer = str(row["Nummer"]) if "Nummer" in row else None

                    if not familie_id or not nummer:
                        self.stdout.write(f"Skipping row - Missing ID or SKU: {row}")
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
                    weight = (
                        float(row["Gewicht"]) if pd.notna(row.get("Gewicht")) else 0
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

                    # Map Haengend to is_hanging (we now know the exact field name)
                    is_hanging = bool(row.get("Haengend", False))
                    if debug:
                        self.stdout.write(
                            f"Haengend field value: {row.get('Haengend', 'Not found')}"
                        )

                    # Map Einseitig to is_one_sided (we now know the exact field name)
                    is_one_sided = bool(row.get("Einseitig", False))
                    if debug:
                        self.stdout.write(
                            f"Einseitig field value: {row.get('Einseitig', 'Not found')}"
                        )

                    # Add debug logging for these fields
                    if debug:
                        self.stdout.write(
                            f"Product {nummer} - is_hanging: {is_hanging}, "
                            f"is_one_sided: {is_one_sided}"
                        )
                        self.stdout.write(f"Available fields: {list(row.keys())}")

                    # Try to find category from ArtGr
                    category = default_category
                    if art_gr:
                        try:
                            category = ProductCategory.objects.get(code=art_gr)
                        except ProductCategory.DoesNotExist:
                            category = ProductCategory.objects.create(
                                code=art_gr,
                                name=art_gr,  # Use code as name if no mapping exists
                                description=(
                                    f"Category imported from legacy system with code {art_gr}"
                                ),
                            )
                            self.stdout.write(f"Created new category: {art_gr}")

                    # Check if parent product exists
                    existing_parent = ParentProduct.objects.filter(
                        Q(sku=nummer) | Q(legacy_id=familie_id)
                    ).first()

                    # Create parent product data dictionary
                    parent_data = {
                        "sku": nummer,
                        "base_sku": nummer,  # For a parent, sku and base_sku are the same
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
                                self.stdout.write(
                                    f"Skipping existing parent {nummer} "
                                    f"(update not enabled)"
                                )
                            stats["skipped"] += 1
                            continue

                        # Update existing parent product
                        if not dry_run:
                            for key, value in parent_data.items():
                                setattr(existing_parent, key, value)
                            existing_parent.save()

                        self.stdout.write(f"Updated parent product: {nummer}")
                        stats["updated"] += 1

                        # Associate variants with this parent
                        if not dry_run:
                            self.associate_variants(existing_parent, familie_id, debug)
                    else:
                        # Create new parent product
                        if not dry_run:
                            with transaction.atomic():
                                parent_product = ParentProduct.objects.create(
                                    **parent_data
                                )
                                self.associate_variants(
                                    parent_product, familie_id, debug
                                )

                        self.stdout.write(f"Created parent product: {nummer}")
                        stats["created"] += 1

                except Exception as e:
                    self.stderr.write(f"Error processing parent product: {e}")
                    stats["errors"] += 1

        except Exception as e:
            self.stderr.write(f"Failed to fetch parent products: {e}")
            return

        # Print summary
        self.stdout.write("Parent product update process completed")
        self.stdout.write(f"Total: {stats['total']}")
        self.stdout.write(f"Created: {stats['created']}")
        self.stdout.write(f"Updated: {stats['updated']}")
        self.stdout.write(f"Skipped: {stats['skipped']}")
        self.stdout.write(f"Errors: {stats['errors']}")

    def associate_variants(self, parent, familie_id, debug=False):
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
            self.stdout.write(f"Associated {count} variants with parent {parent.sku}")
