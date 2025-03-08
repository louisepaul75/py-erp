"""Management command to import products from the legacy 4D system."""

import contextlib
import logging
import sys
from decimal import Decimal

import pandas as pd
from django.core.management.base import BaseCommand

from pyerp.business_modules.products.models import Product, ProductCategory
from pyerp.business_modules.products.validators import ProductImportValidator
from wsz_api.getTable import fetch_data_from_api

# Add the WSZ_api path to the Python path
WSZ_API_PATH = r"C:\Users\Joan-Admin\PycharmProjects\WSZ_api"
if WSZ_API_PATH not in sys.path:
    sys.path.append(WSZ_API_PATH)

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Import products from the legacy 4D system (Artikel_Variante table)"

    def add_arguments(self, parser):
        parser.add_argument(
            "--limit",
            type=int,
            default=0,
            help="Limit the number of products to import",
        )
        parser.add_argument(
            "--update",
            action="store_true",
            help="Update existing products",
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
            "--create-parents",
            action="store_true",
            help="Create parent products for variants with the same base SKU",
        )

    def handle(self, *args, **options):
        """Handle command execution."""
        self.stdout.write("Starting product import from 4D (Artikel_Variante)...")

        # Command options
        self.limit = options["limit"]
        self.update = options["update"]
        self.dry_run = options["dry_run"]
        self.debug = options["debug"]
        self.create_parents = options["create_parents"]

        # Get or create default category
        self.default_category, _ = ProductCategory.objects.get_or_create(
            code="UNCATEGORIZED",
            defaults={
                "name": "Uncategorized",
                "description": "Default category for products without a specific category",
            },
        )

        # Initialize the validator with the default category
        self.validator = ProductImportValidator(
            strict=False,
            transform_data=True,
            default_category=self.default_category,
        )

        # Fetch data from Artikel_Variante
        self.stdout.write("Fetching data from Artikel_Variante table...")
        try:
            df = fetch_data_from_api("Artikel_Variante")
            self.stdout.write(f"Retrieved {len(df)} records")

            if self.debug:
                self.stdout.write("Column names:")
                for column in df.columns:
                    self.stdout.write(f"- {column}")

                # Print first few rows for debugging
                self.stdout.write("\nFirst 5 rows:")
                for i in range(min(5, len(df))):
                    self.stdout.write(f"\nRow {i}:")
                    for key, value in df.iloc[i].items():
                        self.stdout.write(f"  {key}: {value}")

            # Process data
            skipped = 0
            created = 0
            updated = 0

            # Limit the number of records to process if specified
            if self.limit > 0:
                df = df.head(self.limit)

            # If create_parents is True, analyze SKUs to find base SKUs needing parent products
            parent_skus = set()
            if self.create_parents:
                self.stdout.write("Analyzing SKUs to identify parent products...")
                for index, row in df.iterrows():
                    alte_nummer = self.get_value(row, "alteNummer", "")
                    if "-" in alte_nummer:
                        base_sku = alte_nummer.split("-", 1)[0]
                        parent_skus.add(base_sku)

                self.stdout.write(
                    f"Identified {len(parent_skus)} potential parent products",
                )

            # Process each record
            for index, row in df.iterrows():
                product_data = self.extract_product_data(row, index)

                if not product_data:
                    skipped += 1
                    continue

                # Skip processing in dry run mode
                if self.dry_run:
                    self.stdout.write(
                        f"[DRY RUN] Would create/update product: {product_data['sku']} - {product_data['name']}",
                    )
                    continue

                # Check if product exists
                try:
                    product = Product.objects.get(sku=product_data["sku"])

                    # Update product if --update flag is set
                    if self.update:
                        for key, value in product_data.items():
                            setattr(product, key, value)
                        product.save()
                        updated += 1
                        self.stdout.write(
                            f"Updated product: {product.sku} - {product.name}",
                        )
                    else:
                        skipped += 1
                        self.stdout.write(f"Skipped existing product: {product.sku}")

                except Product.DoesNotExist:
                    Product.objects.create(**product_data)
                    created += 1
                    self.stdout.write(
                        f"Created product: {product_data['sku']} - {product_data['name']}",
                    )

                # Print progress every 100 records
                if (index + 1) % 100 == 0:
                    self.stdout.write(f"Processed {index + 1} records...")

            # Create parent products if requested
            if self.create_parents and not self.dry_run:
                self.create_parent_products(parent_skus)

            if self.dry_run:
                self.stdout.write("DRY RUN - No changes were made to the database")

            self.stdout.write("Import completed:")
            self.stdout.write(f"  Products created: {created}")
            self.stdout.write(f"  Products updated: {updated}")
            self.stdout.write(f"  Products skipped: {skipped}")

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error: {e!s}"))
            import traceback

            self.stdout.write(self.style.ERROR(traceback.format_exc()))
            raise

    def extract_product_data(self, row, index):
        """Extract product data from an Artikel_Variante row."""
        try:
            legacy_id = self.get_value(row, "UID", "")

            # Debug log
            if self.debug:
                self.stdout.write(f"\nProcessing row {index}:")
                self.stdout.write(f"  UID: {legacy_id}")
                self.stdout.write(
                    f"  Bezeichnung: {self.get_value(row, 'Bezeichnung', '')}",
                )

            # Prepare row data with raw values for validation
            row_data = {
                "sku": self.get_value(row, "alteNummer", ""),
                "name": self.get_value(row, "Bezeichnung", ""),
                "legacy_id": str(legacy_id),
                "Preise": self.get_value(row, "Preise", None),
                "is_active": self.get_value(row, "Aktiv", True),
                "ArtGruppe": self.get_value(row, "ArtGruppe", None),
            }

            # Validate and transform the data
            is_valid, validated_data, validation_result = self.validator.validate_row(
                row_data,
                index,
            )

            # Log warnings
            for field, warnings in validation_result.warnings.items():
                for warning in warnings:
                    self.stdout.write(
                        self.style.WARNING(
                            f"Warning for row {index}, field {field}: {warning}",
                        ),
                    )

            # If validation failed, log errors and return None
            if not is_valid:
                self.stdout.write(
                    self.style.ERROR(f"Validation failed for row {index}:"),
                )
                for field, errors in validation_result.errors.items():
                    for error in errors:
                        self.stdout.write(self.style.ERROR(f"  {field}: {error}"))
                return None

            # Use the transformed data for product creation/update
            product_data = {
                "sku": validated_data["sku"],
                "base_sku": validated_data.get("base_sku", ""),
                "variant_code": validated_data.get("variant_code", ""),
                "legacy_id": validated_data["legacy_id"],
                "name": validated_data["name"],
                "list_price": validated_data.get("list_price", Decimal("0.00")),
                "wholesale_price": validated_data.get(
                    "wholesale_price",
                    Decimal("0.00"),
                ),
                "cost_price": validated_data.get("cost_price", Decimal("0.00")),
                "is_active": validated_data.get("is_active", True),
                "is_parent": validated_data.get("is_parent", False),
                "category": validated_data.get("category", self.default_category),
            }

            # Set created_at if creation date exists
            created_date = self.get_value(row, "created_date", None)
            if created_date and not pd.isna(created_date):
                with contextlib.suppress(ValueError, TypeError):
                    product_data["created_at"] = created_date

            return product_data

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error processing row {index}: {e!s}"))
            return None

    def create_parent_products(self, parent_skus):
        """Create parent products for SKUs that need them."""
        created = 0

        for base_sku in parent_skus:
            if Product.objects.filter(base_sku=base_sku, is_parent=True).exists():
                continue

            # Get all variants with this base_sku
            variants = Product.objects.filter(base_sku=base_sku, is_parent=False)
            if not variants.exists():
                continue

            # Use the first variant as a template for the parent
            template = variants.first()

            # Create parent product
            parent = Product(
                sku=base_sku,
                base_sku=base_sku,
                variant_code="",
                name=template.name,
                legacy_id=f"parent-{base_sku}",
                list_price=template.list_price,
                wholesale_price=template.wholesale_price,
                cost_price=template.cost_price,
                is_active=True,
                is_parent=True,
                category=template.category,
            )
            parent.save()
            created += 1

            # Update all variants to point to this parent
            for variant in variants:
                variant.parent = parent
                variant.save()

            self.stdout.write(
                f"Created parent product: {parent.sku} with {variants.count()} variants",
            )

        self.stdout.write(f"Created {created} parent products")

    def get_value(self, row, key, default):
        """Get a value from a row, returning default if not found or None."""
        if not isinstance(row, pd.Series):
            return row.get(key, default)
        try:
            value = row[key]
            return default if pd.isna(value) else value
        except (KeyError, TypeError):
            return default
