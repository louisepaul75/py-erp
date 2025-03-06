"""
Management command to fix missing variants by creating placeholder parent products.  # noqa: E501
"""

import logging
from typing import Any

from django.core.management.base import BaseCommand
from django.db import transaction

from pyerp.products.models import (
    ParentProduct,
    ProductCategory,
    VariantProduct,
)

# Configure logging
logger = logging.getLogger(__name__)

# Constants
SKU_PREFIX_LENGTH = 3
MAX_DISPLAY_VARIANTS = 20


class Command(BaseCommand):
    """Command to fix missing variant relationships."""

    help = "Fix missing variant relationships"

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Show what would be done without making changes",
        )
        parser.add_argument(
            "--limit",
            type=int,
            help="Maximum number of variants to process",
        )

    def handle(self, *args: Any, **options: Any) -> None:
        """Fix missing variant relationships.

        Args:
            *args: Variable length argument list
            **options: Arbitrary keyword arguments:
                - dry_run: Run without making changes
                - limit: Max variants to process

        Returns:
            None
        """
        dry_run = options["dry_run"]
        limit = options["limit"]

        # Get variants without parents
        missing_variants = VariantProduct.objects.filter(parent__isnull=True)

        if limit:
            missing_variants = missing_variants[:limit]

        if not missing_variants:
            self.stdout.write(self.style.SUCCESS("No variants without parents found."))
            return

        # Group variants by prefix
        prefix_groups = {}
        for variant in missing_variants:
            prefix = (
                variant.sku[:SKU_PREFIX_LENGTH]
                if len(variant.sku) >= SKU_PREFIX_LENGTH
                else variant.sku
            )
            if prefix not in prefix_groups:
                prefix_groups[prefix] = []
            prefix_groups[prefix].append(variant)

        # Display sample of variants
        for variant in missing_variants[:MAX_DISPLAY_VARIANTS]:
            variant_info = f"  {variant.sku}"
            if variant.base_sku:
                variant_info += f" (base_sku: {variant.base_sku})"
            self.stdout.write(variant_info)

        if len(missing_variants) > MAX_DISPLAY_VARIANTS:
            remaining = len(missing_variants) - MAX_DISPLAY_VARIANTS
            self.stdout.write(f"  ... and {remaining} more")

        # Print prefix groups
        self.stdout.write("\nGrouped by prefix:")
        for prefix, variants in prefix_groups.items():
            group_count = len(variants)
            self.stdout.write(f"  {prefix}: {group_count} variants")

        # Ask for confirmation
        if not dry_run:
            confirm = input("\nDo you want to proceed? (y/n): ")
            if confirm.lower() != "y":
                self.stdout.write("Operation cancelled.")
                return

        # Process variants
        created_parents = 0
        migrated_variants = 0

        with transaction.atomic():
            for prefix, variants in prefix_groups.items():
                try:
                    # Create parent product
                    parent_sku = f"{prefix}-P"
                    first_variant = variants[0]
                    name_prefix = "Parent Product for"
                    parent_name = f"{name_prefix} {first_variant.name}"

                    if not dry_run:
                        desc = "Automatically created parent product"
                        parent = ParentProduct.objects.create(
                            sku=parent_sku,
                            name=parent_name,
                            description=desc,
                        )
                        created_parents += 1

                        # Create variants
                        for variant in variants:
                            has_prefix = len(variant.sku) >= 3
                            variant_code = variant.sku[3:] if has_prefix else ""

                            # Create variant product
                            variant.parent = parent
                            variant.variant_code = variant_code
                            variant.save()
                            migrated_variants += 1
                except Exception as e:
                    err_msg = f"Error processing prefix {prefix}: {e}"
                    self.stdout.write(self.style.ERROR(err_msg))

        # Print summary
        summary = (
            f"\nCreated {created_parents} parents, "
            f"Migrated {migrated_variants} variants"
        )
        self.stdout.write(self.style.SUCCESS(summary))

        if dry_run:
            dry_run_msg = "This was a dry run - no changes made."
            self.stdout.write(self.style.WARNING(dry_run_msg))

    def create_placeholder_parents(self, prefix_groups, group_by_prefix):
        """Create placeholder parent products for missing variants."""
        self.stdout.write(
            self.style.NOTICE("\nCreating placeholder parent products..."),
        )

        # Get or create uncategorized category
        uncategorized, _ = ProductCategory.objects.get_or_create(
            code="UNCATEGORIZED",
            defaults={"name": "Uncategorized"},
        )

        created_parents = 0
        migrated_variants = 0

        with transaction.atomic():
            if group_by_prefix:
                for prefix, variants in prefix_groups.items():
                    parent_sku = f"{prefix}000"
                    parent_name = f"Product Group {prefix}xxx"

                    # Create parent product
                    parent, created = ParentProduct.objects.get_or_create(
                        sku=parent_sku,
                        defaults={
                            "name": parent_name,
                            "base_sku": parent_sku,
                            "category": uncategorized,
                            "is_active": True,
                            "description": f"Placeholder parent for {len(variants)} variants with prefix {prefix}xxx",
                        },
                    )

                    if created:
                        created_parents += 1
                        self.stdout.write(
                            f"  Created parent: {parent_sku} - {parent_name}",
                        )

                    # Create variants
                    for variant in variants:
                        variant_code = variant.sku[3:] if len(variant.sku) >= 3 else ""

                        # Create variant product
                        new_variant, created = VariantProduct.objects.get_or_create(
                            legacy_id=variant.legacy_id,
                            defaults={
                                "sku": variant.sku,
                                "name": variant.name,
                                "parent": parent,
                                "base_sku": parent.sku,
                                "variant_code": variant_code,
                                "legacy_sku": variant.legacy_sku or variant.sku,
                                "category": parent.category,
                                "is_active": variant.is_active,
                                "list_price": variant.list_price,
                                "wholesale_price": variant.wholesale_price,
                                "gross_price": variant.gross_price,
                                "cost_price": variant.cost_price,
                                "stock_quantity": variant.stock_quantity,
                                "description": variant.description,
                                "short_description": variant.short_description,
                            },
                        )

                        if created:
                            migrated_variants += 1
            else:
                for _prefix, variants in prefix_groups.items():
                    for variant in variants:
                        parent_sku = f"{variant.sku}-P"
                        parent_name = f"{variant.name} (Parent)"

                        # Create parent product
                        parent, created = ParentProduct.objects.get_or_create(
                            sku=parent_sku,
                            defaults={
                                "name": parent_name,
                                "base_sku": variant.sku,
                                "category": uncategorized,
                                "is_active": variant.is_active,
                                "description": f"Placeholder parent for variant {variant.sku}",
                            },
                        )

                        if created:
                            created_parents += 1
                            self.stdout.write(
                                f"  Created parent: {parent_sku} - {parent_name}",
                            )

                        # Create variant product
                        new_variant, created = VariantProduct.objects.get_or_create(
                            legacy_id=variant.legacy_id,
                            defaults={
                                "sku": variant.sku,
                                "name": variant.name,
                                "parent": parent,
                                "base_sku": parent.sku,
                                "variant_code": "V1",
                                "legacy_sku": variant.legacy_sku or variant.sku,
                                "category": parent.category,
                                "is_active": variant.is_active,
                                "list_price": variant.list_price,
                                "wholesale_price": variant.wholesale_price,
                                "gross_price": variant.gross_price,
                                "cost_price": variant.cost_price,
                                "stock_quantity": variant.stock_quantity,
                                "description": variant.description,
                                "short_description": variant.short_description,
                            },
                        )

                        if created:
                            migrated_variants += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Created {created_parents} placeholder parents and migrated {migrated_variants} variants",
            ),
        )

    def simulate_parent_creation(self, prefix_groups, group_by_prefix):
        """Simulate creating placeholder parent products for missing variants."""
        if group_by_prefix:
            for prefix, variants in prefix_groups.items():
                parent_sku = f"{prefix}000"
                parent_name = f"Product Group {prefix}xxx"
                self.stdout.write(
                    f"  Would create parent: {parent_sku} - {parent_name} for {len(variants)} variants",
                )
        else:
            variant_count = sum(len(variants) for variants in prefix_groups.values())
            self.stdout.write(
                f"  Would create {variant_count} individual parent products, one for each variant",
            )
