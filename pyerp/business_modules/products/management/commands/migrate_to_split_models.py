"""
Management command to migrate data from the old Product model to the new ParentProduct and VariantProduct models.  # noqa: E501
"""

import logging

from django.core.management.base import BaseCommand
from django.db import transaction

from pyerp.business_modules.products.models import ParentProduct, Product, VariantProduct

# Configure logging
logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Migrate data from the old Product model to the new ParentProduct and VariantProduct models"

    def add_arguments(self, parser):
        parser.add_argument(
            "--limit",
            type=int,
            default=None,
            help="Limit the number of products to migrate",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Perform a dry run without saving to the database",
        )
        parser.add_argument(
            "--skip-existing",
            action="store_true",
            help="Skip products that already exist in the new models",
        )

    def handle(self, *args, **options):
        limit = options["limit"]
        dry_run = options["dry_run"]
        skip_existing = options["skip_existing"]

        self.stdout.write(self.style.NOTICE("Starting migration to split models..."))

        # Migrate parent products first
        self.migrate_parent_products(limit, skip_existing, dry_run)

        # Then migrate variant products
        self.migrate_variant_products(limit, skip_existing, dry_run)

        self.stdout.write(self.style.SUCCESS("Migration completed"))

    def migrate_parent_products(
        self, limit=None, *, skip_existing=False, dry_run=False
    ):
        """
        Migrate parent products from the old Product model to the new ParentProduct model.  # noqa: E501
        """
        self.stdout.write("Migrating parent products...")

        # Get parent products from the old model
        parent_products = Product.objects.filter(is_parent=True)
        if limit:
            parent_products = parent_products[:limit]

        self.stdout.write(f"Found {parent_products.count()} parent products to migrate")

        # Track statistics
        stats = {
            "total": parent_products.count(),
            "created": 0,
            "skipped": 0,
            "errors": 0,
        }

        # Create a mapping of old parent IDs to new parent IDs
        parent_mapping = {}

        # Process each parent product
        for old_parent in parent_products:
            try:
                if (
                    skip_existing
                    and ParentProduct.objects.filter(
                        legacy_id=old_parent.legacy_id,
                    ).exists()
                ):
                    self.stdout.write(
                        f"Skipping existing parent product: {old_parent.sku}",
                    )
                    stats["skipped"] += 1
                    continue

                # Create parent data
                parent_data = {
                    "sku": old_parent.sku,
                    "base_sku": old_parent.base_sku,
                    "legacy_id": old_parent.legacy_id,
                    "name": old_parent.name,
                    "name_en": old_parent.name_en,
                    "short_description": old_parent.short_description,
                    "short_description_en": old_parent.short_description_en,
                    "description": old_parent.description,
                    "description_en": old_parent.description_en,
                    "keywords": old_parent.keywords,
                    "dimensions": old_parent.dimensions,
                    "weight": old_parent.weight,
                    "list_price": old_parent.list_price,
                    "wholesale_price": old_parent.wholesale_price,
                    "gross_price": old_parent.gross_price,
                    "cost_price": old_parent.cost_price,
                    "stock_quantity": old_parent.stock_quantity,
                    "min_stock_quantity": old_parent.min_stock_quantity,
                    "backorder_quantity": old_parent.backorder_quantity,
                    "open_purchase_quantity": old_parent.open_purchase_quantity,
                    "last_receipt_date": old_parent.last_receipt_date,
                    "last_issue_date": old_parent.last_issue_date,
                    "units_sold_current_year": old_parent.units_sold_current_year,
                    "units_sold_previous_year": old_parent.units_sold_previous_year,
                    "revenue_previous_year": old_parent.revenue_previous_year,
                    "is_active": old_parent.is_active,
                    "is_discontinued": old_parent.is_discontinued,
                    "has_bom": old_parent.has_bom,
                    "is_one_sided": old_parent.is_one_sided,
                    "is_hanging": old_parent.is_hanging,
                    "category": old_parent.category,
                }

                # Print parent data in dry run mode
                if dry_run:
                    self.stdout.write(
                        f"Would create parent product: {parent_data['sku']} - {parent_data['name']}",
                    )
                    stats["created"] += 1
                    parent_mapping[old_parent.id] = None
                    continue

                # Create or update the parent product
                with transaction.atomic():
                    new_parent, created = ParentProduct.objects.update_or_create(
                        legacy_id=old_parent.legacy_id,
                        defaults=parent_data,
                    )

                    # Add to mapping
                    parent_mapping[old_parent.id] = new_parent

                    if created:
                        self.stdout.write(f"Created parent product: {new_parent.sku}")
                    else:
                        self.stdout.write(f"Updated parent product: {new_parent.sku}")

                    stats["created"] += 1

            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(
                        f"Error migrating parent product {old_parent.sku}: {e!s}",
                    ),
                )
                stats["errors"] += 1

        # Print summary
        self.stdout.write(
            self.style.SUCCESS(
                "\nParent product migration summary:\n"
                f"Total: {stats['total']}\n"
                f"Created/Updated: {stats['created']}\n"
                f"Skipped: {stats['skipped']}\n"
                f"Errors: {stats['errors']}",
            ),
        )

        return parent_mapping

    def migrate_variant_products(
        self, limit=None, *, skip_existing=False, dry_run=False
    ):
        """
        Migrate variant products from the old Product model to the new VariantProduct model.  # noqa: E501
        """
        self.stdout.write("Migrating variant products...")

        # Get variant products from the old model
        variant_products = Product.objects.filter(is_parent=False)
        if limit:
            variant_products = variant_products[:limit]

        self.stdout.write(
            f"Found {variant_products.count()} variant products to migrate",
        )

        # Track statistics
        stats = {
            "total": variant_products.count(),
            "created": 0,
            "skipped": 0,
            "errors": 0,
            "parent_not_found": 0,
        }

        # Process each variant product
        for old_variant in variant_products:
            try:
                if (
                    skip_existing
                    and VariantProduct.objects.filter(
                        legacy_id=old_variant.legacy_id,
                    ).exists()
                ):
                    self.stdout.write(
                        f"Skipping existing variant product: {old_variant.sku}",
                    )
                    stats["skipped"] += 1
                    continue

                # Find parent product
                parent = None
                if old_variant.parent_id:
                    try:
                        parent = ParentProduct.objects.get(
                            legacy_id=old_variant.parent.legacy_id,
                        )
                    except ParentProduct.DoesNotExist:
                        try:
                            parent = ParentProduct.objects.get(
                                sku=old_variant.parent.sku,
                            )
                        except ParentProduct.DoesNotExist:
                            pass

                # If parent not found, try to find by base_sku
                if not parent and old_variant.base_sku:
                    try:
                        parent = ParentProduct.objects.get(
                            base_sku=old_variant.base_sku,
                        )
                    except ParentProduct.DoesNotExist:
                        pass

                if not parent:
                    self.stdout.write(
                        self.style.WARNING(
                            f"Parent product not found for variant: {old_variant.sku}",
                        ),
                    )
                    stats["parent_not_found"] += 1
                    continue  # Skip this variant since we need a parent

                # Create variant data
                variant_data = {
                    "sku": old_variant.sku,
                    "base_sku": old_variant.base_sku,
                    "variant_code": old_variant.variant_code,
                    "legacy_id": old_variant.legacy_id,
                    "legacy_sku": old_variant.legacy_sku,
                    "parent": parent,
                    "name": old_variant.name,
                    "name_en": old_variant.name_en,
                    "short_description": old_variant.short_description,
                    "short_description_en": old_variant.short_description_en,
                    "description": old_variant.description,
                    "description_en": old_variant.description_en,
                    "keywords": old_variant.keywords,
                    "dimensions": old_variant.dimensions,
                    "weight": old_variant.weight,
                    "list_price": old_variant.list_price,
                    "wholesale_price": old_variant.wholesale_price,
                    "gross_price": old_variant.gross_price,
                    "cost_price": old_variant.cost_price,
                    "stock_quantity": old_variant.stock_quantity,
                    "min_stock_quantity": old_variant.min_stock_quantity,
                    "backorder_quantity": old_variant.backorder_quantity,
                    "open_purchase_quantity": old_variant.open_purchase_quantity,
                    "last_receipt_date": old_variant.last_receipt_date,
                    "last_issue_date": old_variant.last_issue_date,
                    "units_sold_current_year": old_variant.units_sold_current_year,
                    "units_sold_previous_year": old_variant.units_sold_previous_year,
                    "revenue_previous_year": old_variant.revenue_previous_year,
                    "is_active": old_variant.is_active,
                    "is_discontinued": old_variant.is_discontinued,
                    "has_bom": old_variant.has_bom,
                    "is_one_sided": old_variant.is_one_sided,
                    "is_hanging": old_variant.is_hanging,
                    "category": old_variant.category,
                }

                # Print variant data in dry run mode
                if dry_run:
                    self.stdout.write(
                        f"Would create variant product: {variant_data['sku']} - {variant_data['name']}",
                    )
                    stats["created"] += 1
                    continue

                # Create or update the variant product
                with transaction.atomic():
                    new_variant, created = VariantProduct.objects.update_or_create(
                        legacy_id=old_variant.legacy_id,
                        defaults=variant_data,
                    )

                    if created:
                        self.stdout.write(f"Created variant product: {new_variant.sku}")
                    else:
                        self.stdout.write(f"Updated variant product: {new_variant.sku}")

                    stats["created"] += 1

            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(
                        f"Error migrating variant product {old_variant.sku}: {e!s}",
                    ),
                )
                stats["errors"] += 1

        # Print summary
        self.stdout.write(
            self.style.SUCCESS(
                "\nVariant product migration summary:\n"
                f"Total: {stats['total']}\n"
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
