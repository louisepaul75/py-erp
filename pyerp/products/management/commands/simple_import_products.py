"""
Management command to populate the ParentProduct and VariantProduct tables with sample data.  # noqa: E501
This is a simplified version that doesn't depend on external APIs.
"""

import logging

from django.core.management.base import BaseCommand
from django.db import transaction

from pyerp.products.models import (
    ParentProduct,
    ProductCategory,
    VariantProduct,
)

# Configure logging
logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Populate ParentProduct and VariantProduct tables with sample data"

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Run without making changes to the database",
        )
        parser.add_argument(
            "--parent-count",
            type=int,
            default=10,
            help="Number of parent products to create",
        )
        parser.add_argument(
            "--variants-per-parent",
            type=int,
            default=3,
            help="Number of variants per parent",
        )

    def handle(self, *args, **options):
        dry_run = options["dry_run"]
        parent_count = options["parent_count"]
        variants_per_parent = options["variants_per_parent"]

        self.stdout.write(
            self.style.NOTICE(
                f"Starting import of {parent_count} parent products and {parent_count * variants_per_parent} variants...",
            ),
        )

        # Create a default category if needed
        category, created = ProductCategory.objects.get_or_create(
            code="DEFAULT",
            defaults={"name": "Default Category"},
        )

        # Begin transaction
        with transaction.atomic():
            parents_created = 0
            for i in range(1, parent_count + 1):
                try:
                    parent_sku = f"P{i:04d}"
                    legacy_id = f"LEGACY_KEY_{i}"
                    legacy_uid = f"UID_{i}"

                    parent = ParentProduct(
                        sku=parent_sku,
                        base_sku=parent_sku,
                        legacy_id=legacy_id,
                        legacy_uid=legacy_uid,
                        __KEY=legacy_id,
                        UID=legacy_uid,
                        FAMILIE_=f"Family {i}",
                        name=f"Parent Product {i}",
                        is_active=True,
                    )

                    if not dry_run:
                        parent.save()
                        parents_created += 1
                        self.stdout.write(f"Created parent product: {parent_sku}")

                    # Create variant products for this parent
                    for j in range(1, variants_per_parent + 1):
                        variant_sku = f"{parent_sku}-V{j}"
                        variant_code = f"VAR{j}"

                        variant = VariantProduct(
                            sku=variant_sku,
                            legacy_sku=variant_sku,
                            base_sku=parent_sku,
                            legacy_id=f"{legacy_id}_V{j}",
                            legacy_uid=f"{legacy_uid}_V{j}",
                            __KEY=f"{legacy_id}_V{j}",
                            UID=f"{legacy_uid}_V{j}",
                            FAMILIE_=f"Family {i}",
                            name=f"Variant {j} of Parent {i}",
                            is_active=True,
                            variant_code=variant_code,
                        )

                        if not dry_run:
                            variant.save()
                            self.stdout.write(f"  Created variant: {variant_sku}")

                except Exception as e:
                    self.stdout.write(
                        self.style.ERROR(f"Error creating products: {e!s}"),
                    )
                    raise

            # If it's a dry run, rollback the transaction
            if dry_run:
                self.stdout.write(
                    self.style.WARNING(
                        "DRY RUN - No changes were saved to the database",
                    ),
                )
                transaction.set_rollback(True)

        # Transaction completed
        if not dry_run:
            parent_count_db = ParentProduct.objects.count()
            variant_count_db = VariantProduct.objects.count()
            self.stdout.write(
                self.style.SUCCESS(
                    f"Final product counts - Parents: {parent_count_db}, Variants: {variant_count_db}",
                ),
            )

        self.stdout.write(self.style.SUCCESS("Import completed successfully!"))
